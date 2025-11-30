import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import os
from datetime import datetime
from shapely.geometry import Point

# Create images directory
if not os.path.exists("images"):
    os.makedirs("images")

# Load the filtered data
df = pd.read_csv("clinvar_results_filtered.csv")

# Filter for 2022-2025
def parse_date(date_str):
    try:
        return pd.to_datetime(date_str)
    except:
        return pd.NaT

df['Submission Date'] = df['Submission Date'].apply(parse_date)
df = df.dropna(subset=['Submission Date'])
df = df[df['Submission Date'].dt.year.isin([2022, 2023, 2024, 2025])]

print(f"Filtered data (2022-2025): {len(df)} records")

# 1. Diagnoses over Time (Yearly) - Polish
yearly_counts = df['Submission Date'].dt.year.value_counts().sort_index()
plt.figure(figsize=(10, 6))
yearly_counts.plot(kind='bar', color='#4C72B0')
plt.title('Liczba zgłoszeń wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic w latach 2022-2025')
plt.xlabel('Rok')
plt.ylabel('Liczba zgłoszeń')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('images/impact_timeline_pl.png')
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
plt.savefig('images/impact_by_gene_pl.png')
plt.close()

# 3. Map - Static with Geopandas
location_map = {
    "GeneDx": {"lat": 39.1031, "lon": -77.1593, "city": "Gaithersburg, USA"},
    "Invitae": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco, USA"},
    "Laboratory for Molecular Medicine, Mass General Brigham Personalized Medicine": {"lat": 42.3601, "lon": -71.0589, "city": "Boston, USA"},
    "CeGaT Center for Human Genetics Tuebingen": {"lat": 48.5216, "lon": 9.0576, "city": "Tuebingen, Germany"},
    "Ambry Genetics": {"lat": 33.6007, "lon": -117.6719, "city": "Aliso Viejo, USA"},
    "Blueprint Genetics": {"lat": 60.1699, "lon": 24.9384, "city": "Helsinki, Finland"},
    "PreventionGenetics, part of Exact Sciences": {"lat": 44.6291, "lon": -90.1775, "city": "Marshfield, USA"},
    "Baylor Genetics": {"lat": 29.7604, "lon": -95.3698, "city": "Houston, USA"},
    "EGL Genetics": {"lat": 33.7948, "lon": -84.3237, "city": "Atlanta, USA"},
    "University of Chicago Genetic Services Laboratories": {"lat": 41.7886, "lon": -87.5987, "city": "Chicago, USA"},
    "ARUP Laboratories, Molecular Genetics and Genomics, ARUP Laboratories": {"lat": 40.7608, "lon": -111.8910, "city": "Salt Lake City, USA"},
    "Labcorp Genetics (formerly Invitae), Labcorp": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco, USA"}, 
    "Quest Diagnostics Nichols Institute San Juan Capistrano": {"lat": 33.5017, "lon": -117.6625, "city": "San Juan Capistrano, USA"},
    "OMIM": {"lat": 39.2904, "lon": -76.6122, "city": "Baltimore, USA"},
    "3billion": {"lat": 37.5665, "lon": 126.9780, "city": "Seoul, South Korea"},
    "Centogene": {"lat": 54.0833, "lon": 12.1088, "city": "Rostock, Germany"},
    "Fulgent Genetics, Fulgent Genetics": {"lat": 34.0686, "lon": -118.0276, "city": "Temple City, USA"},
    "HudsonAlpha Institute for Biotechnology, HudsonAlpha Institute for Biotechnology": {"lat": 34.7304, "lon": -86.5861, "city": "Huntsville, USA"},
    "Laboratory of Genetics, Children's Clinical University Hospital Latvia": {"lat": 56.9496, "lon": 24.1052, "city": "Riga, Latvia"},
    "Laboratorio de Genetica e Diagnostico Molecular, Hospital Israelita Albert Einstein": {"lat": -23.5505, "lon": -46.6333, "city": "Sao Paulo, Brazil"},
    "Victorian Clinical Genetics Services, Murdoch Childrens Research Institute": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Institute of Human Genetics, University of Leipzig Medical Center": {"lat": 51.3397, "lon": 12.3731, "city": "Leipzig, Germany"},
    "Center for Statistical Genetics, Columbia University": {"lat": 40.8075, "lon": -73.9626, "city": "New York, USA"},
    "Genomic Medicine Center of Excellence, King Faisal Specialist Hospital and Research Centre": {"lat": 24.7136, "lon": 46.6753, "city": "Riyadh, Saudi Arabia"},
    "Clinical Genomics Laboratory, Laboratory for Precision Diagnostics, University of Washington": {"lat": 47.6062, "lon": -122.3321, "city": "Seattle, USA"},
    "Foundation for Research in Genetics and Endocrinology, FRIGE's Institute of Human Genetics": {"lat": 23.0225, "lon": 72.5714, "city": "Ahmedabad, India"},
    "Women's Health and Genetics/Laboratory Corporation of America, LabCorp": {"lat": 36.0726, "lon": -79.7920, "city": "Burlington, USA"},
    "Institute of Medical Genetics and Applied Genomics, University of Tuebingen": {"lat": 48.5216, "lon": 9.0576, "city": "Tuebingen, Germany"},
    "Radboud University Medical Center, Nijmegen": {"lat": 51.8126, "lon": 5.8372, "city": "Nijmegen, Netherlands"},
    "Centre for Human Genetics, University Hospital Leuven": {"lat": 50.8798, "lon": 4.7005, "city": "Leuven, Belgium"},
    "BGI": {"lat": 22.5431, "lon": 114.0579, "city": "Shenzhen, China"},
    "Berry Genomics": {"lat": 39.9042, "lon": 116.4074, "city": "Beijing, China"},
    "Myriad Women's Health": {"lat": 37.6624, "lon": -122.3917, "city": "South San Francisco, USA"},
    "Counsyl": {"lat": 37.6624, "lon": -122.3917, "city": "South San Francisco, USA"},
    "Integrated Genetics/Laboratory Corporation of America, LabCorp": {"lat": 36.0726, "lon": -79.7920, "city": "Burlington, USA"},
    "Sorbonne Université, APHP, Pitié-Salpêtrière Hospital, Department of Genetics": {"lat": 48.8566, "lon": 2.3522, "city": "Paris, France"},
    "Manchester Centre for Genomic Medicine": {"lat": 53.4808, "lon": -2.2426, "city": "Manchester, UK"},
    "Wessex Regional Genetics Laboratory": {"lat": 51.0577, "lon": -1.3972, "city": "Salisbury, UK"},
    "North West Genomic Laboratory Hub": {"lat": 53.4808, "lon": -2.2426, "city": "Manchester, UK"},
    "Oxford Regional Genetics Laboratories": {"lat": 51.7520, "lon": -1.2577, "city": "Oxford, UK"},
    "West Midlands Regional Genetics Laboratory": {"lat": 52.4862, "lon": -1.8904, "city": "Birmingham, UK"},
    "Bristol Genetics Laboratory": {"lat": 51.4545, "lon": -2.5879, "city": "Bristol, UK"},
    "East Anglian Medical Genetics Service": {"lat": 52.2053, "lon": 0.1218, "city": "Cambridge, UK"},
    "Northern Genetics Service": {"lat": 54.9783, "lon": -1.6178, "city": "Newcastle, UK"},
    "Dundee Genetics Laboratory": {"lat": 56.4620, "lon": -2.9707, "city": "Dundee, UK"},
    "Edinburgh Genetics": {"lat": 55.9533, "lon": -3.1883, "city": "Edinburgh, UK"},
    "Glasgow Genetics": {"lat": 55.8642, "lon": -4.2518, "city": "Glasgow, UK"},
    "Cardiff Genetics": {"lat": 51.4816, "lon": -3.1791, "city": "Cardiff, UK"},
    "Genetics Department, Guy's Hospital": {"lat": 51.5074, "lon": -0.1278, "city": "London, UK"},
    "Great Ormond Street Hospital": {"lat": 51.5214, "lon": -0.1197, "city": "London, UK"},
    "St George's University Hospitals NHS Foundation Trust": {"lat": 51.4263, "lon": -0.1751, "city": "London, UK"},
    "Royal Devon and Exeter NHS Foundation Trust": {"lat": 50.7184, "lon": -3.5339, "city": "Exeter, UK"},
    "Sheffield Diagnostic Genetics Service": {"lat": 53.3811, "lon": -1.4701, "city": "Sheffield, UK"},
    "Leeds Genetics Laboratory": {"lat": 53.8008, "lon": -1.5491, "city": "Leeds, UK"},
    "Liverpool Women's NHS Foundation Trust": {"lat": 53.4084, "lon": -2.9916, "city": "Liverpool, UK"},
    "Nottingham Genetics": {"lat": 52.9548, "lon": -1.1581, "city": "Nottingham, UK"},
    "Leicester Genetics": {"lat": 52.6369, "lon": -1.1398, "city": "Leicester, UK"},
    "All Wales Medical Genetics Service": {"lat": 51.4816, "lon": -3.1791, "city": "Cardiff, UK"},
    "Northern Ireland Regional Genetics Centre": {"lat": 54.5973, "lon": -5.9301, "city": "Belfast, UK"},
    "National Centre for Medical Genetics, Dublin": {"lat": 53.3498, "lon": -6.2603, "city": "Dublin, Ireland"},
    "PathWest Laboratory Medicine WA": {"lat": -31.9505, "lon": 115.8605, "city": "Perth, Australia"},
    "Genetic Health Queensland": {"lat": -27.4698, "lon": 153.0251, "city": "Brisbane, Australia"},
    "SA Pathology": {"lat": -34.9285, "lon": 138.6007, "city": "Adelaide, Australia"},
    "Sydney Genome Diagnostics": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney, Australia"},
    "Canberra Clinical Genomics": {"lat": -35.2809, "lon": 149.1300, "city": "Canberra, Australia"},
    "Diagnostic Genomics, PathWest": {"lat": -31.9505, "lon": 115.8605, "city": "Perth, Australia"},
    "Molecular Genetics, Royal Prince Alfred Hospital": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney, Australia"},
    "Hunter Genetics": {"lat": -32.9283, "lon": 151.7817, "city": "Newcastle, Australia"},
    "Monash Health": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Austin Health": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Peter MacCallum Cancer Centre": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Royal Melbourne Hospital": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Alfred Health": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "St Vincent's Hospital Melbourne": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Box Hill Hospital": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Northern Health": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Western Health": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Peninsula Health": {"lat": -37.8136, "lon": 144.9631, "city": "Melbourne, Australia"},
    "Barwon Health": {"lat": -38.1499, "lon": 144.3617, "city": "Geelong, Australia"},
    "Ballarat Health Services": {"lat": -37.5622, "lon": 143.8503, "city": "Ballarat, Australia"},
    "Bendigo Health": {"lat": -36.7570, "lon": 144.2794, "city": "Bendigo, Australia"},
    "Goulburn Valley Health": {"lat": -36.3833, "lon": 145.4000, "city": "Shepparton, Australia"},
    "Albury Wodonga Health": {"lat": -36.0737, "lon": 146.9135, "city": "Albury, Australia"},
    "Latrobe Regional Hospital": {"lat": -38.2333, "lon": 146.4000, "city": "Traralgon, Australia"},
    "Central Gippsland Health": {"lat": -38.1000, "lon": 147.0667, "city": "Sale, Australia"},
    "Bairnsdale Regional Health Service": {"lat": -37.8333, "lon": 147.6167, "city": "Bairnsdale, Australia"},
    "West Gippsland Healthcare Group": {"lat": -38.1667, "lon": 145.9333, "city": "Warragul, Australia"},
    "Bass Coast Health": {"lat": -38.6000, "lon": 145.5833, "city": "Wonthaggi, Australia"},
    "South Gippsland Hospital": {"lat": -38.6500, "lon": 146.2333, "city": "Foster, Australia"},
    "Gippsland Southern Health Service": {"lat": -38.4833, "lon": 145.9333, "city": "Leongatha, Australia"},
    "Yarram and District Health Service": {"lat": -38.5667, "lon": 146.6667, "city": "Yarram, Australia"},
    "Omeo District Health": {"lat": -37.1000, "lon": 147.6000, "city": "Omeo, Australia"},
    "Orbost Regional Health": {"lat": -37.7000, "lon": 148.4500, "city": "Orbost, Australia"},
    "Robinvale District Health Services": {"lat": -34.5833, "lon": 142.7667, "city": "Robinvale, Australia"},
    "Mallee Track Health and Community Service": {"lat": -35.0667, "lon": 142.2667, "city": "Ouyen, Australia"},
    "Mildura Base Public Hospital": {"lat": -34.1833, "lon": 142.1500, "city": "Mildura, Australia"},
    "Swan Hill District Health": {"lat": -35.3333, "lon": 143.5500, "city": "Swan Hill, Australia"},
    "Kerang District Health": {"lat": -35.7333, "lon": 143.9167, "city": "Kerang, Australia"},
    "Cohuna District Hospital": {"lat": -35.8000, "lon": 144.2167, "city": "Cohuna, Australia"},
    "Echuca Regional Health": {"lat": -36.1333, "lon": 144.7500, "city": "Echuca, Australia"},
    "Kyabram District Health Service": {"lat": -36.3167, "lon": 145.0500, "city": "Kyabram, Australia"},
    "Rochester and Elmore District Health Service": {"lat": -36.3667, "lon": 144.7000, "city": "Rochester, Australia"},
    "Boort District Health": {"lat": -36.1167, "lon": 143.7167, "city": "Boort, Australia"},
    "Inglewood and Districts Health Service": {"lat": -36.5667, "lon": 143.8667, "city": "Inglewood, Australia"},
    "Maryborough District Health Service": {"lat": -37.0500, "lon": 143.7333, "city": "Maryborough, Australia"},
    "Castlemaine Health": {"lat": -37.0667, "lon": 144.2167, "city": "Castlemaine, Australia"},
    "Maldon Hospital": {"lat": -36.9833, "lon": 144.0667, "city": "Maldon, Australia"},
    "Kyneton District Health": {"lat": -37.2500, "lon": 144.4500, "city": "Kyneton, Australia"},
    "Heathcote Health": {"lat": -36.9167, "lon": 144.7000, "city": "Heathcote, Australia"},
    "Kilmore and District Hospital": {"lat": -37.3000, "lon": 144.9500, "city": "Kilmore, Australia"},
    "Seymour Health": {"lat": -37.0333, "lon": 145.1333, "city": "Seymour, Australia"},
    "Yea and District Memorial Hospital": {"lat": -37.2167, "lon": 145.4333, "city": "Yea, Australia"},
    "Alexandra District Health": {"lat": -37.1833, "lon": 145.7167, "city": "Alexandra, Australia"},
    "Mansfield District Hospital": {"lat": -37.0500, "lon": 146.0833, "city": "Mansfield, Australia"},
    "Benalla Health": {"lat": -36.5500, "lon": 145.9833, "city": "Benalla, Australia"},
    "Wangaratta District Specialist School": {"lat": -36.3500, "lon": 146.3167, "city": "Wangaratta, Australia"},
    "Northeast Health Wangaratta": {"lat": -36.3500, "lon": 146.3167, "city": "Wangaratta, Australia"},
    "Alpine Health": {"lat": -36.7167, "lon": 146.9667, "city": "Bright, Australia"},
    "Beechworth Health Service": {"lat": -36.3667, "lon": 146.6833, "city": "Beechworth, Australia"},
    "Yarrawonga Health": {"lat": -36.0167, "lon": 146.0000, "city": "Yarrawonga, Australia"},
    "Numurkah District Health Service": {"lat": -36.0833, "lon": 145.4333, "city": "Numurkah, Australia"},
    "Nathalia District Hospital": {"lat": -36.0500, "lon": 145.2000, "city": "Nathalia, Australia"},
    "Cobram District Health": {"lat": -35.9167, "lon": 145.6500, "city": "Cobram, Australia"},
}

