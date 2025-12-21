import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Ensure output directory exists
output_dir = "cache/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load Data
df = pd.read_csv("cache/clinvar_filtered_2022_2025_final.csv")

# Filter for 2022-2025
def parse_date(date_str):
    try:
        return pd.to_datetime(date_str)
    except:
        return pd.NaT

df['Date Created'] = df['Date Created'].apply(parse_date)
df = df.dropna(subset=['Date Created'])
df = df[df['Date Created'].dt.year.isin([2022, 2023, 2024, 2025])]

print(f"Filtered data (2022-2025): {len(df)} records")

# 1. Diagnoses over Time (Yearly) - Polish
yearly_counts = df['Date Created'].dt.year.value_counts().sort_index()
plt.figure(figsize=(10, 6))
yearly_counts.plot(kind='bar', color='#4C72B0')
plt.title('Liczba zgłoszeń wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic w latach 2022-2025')
plt.xlabel('Rok')
plt.ylabel('Liczba zgłoszeń')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('cache/impact_timeline_pl.png')
plt.close()

# 2. Diagnoses by Gene - Polish
gene_counts = df['Gene'].value_counts()
plt.figure(figsize=(12, 6))
gene_counts.plot(kind='bar', color='#55A868')
plt.title('Liczba zgłoszeń wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic wg genu (2022-2025)')
plt.xlabel('Gen')
plt.ylabel('Liczba zgłoszeń')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('cache/impact_by_gene_pl.png')
plt.close()

print("Polish visualizations generated in cache/")
