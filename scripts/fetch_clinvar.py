#!/usr/bin/env python3
"""
Fetch pathogenic and likely pathogenic ClinVar submissions for a fixed gene list.

The script searches ClinVar for each target gene (including aliases), pulls the
full ClinVar record for each matching VCV accession, and expands individual
clinical submissions into a TSV table with the following columns:

1. Gene symbol
2. Phenotype (one per row)
3. Classification (pathogenic, likely pathogenic, pathogenic/likely pathogenic)
4. Variant (HGVS expression when available)
5. Submission date
6. Submitter
7. Molecular consequence
8. Review status

Network access to the ClinVar/NCBI APIs is required at runtime. An optional
``--api-key`` argument can be used to increase rate limits for NCBI E-utilities
requests. All dependencies are from the Python standard library.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
VARIATION_URL = "https://api.ncbi.nlm.nih.gov/variation/v0/clinvar"

GENE_ALIASES: Dict[str, Sequence[str]] = {
    "ANKLE2": (),
    "TANGO2": (),
    "PGM3": (),
    "COPA": (),
    "CORO1A": (),
    "DVL1": (),
    "ACTG2": (),
    "TUBGCP2": (),
    "MIPEP": (),
    "RDH11": (),
    "PRUNE": ("PRUNE1",),
    "VARS": ("VARS1",),
    "DHX37": (),
    "SOHLH1": (),
}


@dataclass(frozen=True)
class SubmissionRow:
    gene: str
    phenotype: str
    classification: str
    variant: str
    submission_date: str
    submitter: str
    consequence: str
    review_status: str

    def as_tsv(self) -> List[str]:
        return [
            self.gene,
            self.phenotype,
            self.classification,
            self.variant,
            self.submission_date,
            self.submitter,
            self.consequence,
            self.review_status,
        ]


def build_gene_term(gene: str, aliases: Sequence[str]) -> str:
    tokens = [f"{symbol}[gene]" for symbol in (gene, *aliases)]
    return f"({ ' OR '.join(tokens) })"


def fetch_json(url: str, *, params: Optional[Dict[str, str]] = None) -> dict:
    query = f"{url}?{urllib.parse.urlencode(params)}" if params else url
    request = urllib.request.Request(query, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as resp:
        payload = resp.read().decode("utf-8")
    return json.loads(payload)


def esearch_ids(term: str, *, api_key: Optional[str]) -> List[str]:
    params = {
        "db": "clinvar",
        "retmode": "json",
        "retmax": "500",
        "term": term,
    }
    if api_key:
        params["api_key"] = api_key

    start = 0
    ids: List[str] = []
    while True:
        params["retstart"] = str(start)
        response = fetch_json(ESEARCH_URL, params=params)
        result = response.get("esearchresult", {})
        ids.extend(result.get("idlist", []))
        count = int(result.get("count", 0))
        start += int(result.get("retmax", 0))
        if start >= count:
            break
    return ids


def fetch_vcv_record(vcv_id: str, *, api_key: Optional[str]) -> Optional[dict]:
    url = f"{VARIATION_URL}/{vcv_id}"
    try:
        return fetch_json(url)
    except HTTPError as exc:
        if exc.code == 404:
            print(
                f"[warn] Variation service returned 404 for VCV {vcv_id}; skipping record",
                file=sys.stderr,
            )
            return None
        print(f"[warn] Variation service failed for VCV {vcv_id}: {exc}", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001 - log and fallback to EFetch
        print(f"[warn] Variation service failed for VCV {vcv_id}: {exc}", file=sys.stderr)

    params = {
        "db": "clinvar",
        "id": vcv_id,
        "rettype": "vcv",
        "retmode": "json",
    }
    if api_key:
        params["api_key"] = api_key

    try:
        return fetch_json(EFETCH_URL, params=params)
    except HTTPError as exc:
        if exc.code == 404:
            print(f"[warn] EFetch returned 404 for VCV {vcv_id}; skipping record", file=sys.stderr)
            return None
        print(f"[warn] EFetch failed for VCV {vcv_id}: {exc}", file=sys.stderr)
        return None
    except Exception as exc:  # noqa: BLE001 - log and skip record entirely
        print(f"[warn] EFetch failed for VCV {vcv_id}: {exc}", file=sys.stderr)
        return None


def normalize_classification(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    return cleaned


def classification_is_pathogenic(text: str) -> bool:
    lowered = text.lower()
    return "pathogenic" in lowered


def extract_gene_symbols(record: dict) -> Set[str]:
    symbols: Set[str] = set()
    for gene in record.get("genes", []):
        symbol = gene.get("symbol") or gene.get("symbol_upper")
        if symbol:
            symbols.add(symbol)

    primary = record.get("primary_snapshot_data", {})
    for gene in primary.get("genes", []):
        symbol = gene.get("locus") or gene.get("symbol")
        if symbol:
            symbols.add(symbol)

    for gene in record.get("gene", []):
        if isinstance(gene, dict):
            symbol = gene.get("symbol") or gene.get("gene_symbol")
            if symbol:
                symbols.add(symbol)
    return symbols


def pick_first_non_empty(values: Iterable[Optional[str]], default: str = "") -> str:
    for value in values:
        if value:
            return str(value)
    return default


def normalize_phenotypes(rcv_entry: dict) -> List[str]:
    phenotypes: Set[str] = set()
    for condition in rcv_entry.get("conditions", []):
        if isinstance(condition, dict):
            for key in ("preferred_name", "name"):
                if condition.get(key):
                    phenotypes.add(condition[key])
            for synonym in condition.get("synonyms", []) or []:
                phenotypes.add(synonym)
    for trait_set in rcv_entry.get("trait_set", []):
        if isinstance(trait_set, dict):
            for trait in trait_set.get("traits", []):
                name = trait.get("name")
                if name:
                    phenotypes.add(name)
    for trait in rcv_entry.get("trait", []):
        if isinstance(trait, dict):
            name = trait.get("name") or trait.get("trait_name")
            if name:
                phenotypes.add(name)
    return sorted(phenotypes) or ["Phenotype not specified"]


def extract_assertions(rcv_entry: dict) -> Iterable[Tuple[dict, str]]:
    for assertion in rcv_entry.get("clinical_assertions", []):
        classification = normalize_classification(
            pick_first_non_empty(
                (
                    assertion.get("clinical_significance", {}).get("description"),
                    assertion.get("classification"),
                    assertion.get("significance"),
                ),
                default="",
            )
        )
        if classification_is_pathogenic(classification):
            yield assertion, classification

    # Some records provide only aggregate significance at the RCV level
    rcv_classification = normalize_classification(
        pick_first_non_empty(
            (
                rcv_entry.get("clinical_significance", {}).get("description"),
                rcv_entry.get("clinical_significance", {}).get("last_evaluated"),
                rcv_entry.get("clinical_significance", {}).get("citation"),
                rcv_entry.get("clinical_significance", {}).get("comment"),
                rcv_entry.get("clinical_significance"),
            ),
            default="",
        )
    )
    if rcv_classification and classification_is_pathogenic(rcv_classification):
        synthetic = {
            "clinical_significance": {"description": rcv_classification},
            "submission_date": rcv_entry.get("date_last_updated", ""),
            "review_status": rcv_entry.get("review_status", ""),
            "submitter": rcv_entry.get("submitter", ""),
        }
        yield synthetic, rcv_classification


def extract_hgvs(assertion: dict, record: dict) -> str:
    assertion_hgvs = []
    for key in ("hgvs_c", "hgvs_p", "hgvs" ):
        value = assertion.get(key)
        if isinstance(value, list):
            assertion_hgvs.extend(str(v) for v in value if v)
        elif value:
            assertion_hgvs.append(str(value))
    for expr in assertion.get("expressions", []) or []:
        if isinstance(expr, dict) and expr.get("expression"):
            assertion_hgvs.append(expr["expression"])

    record_hgvs = []
    for expr in record.get("hgvs", []) or []:
        if isinstance(expr, dict):
            if expr.get("expression"):
                record_hgvs.append(expr["expression"])
        elif expr:
            record_hgvs.append(str(expr))

    primary = record.get("primary_snapshot_data", {})
    for ann in primary.get("allele_annotations", []):
        for expr in ann.get("hgvs", []) or []:
            if isinstance(expr, dict) and expr.get("expression"):
                record_hgvs.append(expr["expression"])

    combined = assertion_hgvs or record_hgvs
    return combined[0] if combined else record.get("accession", "")


def extract_consequence(assertion: dict, record: dict) -> str:
    for source in (assertion, record.get("variant_properties", {}), record):
        consequence = pick_first_non_empty(
            (
                source.get("molecular_consequence"),
                source.get("consequence"),
                source.get("functional_consequence"),
            ),
            default="",
        )
        if consequence:
            if isinstance(consequence, list):
                return str(consequence[0])
            return str(consequence)

    primary = record.get("primary_snapshot_data", {})
    for ann in primary.get("allele_annotations", []):
        for consequence in ann.get("functional_annotations", []):
            if isinstance(consequence, dict):
                term = pick_first_non_empty(
                    (
                        consequence.get("consequence"),
                        consequence.get("func_impact"),
                        consequence.get("hgvs_functional_annotation"),
                    ),
                    default="",
                )
                if term:
                    return term
    return ""


def extract_submission_rows(record: dict, *, gene: str, aliases: Sequence[str]) -> List[SubmissionRow]:
    if not record:
        return []

    gene_symbols = extract_gene_symbols(record)
    gene_match = {gene, *aliases}
    if gene_symbols and gene_match.isdisjoint(gene_symbols):
        return []

    rows: List[SubmissionRow] = []
    for rcv_entry in record.get("rcv", []) or []:
        phenotypes = normalize_phenotypes(rcv_entry)
        review_status_rcv = pick_first_non_empty(
            (
                rcv_entry.get("review_status"),
                rcv_entry.get("assertion_review_status"),
            ),
            default="",
        )
        for assertion, classification in extract_assertions(rcv_entry):
            variant = extract_hgvs(assertion, record)
            submission_date = pick_first_non_empty(
                (
                    assertion.get("submission_date"),
                    assertion.get("date_last_updated"),
                    assertion.get("last_updated"),
                ),
                default="",
            )
            submitter = pick_first_non_empty(
                (
                    assertion.get("submitter", {}),
                    assertion.get("submitter_name"),
                    assertion.get("submitter"),
                ),
                default="",
            )
            if isinstance(submitter, dict):
                submitter = pick_first_non_empty(
                    (
                        submitter.get("name"),
                        submitter.get("organization"),
                    ),
                    default="",
                )
            consequence = extract_consequence(assertion, record)
            review_status = pick_first_non_empty(
                (
                    assertion.get("review_status"),
                    assertion.get("assertion_review_status"),
                    review_status_rcv,
                ),
                default="",
            )
            for phenotype in phenotypes:
                rows.append(
                    SubmissionRow(
                        gene=gene,
                        phenotype=phenotype,
                        classification=classification,
                        variant=variant,
                        submission_date=submission_date,
                        submitter=str(submitter),
                        consequence=consequence,
                        review_status=review_status,
                    )
                )
    return rows


def collect_rows(*, api_key: Optional[str], delay: float) -> List[SubmissionRow]:
    rows: List[SubmissionRow] = []
    for gene, aliases in GENE_ALIASES.items():
        term = f"{build_gene_term(gene, aliases)} AND (pathogenic[clinsig] OR \"likely pathogenic\"[clinsig])"
        vcv_ids = esearch_ids(term, api_key=api_key)
        for vcv_id in vcv_ids:
            record = fetch_vcv_record(vcv_id, api_key=api_key)
            rows.extend(extract_submission_rows(record, gene=gene, aliases=aliases))
            if delay:
                time.sleep(delay)
    return rows


def write_rows(rows: Sequence[SubmissionRow], output: Optional[str]) -> None:
    header = [
        "gene",
        "phenotype",
        "classification",
        "variant",
        "submission_date",
        "submitter",
        "consequence",
        "review_status",
    ]
    destination = open(output, "w", newline="", encoding="utf-8") if output else sys.stdout
    writer = csv.writer(destination, delimiter="\t")
    writer.writerow(header)
    for row in rows:
        writer.writerow(row.as_tsv())
    if destination is not sys.stdout:
        destination.close()


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download pathogenic and likely pathogenic ClinVar submissions for the "
            "targeted genes (including PRUNE1 and VARS1 aliases)."
        )
    )
    parser.add_argument("--api-key", dest="api_key", default=None, help="NCBI API key for E-utilities requests")
    parser.add_argument(
        "--delay", type=float, default=0.34, help="Sleep interval in seconds between successive VCV fetches"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to a TSV file to write results to (defaults to stdout)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    rows = collect_rows(api_key=args.api_key, delay=args.delay)
    write_rows(rows, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
