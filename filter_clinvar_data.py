import pandas as pd
import re

def filter_data():
    df = pd.read_csv("clinvar_results.csv")
    
    rejected = []
    keep = []
    
    for index, row in df.iterrows():
        reason = None
        
        gene = str(row['Gene'])
        variant = str(row['Variant (HGVS)'])
        phenotype = str(row['Phenotype'])
        consequence = str(row['Consequence'])
        
        # 1. Filter out explicit Copy Number Variants
        if "copy number" in variant.lower() or "copy number" in consequence.lower():
            reason = "Large CNV (Copy Number Variant)"
        
        # 2. Filter out large deletions/duplications (often indicated by coordinates or 'del' without specific nucleotide changes in a way that implies whole gene/exon)
        # Heuristic: If variant name implies a large range or chromosomal region rather than a specific mutation
        elif "del" in variant.lower() and "ins" not in variant.lower() and ("(" in variant and ")" in variant and ".." in variant):
             # e.g. NM_001111.1:c.1_1000del - might be large, but let's be careful. 
             # Better check: if phenotype mentions a microdeletion syndrome
             pass

        # 3. Filter out specific Microdeletion/Microduplication Syndromes
        if not reason:
            syndrome_keywords = [
                "22q11", "16p11", "microdeletion", "microduplication", 
                "contiguous gene syndrome", "deletion syndrome", "duplication syndrome"
            ]
            for kw in syndrome_keywords:
                if kw in phenotype.lower():
                    reason = f"Syndrome/CNV phenotype: {kw}"
                    break
        
        # 4. Filter out "See cases" if it typically points to a CNV summary
        if not reason and "see cases" in variant.lower():
             # Often these are aggregated CNV entries
             reason = "Aggregated/Generic Variant Entry (likely CNV)"

        if reason:
            row['Rejection Reason'] = reason
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
    
    # Display sample rejections for review
    if not df_rejected.empty:
        print("\nSample Rejected Records:")
        print(df_rejected[['Gene', 'Phenotype', 'Variant (HGVS)', 'Rejection Reason']].head(10).to_string())

if __name__ == "__main__":
    filter_data()
