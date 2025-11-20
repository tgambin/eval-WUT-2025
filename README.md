# eval-WUT-2025

This repository contains a small utility script that exports pathogenic and likely
pathogenic ClinVar submissions for a curated gene list (ANKLE2, TANGO2, PGM3,
COPA, CORO1A, DVL1, ACTG2, TUBGCP2, MIPEP, RDH11, PRUNE/PRUNE1, VARS/VARS1,
DHX37, SOHLH1).

## Usage

Run the fetcher to produce a TSV file with one row per submission/phenotype:

```bash
python scripts/fetch_clinvar.py --output results.tsv --api-key <NCBI_API_KEY>
```

Options:
- `--output`: Optional path for the TSV output (defaults to stdout).
- `--api-key`: NCBI API key to raise E-utilities rate limits.
- `--delay`: Delay (seconds) between VCV fetches, default 0.34 to stay within API guidelines.