df['Location'] = df['Submitter'].map(location_map)
df_mapped = df.dropna(subset=['Location'])

location_counts = df_mapped.groupby(['Submitter']).size().reset_index(name='Count')
location_counts['lat'] = location_counts['Submitter'].apply(lambda x: location_map[x]['lat'])
location_counts['lon'] = location_counts['Submitter'].apply(lambda x: location_map[x]['lon'])

# Create GeoDataFrame
geometry = [Point(xy) for xy in zip(location_counts['lon'], location_counts['lat'])]
gdf = gpd.GeoDataFrame(location_counts, geometry=geometry)

# Plot Map
world = gpd.read_file('ne_110m_admin_0_countries.shp')

fig, ax = plt.subplots(figsize=(15, 10))
world.plot(ax=ax, color='lightgrey', edgecolor='white')
gdf.plot(ax=ax, markersize=gdf['Count']*10, color='red', alpha=0.6, legend=True)

# Add labels for top centers
for x, y, label, count in zip(gdf.geometry.x, gdf.geometry.y, gdf['Submitter'], gdf['Count']):
    if count > 5: # Only label significant ones
        ax.text(x, y, str(count), fontsize=8, ha='right')

plt.title('Globalny zasięg: Ośrodki diagnozujące (2022-2025)', fontsize=15)
plt.axis('off')
plt.savefig('images/impact_map_pl.png', dpi=300, bbox_inches='tight')
plt.close()

print("Polish visualizations generated in images/")
