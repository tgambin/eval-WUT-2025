import pandas as pd
import re

def parse_variant_size(variant_str):
    """
    Parses variant string to estimate size.
    Looks for patterns like:
    - chr22:18648855-21800471
    - c.1_1000del
    """
    # Pattern for genomic coordinates: chrX:123-456
    # Also handle NC_000022.11:g.123_456del format
    
    # 1. Standard chrX:123-456
    coord_match = re.search(r'chr[\w\d]+:(\d+)-(\d+)', variant_str)
    if coord_match:
        start = int(coord_match.group(1))
        end = int(coord_match.group(2))
        return abs(end - start)

    # 2. NC_ format: g.123_456
    nc_match = re.search(r':g\.(\d+)_(\d+)', variant_str)
    if nc_match:
        start = int(nc_match.group(1))
        end = int(nc_match.group(2))
        return abs(end - start)
    
    # Pattern for cDNA ranges: c.123_456del
    # This is rough, as cDNA pos isn't genomic size, but good proxy for "small"
    cdna_match = re.search(r'c\.(\d+)_(\d+)', variant_str)
    if cdna_match:
        start = int(cdna_match.group(1))
        end = int(cdna_match.group(2))
        return abs(end - start)
        
    return 0 # Assume small if no range found (e.g. point mutation)

def filter_data():
    df = pd.read_csv("clinvar_results.csv")
    
    rejected = []
    keep = []
    
    # Threshold for "Large CNV" vs "Intragenic CNV"
    # TANGO2 Exon 3-9 deletion is ~20-30kb. 
    # 22q11.2 deletion is ~3Mb.
    # Let's set a safe threshold, e.g., 500kb (500,000 bp).
    SIZE_THRESHOLD = 500000 
    
    for index, row in df.iterrows():
        reason = None
        
        gene = str(row['Gene'])
        variant = str(row['Variant (HGVS)'])
        phenotype = str(row['Phenotype'])
        consequence = str(row['Consequence'])
        
        size = parse_variant_size(variant)
        
        # 1. Size-based filtering
        if size > SIZE_THRESHOLD:
            reason = f"Large Genomic Event (>500kb): {size} bp"
        
        # 2. Phenotype-based filtering for known syndromes (double check)
        if not reason:
            syndrome_keywords = [
                "22q11 deletion", "22q11.2 deletion", 
                "16p11.2 deletion", "16p11.2 duplication",
                "microdeletion syndrome", "microduplication syndrome"
            ]
            for kw in syndrome_keywords:
                if kw in phenotype.lower():
                    # Check if it's NOT a specific gene mention
                    # e.g. "TANGO2-related metabolic encephalomyopathy" is fine
                    # but "22q11.2 deletion syndrome" is not.
                    reason = f"Syndrome Phenotype: {kw}"
                    break
        
        # 3. "See cases" check - often aggregates
        if not reason and "see cases" in variant.lower():
             reason = "Aggregated/Generic Variant Entry"

        if reason:
            row['Rejection Reason'] = reason
            row['Estimated Size'] = size
            rejected.append(row)
        else:
            keep.append(row)
            
    df_rejected = pd.DataFrame(rejected)
    df_keep = pd.DataFrame(keep)
    
    # Save files
    df_rejected.to_csv("rejected_variants.csv", index=False)
    df_keep.to_csv("clinvar_results_filtered.csv", index=False)
    
    print(f"Total records: {len(df)}")
    print(f"Kept records: {len(df_keep)}")
    print(f"Rejected records: {len(df_rejected)}")
    
    if not df_rejected.empty:
        print("\nSample Rejected Records:")
        print(df_rejected[['Gene', 'Phenotype', 'Variant (HGVS)', 'Rejection Reason']].head(20).to_string())

if __name__ == "__main__":
    filter_data()
