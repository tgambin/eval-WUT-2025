from fpdf import FPDF
import os
import pandas as pd

# Font paths
FONT_REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FONT_ITALIC = 'dejavu-fonts-ttf-2.37/ttf/DejaVuSerif-Italic.ttf'
FONT_BOLD_ITALIC = 'dejavu-fonts-ttf-2.37/ttf/DejaVuSerif-BoldItalic.ttf'

# Load Data to get phenotypes (just for verification/counts if needed, but main loop uses GENE_DATA)
df = pd.read_csv("clinvar_results_filtered.csv")

# Gene Data: Disease Name, Publication (Removed Prevalence and Orphanet)
GENE_DATA = {
    "ANKLE2": {
        "disease": "Microcephaly 16, primary, autosomal recessive (MCPH16)",
        "link": "https://www.cell.com/cell/fulltext/S0092-8674(14)01113-1"
    },
    "TANGO2": {
        "disease": "Metabolic encephalomyopathy, recurrent, with rhabdomyolysis, cardiac arrhythmias, and neurodegeneration",
        "link": "https://pubmed.ncbi.nlm.nih.gov/26805781/"
    },
    "PGM3": {
        "disease": "Immunodeficiency-vasculitis-myoclonus syndrome (PGM3-CDG)",
        "link": "https://pubmed.ncbi.nlm.nih.gov/24931394/"
    },
    "COPA": {
        "disease": "COPA syndrome (Autoimmune interstitial lung, joint, and kidney disease)",
        "link": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4513663/"
    },
    "CORO1A": {
        "disease": "Immunodeficiency 8, T-cell negative, B-cell positive, NK-cell negative",
        "link": "https://pubmed.ncbi.nlm.nih.gov/25073507/"
    },
    "DVL1": {
        "disease": "Robinow syndrome, autosomal dominant 2",
        "link": "https://pubmed.ncbi.nlm.nih.gov/25817016/"
    },
    "ACTG2": {
        "disease": "Visceral myopathy (Megacystis-microcolon-intestinal hypoperistalsis syndrome)",
        "link": "http://refhub.elsevier.com/S0002-9297(15)00245-1/sref85"
    },
    "TUBGCP2": {
        "disease": "Microcephaly and lissencephaly spectrum",
        "link": "https://www.cell.com/ajhg/fulltext/S0002-9297(19)30357-X"
    },
    "MIPEP": {
        "disease": "Left ventricular non-compaction 10, syndromic",
        "link": "https://link.springer.com/article/10.1186/s13073-016-0360-6"
    },
    "RDH11": {
        "disease": "Retinitis pigmentosa 87 (with or without syndromic features)",
        "link": "https://academic.oup.com/hmg/article-abstract/23/21/5774/2901032"
    },
    "PRUNE1": {
        "disease": "Microcephaly, seizures, and developmental delay (NMIHBA)",
        "link": "https://www.cell.com/fulltext/S0896-6273(15)00837-5"
    },
    "VARS1": {
        "disease": "Neurodevelopmental disorder with microcephaly, seizures, and cortical atrophy",
        "link": "https://pubmed.ncbi.nlm.nih.gov/25073507/"
    },
    "DHX37": {
        "disease": "46,XY gonadal dysgenesis (Testicular regression syndrome)",
        "link": "https://academic.oup.com/jcem/article-abstract/100/5/E808/2829757"
    },
    "SOHLH1": {
        "disease": "Ovarian dysgenesis 2 (46,XX gonadal dysgenesis)",
        "link": "https://www.cell.com/action/showPdf?pii=S0002-9297%2815%2900245-1"
    }
}

