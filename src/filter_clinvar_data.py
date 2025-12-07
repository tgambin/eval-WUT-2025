import pandas as pd
import re
import json
import os
import sys

def parse_variant_size(variant_name):
    """
    Parses variant name to estimate size (for CNVs).
    Returns size in bp, or 0 if not applicable/parsable.
    """
    variant_name = str(variant_name)
    
    # 1. Handle "chrX:Start-End" format (e.g. GRCh37/hg19 12q24(chr12:123-456))
    match_chr = re.search(r'chr\w+:(\d+)-(\d+)', variant_name)
    if match_chr:
        start, end = map(int, match_chr.groups())
        return abs(end - start)

    # 2. Handle "NC_...:g.Start_End..." format
    # Look for g. followed by coordinates
    if 'g.' in variant_name:
        # Extract the coordinate part after g.
        coords_part = variant_name.split('g.')[1]
        # Find all integers in the coordinate part
        # We expect patterns like:
        # 123_456del
        # (123_456)_(789_101)del
        # (?_123)_(456_?)del
        
        # Filter out '?' and just take digits
        numbers = [int(x) for x in re.findall(r'\d+', coords_part)]
        
        if len(numbers) >= 2:
            # If 2 numbers: A_B -> Size = B - A
            if len(numbers) == 2:
                return abs(numbers[1] - numbers[0])
            
            # If 4 numbers: (A_B)_(C_D) -> Min Size = C - B
            # Assuming sorted order A < B < C < D
            if len(numbers) == 4:
                # Check if they are sorted-ish
                if numbers[1] < numbers[2]:
                    return numbers[2] - numbers[1]
                else:
                    # Fallback: Max - Min? No, that's dangerous.
                    # If B > C, it implies overlap or error.
                    # Let's return 0 to be safe (don't filter)
                    return 0
            
            # If 3 numbers: e.g. (A_B)_(C_?) -> Min Size = C - B
            # Or (?_A)_(B_C) -> Min Size = B - A
            # This is getting complex. Let's stick to the 2 and 4 cases which cover most "defined" CNVs.
            # For 3 numbers, it's ambiguous which bound is missing.
            pass

    return 0

def filter_data():
    print("Filtering data...")
    
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "filtering.json")
    cache_dir = os.path.join(base_dir, "cache")
    input_csv = os.path.join(cache_dir, "clinvar_results.csv")
    output_csv = os.path.join(cache_dir, "clinvar_filtered_2022_2025_final.csv")
    rejected_csv = os.path.join(cache_dir, "rejected_variants.csv")
    
    # Load Config
    with open(config_path, "r") as f:
        config = json.load(f)
        
    SIZE_LIMIT = config.get("size_limit", 500000)
    EXCLUDE_KEYWORDS = config.get("exclude_keywords", [])
    
    if not os.path.exists(input_csv):
        print(f"Error: Input file {input_csv} not found.")
        return

    df = pd.read_csv(input_csv)
    
    # Convert Submission Date to datetime
    df['Submission Date'] = pd.to_datetime(df['Submission Date'])
    
    filtered_rows = []
    rejected_rows = []
    
    for _, row in df.iterrows():
        # Convert row to dict to make it mutable and preserve all columns
        row_dict = row.to_dict()
        
        name = str(row_dict.get('Variant (HGVS)', ''))
        phenotype = str(row_dict.get('Phenotype', ''))
        sub_date = row_dict.get('Submission Date')
        
        reason = None
        size = parse_variant_size(name)
        
        # Add Estimated Size to the row
        row_dict['Estimated Size'] = size
        
        # 0. Filter by Date (2022-2025)
        if hasattr(sub_date, 'year') and sub_date.year not in [2022, 2023, 2024, 2025]:
            reason = f"Date out of range: {sub_date.year}"
        
        # 1. Filter by Size (CNVs > Limit)
        if not reason and size > SIZE_LIMIT:
            reason = f"Large Genomic Event (>500kb): {size} bp"
            
        # 2. Filter by Phenotype Keywords (Syndromes)
        if not reason:
            for keyword in EXCLUDE_KEYWORDS:
                if keyword in phenotype:
                    reason = f"Syndrome Phenotype: {keyword}"
                    break
            
        if reason:
            row_dict['Rejection Reason'] = reason
            rejected_rows.append(row_dict)
        else:
            filtered_rows.append(row_dict)
        
    df_filtered = pd.DataFrame(filtered_rows)
    df_rejected = pd.DataFrame(rejected_rows)
    
    # Ensure columns are in a nice order if possible, but keeping all is key
    # We just write what we have.
    
    df_filtered.to_csv(output_csv, index=False)
    df_rejected.to_csv(rejected_csv, index=False)
    
    print(f"Filtered data saved. Kept: {len(df_filtered)}, Rejected: {len(df_rejected)}")
    print(f"Output saved to: {output_csv}")

if __name__ == "__main__":
    filter_data()
