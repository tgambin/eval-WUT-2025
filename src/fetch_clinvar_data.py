import requests
import xml.etree.ElementTree as ET
import csv
import time
import sys
from datetime import datetime

# Constants
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DB = "clinvar"
RETMAX = 100  # Batch size for efetch
SLEEP_TIME = 0.5  # Respect NCBI rate limits

# Gene list with aliases
GENES = [
    "ANKLE2", "TANGO2", "PGM3", "COPA", "CORO1A", "DVL1", 
    "ACTG2", "TUBGCP2", "MIPEP", "RDH11", 
    "PRUNE1", # Alias for PRUNE
    "VARS1",  # Alias for VARS
    "DHX37", "SOHLH1",
    "FOXF1", "TBX4", "FGF10", "PSMD12", "TRIP12"
]

def esearch(term):
    """Search for variants and return list of UIDs."""
    url = f"{BASE_URL}esearch.fcgi"
    params = {
        "db": DB,
        "term": term,
        "retmode": "json",
        "retmax": 10000,
        "usehistory": "y"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    count = int(data["esearchresult"]["count"])
    if count == 0:
        return []
        
    id_list = data["esearchresult"]["idlist"]
    return id_list

def esummary_batch(uids):
    """Fetch summary for a batch of UIDs to get VCV accessions."""
    url = f"{BASE_URL}esummary.fcgi"
    params = {
        "db": DB,
        "id": ",".join(uids),
        "retmode": "json"
    }
    response = requests.post(url, data=params)
    response.raise_for_status()
    data = response.json()
    
    vcv_accessions = []
    if "result" in data:
        for uid in data["result"]["uids"]:
            if uid in data["result"]:
                accession = data["result"][uid].get("accession")
                if accession:
                    vcv_accessions.append(accession)
    return vcv_accessions

def efetch_batch_vcv(vcv_ids):
    """Fetch VCV XML for a batch of VCV IDs."""
    url = f"{BASE_URL}efetch.fcgi"
    params = {
        "db": DB,
        "id": ",".join(vcv_ids),
        "rettype": "vcv",
        "retmode": "xml"
    }
    response = requests.post(url, data=params)
    response.raise_for_status()
    return response.content

def parse_vcv_xml(xml_content, target_gene):
    """Parse VCV XML content and yield extracted rows."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        return

    # Root is ClinVarResult-Set, children are VariationArchive
    for archive in root.findall("VariationArchive"):
        
        # Basic Variant Info from ClassifiedRecord/SimpleAllele
        classified_record = archive.find("ClassifiedRecord")
        if classified_record is None:
            continue
            
        simple_allele = classified_record.find("SimpleAllele")
        if simple_allele is None:
            continue
            
        # Variant Name
        variant_name = "N/A"
        name_node = simple_allele.find("Name")
        if name_node is not None:
            variant_name = name_node.text
            
        # Consequence (MolecularConsequence)
        molecular_consequence = "N/A"
        # Try to find in HGVS list
        hgvs_list = simple_allele.find("HGVSlist")
        if hgvs_list is not None:
            for hgvs in hgvs_list.findall("HGVS"):
                mol_cons = hgvs.find("MolecularConsequence")
                if mol_cons is not None:
                    molecular_consequence = mol_cons.get("Type")
                    break # Take the first one
        
        # Iterate over ClinicalAssertionList (Submissions)
        assertion_list = classified_record.find("ClinicalAssertionList")
        if assertion_list is None:
            continue
            
        for assertion in assertion_list.findall("ClinicalAssertion"):
            
            # Check Classification
            classification_node = assertion.find("Classification")
            if classification_node is None:
                continue
            
            # Look for GermlineClassification
            germline_class = classification_node.find("GermlineClassification")
            if germline_class is not None:
                classification_text = germline_class.text
            else:
                # Fallback to Description if GermlineClassification is missing (rare for Pathogenic)
                desc = classification_node.find("Description")
                if desc is not None:
                    classification_text = desc.text
                else:
                    classification_text = "N/A"
            
            classification_lower = classification_text.lower()
            
            # Filter for Pathogenic / Likely Pathogenic
            if not ("pathogenic" in classification_lower or "likely pathogenic" in classification_lower):
                continue
            
            # Submitter
            submitter = "N/A"
            accession_node = assertion.find("ClinVarAccession")
            if accession_node is not None:
                submitter = accession_node.get("SubmitterName", "N/A")
            
            # Submission Date
            submission_date = assertion.get("SubmissionDate", "N/A")
            
            # Review Status
            review_status = "N/A"
            review_node = classification_node.find("ReviewStatus")
            if review_node is not None:
                review_status = review_node.text
            
            # Phenotypes (Trait)
            traits = []
            trait_set = assertion.find("TraitSet")
            if trait_set is not None:
                for trait in trait_set.findall("Trait"):
                    # Get preferred name
                    name_node = trait.find(".//Name/ElementValue[@Type='Preferred']")
                    if name_node is not None:
                        traits.append(name_node.text)
                    else:
                        # Try any name
                        name_node = trait.find(".//Name/ElementValue")
                        if name_node is not None:
                            traits.append(name_node.text)
            
            if not traits:
                traits = ["Not Provided"]
            
            # Flatten: One row per phenotype
            for phenotype in traits:
                yield {
                    "Gene": target_gene,
                    "Phenotype": phenotype,
                    "Classification": classification_text,
                    "Variant (HGVS)": variant_name,
                    "Submission Date": submission_date,
                    "Submitter": submitter,
                    "Consequence": molecular_consequence,
                    "Review Status": review_status
                }

def main():
    output_file = "clinvar_results.csv"
    fieldnames = ["Gene", "Phenotype", "Classification", "Variant (HGVS)", "Submission Date", "Submitter", "Consequence", "Review Status"]
    
    print(f"Starting ClinVar extraction for genes: {', '.join(GENES)}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for gene in GENES:
            print(f"Processing {gene}...")
            
            # Search for Pathogenic/Likely Pathogenic variants
            term = f"{gene}[Gene Name] AND (pathogenic[Clinical Significance] OR likely pathogenic[Clinical Significance])"
            
            try:
                uids = esearch(term)
            except Exception as e:
                print(f"Failed to search for {gene}: {e}")
                continue
                
            print(f"  Found {len(uids)} variants (UIDs).")
            
            if not uids:
                continue

            # Process UIDs in batches to get VCVs
            # We can do esummary in batches of 100 or more (up to 500 usually safe)
            # Then efetch in batches of 100
            
            batch_size = 100
            for i in range(0, len(uids), batch_size):
                batch_uids = uids[i:i+batch_size]
                try:
                    # 1. Get VCV Accessions
                    vcv_ids = esummary_batch(batch_uids)
                    if not vcv_ids:
                        continue
                        
                    # 2. Fetch XML for VCVs
                    xml_content = efetch_batch_vcv(vcv_ids)
                    
                    # 3. Parse and Write
                    for row in parse_vcv_xml(xml_content, gene):
                        writer.writerow(row)
                        
                except Exception as e:
                    print(f"  Error processing batch {i}: {e}")
                
                time.sleep(SLEEP_TIME)
                
    print(f"Done. Results saved to {output_file}")

if __name__ == "__main__":
    main()