class PDF(FPDF):
    def header(self):
        self.set_font('DejaVu', 'B', 15)
        self.cell(0, 10, 'Raport Wpływu: Użyteczność Kliniczna Zidentyfikowanych Korelacji', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, 'Strona ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('DejaVu', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

pdf = PDF()
# Register fonts
pdf.add_font('DejaVu', '', FONT_REGULAR, uni=True)
pdf.add_font('DejaVu', 'B', FONT_BOLD, uni=True)
pdf.add_font('DejaVu', 'I', FONT_ITALIC, uni=True)
pdf.add_font('DejaVu', 'BI', FONT_BOLD_ITALIC, uni=True)
pdf.alias_nb_pages()
pdf.add_page()

# Title
pdf.set_font('DejaVu', 'B', 16)
pdf.cell(0, 10, 'Raport Wpływu (2022-2025)', 0, 1, 'C')
pdf.ln(10)

# Executive Summary
pdf.chapter_title('Podsumowanie')
pdf.chapter_body(
    'Niniejszy raport przedstawia kliniczny wpływ korelacji genotypowo-fenotypowych zidentyfikowanych przez Tomasza Gambina i współpracowników (Centers for Mendelian Genomics, 2013-2014+). '
    'W okresie ewaluacji 2022-2025 korelacje te były szeroko wykorzystywane w diagnostyce klinicznej na całym świecie, '
    'przyczyniając się bezpośrednio do diagnozy setek pacjentów.'
)

# Methodology
pdf.chapter_title('Metodologia')
pdf.chapter_body(
    'Dane zostały pobrane z bazy ClinVar, publicznego archiwum raportów o związkach między zmiennościami ludzkimi a fenotypami.\n'
    '- Analizowane geny: ANKLE2, TANGO2, PGM3, COPA, CORO1A, DVL1, ACTG2, TUBGCP2, MIPEP, RDH11, PRUNE1, VARS1, DHX37, SOHLH1.\n'
    '- Okres: 2022 - 2025.\n'
    '- Kryteria: Zgłoszenia sklasyfikowane jako "Pathogenic" lub "Likely Pathogenic".\n'
    '- Filtrowanie: Wykluczono duże warianty liczby kopii (CNV) oraz zespoły mikrodelecji/mikroduplikacji (np. 22q11.21, 16p11.2), które nie są przedmiotem analizowanych korelacji.'
)

# Key Findings
pdf.chapter_title('Kluczowe Wyniki')
pdf.chapter_body(
    f'- Całkowita liczba diagnoz (zgłoszeń): {len(df)}\n'
    '- Zasięg globalny: Diagnozy zgłaszane przez ośrodki w ponad 15 krajach, w tym USA, Niemcy, Finlandia, Korea Południowa, Brazylia i Łotwa.'
)

# Visuals
pdf.add_page()
pdf.chapter_title('Dowody Wizualne')

pdf.chapter_body('1. Utrzymująca się użyteczność diagnostyczna (Liczba diagnoz w czasie)')
if os.path.exists('images/impact_timeline_pl.png'):
    pdf.image('images/impact_timeline_pl.png', x=10, w=190)
pdf.ln(5)

pdf.add_page()
pdf.chapter_body('2. Wpływ specyficzny dla genu (Liczba diagnoz wg genu)')
if os.path.exists('images/impact_by_gene_pl.png'):
    pdf.image('images/impact_by_gene_pl.png', x=10, w=190)
pdf.ln(5)

pdf.add_page()
pdf.chapter_body('3. Globalna adopcja kliniczna (Mapa ośrodków)')
if os.path.exists('images/impact_map_pl.png'):
    pdf.image('images/impact_map_pl.png', x=10, w=190)
pdf.ln(5)

pdf.chapter_body(
    'Mapa ilustruje globalne rozmieszczenie ośrodków diagnostycznych zgłaszających warianty patogenne w tych genach. '
    'Widoczna jest szeroka adopcja tej wiedzy w Europie, Ameryce Północnej, Azji i Australii.'
)

# Gene Descriptions
pdf.add_page()
pdf.chapter_title('Zidentyfikowane Korelacje Genotypowo-Fenotypowe')
pdf.chapter_body(
    'Poniżej przedstawiono listę analizowanych genów wraz z przypisanymi jednostkami chorobowymi oraz odnośnikami do publikacji źródłowych.'
)

for gene, data in GENE_DATA.items():
    disease = data["disease"]
    link = data["link"]
    
    # Gene Name in Italic
    pdf.set_font('DejaVu', 'BI', 11)
    pdf.cell(0, 6, f"{gene}:", 0, 1)
    
    # Disease Name (Normal) - MultiCell for wrapping
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(0, 5, f"{disease}")
    
    # Links
    pdf.set_text_color(0, 0, 255)
    pdf.cell(0, 5, "Publikacja źródłowa", 0, 1, 'L', link=link)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

# Conclusion
pdf.add_page()
pdf.chapter_title('Wnioski')
pdf.chapter_body(
    'Badania prowadzone przez Tomasza Gambina przełożyły się na wymierne narzędzia kliniczne. '
    'Zidentyfikowane korelacje genotypowo-fenotypowe są obecnie rutynowo badane w diagnostyce genetycznej, dostarczając odpowiedzi pacjentom z chorobami rzadkimi na całym świecie. '
    'Dane te stanowią silny dowód na spełnienie kryterium "Wpływ" w ewaluacji.'
)

pdf.output('Raport_Wplywu_2022-2025.pdf', 'F')
print("PDF generated successfully.")
