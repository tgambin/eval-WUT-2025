import pandas as pd
import os
from datetime import datetime

def escape_latex(text):
    """Escapes special LaTeX characters."""
    if not isinstance(text, str):
        return str(text)
    chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    return ''.join(chars.get(c, c) for c in text)

def generate_latex():
    # Load data
    df = pd.read_csv("clinvar_filtered_2022_2025_final.csv")
    
    # Gene Data with Links and Descriptions
    # Updated based on user request
    GENE_INFO = {
        "TANGO2": {
            "omim": "616878",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4746334/", "Lalani et al. (2016)"),
                ("https://pubmed.ncbi.nlm.nih.gov/28934986/", "Gambin et al. (2017)")
            ],
            "pw": True
        },
        "PSMD12": {
            "omim": "617516",
            "pubs": [
                ("https://www.cell.com/ajhg/fulltext/S0002-9297(17)30003-4", "Küry et al. (2017)"),
                ("https://pubmed.ncbi.nlm.nih.gov/28934986/", "Gambin et al. (2017)")
            ],
            "pw": True
        },
        "TRIP12": {
            "omim": "604506",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC5543723/", "Zhang et al. (2017) - TG first-coauthor"),
                ("https://pubmed.ncbi.nlm.nih.gov/28934986/", "Gambin et al. (2017)")
            ],
            "pw": True
        },
        "ANKLE2": {
            "omim": "616062",
            "pubs": [
                ("https://pubmed.ncbi.nlm.nih.gov/25259927/", "Yamamoto et al. (2014)")
            ],
            "pw": True
        },
        "TUBGCP2": {
            "omim": "617817",
            "pubs": [
                ("https://www.cell.com/ajhg/fulltext/S0002-9297(19)30357-X", "Mitani et al. (2019)")
            ],
            "pw": True
        },
        "COPA": {
            "omim": "616414",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4513663/", "Watkin et al. (2015)")
            ],
            "pw": False
        },
        "DVL1": {
            "omim": "616331",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4385180/", "White et al. (2015)")
            ],
            "pw": True
        },
        "SOHLH1": {
            "omim": "610224",
            "pubs": [
                ("https://academic.oup.com/jcem/article-abstract/100/5/E808/2829757", "Bayram et al. (2015)")
            ],
            "pw": False
        },
        "MIPEP": {
            "omim": "602241",
            "pubs": [
                ("https://link.springer.com/article/10.1186/s13073-016-0360-6", "Eldomery et al. (2016)")
            ],
            "pw": False
        },
        "PRUNE1": {
            "omim": "617413",
            "pubs": [
                ("https://www.cell.com/neuron/fulltext/S0896-6273(15)00837-5", "Karaca et al. (2015)")
            ],
            "pw": False
        },
        "VARS1": {
            "omim": "617802",
            "pubs": [
                ("https://www.cell.com/neuron/fulltext/S0896-6273(15)00837-5", "Karaca et al. (2015)")
            ],
            "pw": False
        },
        "DHX37": {
            "omim": "617362",
            "pubs": [
                ("https://www.cell.com/neuron/fulltext/S0896-6273(15)00837-5", "Karaca et al. (2015)")
            ],
            "pw": False
        },
        "RDH11": {
            "omim": "607849",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4189905/", "Xie et al. (2014)")
            ],
            "pw": False
        },
        # Phenotype Expansion
        "ACTG2": {
            "omim": "619431",
            "pubs": [
                ("https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1004258", "Wangler et al. (2014)")
            ],
            "pw": True
        },
        "PGM3": {
            "omim": "172100",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4085583/", "Stray-Pedersen et al. (2014)")
            ],
            "pw": False
        },
        "CORO1A": {
            "omim": "605000",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4386834/", "Stray-Pedersen et al. (2014)")
            ],
            "pw": False
        },
        # Lung / Non-coding
        "FOXF1": {
            "omim": "601089", 
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC8284783/", "Szafranski et al. (2021)")
            ],
            "pw": True
        },
        "TBX4": {
            "omim": "601719",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC6369446/", "Karolak et al. (2019)")
            ],
            "pw": True
        },
        "FGF10": {
            "omim": "602115",
            "pubs": [
                ("https://pmc.ncbi.nlm.nih.gov/articles/PMC6369446/", "Karolak et al. (2019)")
            ],
            "pw": True
        }
    }

    # LaTeX Header
    latex_content = r"""\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[polish]{babel}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{geometry}
\usepackage{longtable}
\usepackage{xcolor}
\usepackage{float}
\usepackage{array}

\geometry{margin=2.5cm}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=blue,
}

\title{\textbf{Raport Wpływu: Użyteczność Kliniczna Zidentyfikowanych Korelacji Genotypowo-Fenotypowych (2022-2025)}}
\author{Tomasz Gambin et al.}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
Niniejszy raport przedstawia kliniczny wpływ korelacji genotypowo-fenotypowych zidentyfikowanych przez Tomasza Gambina i współpracowników. W okresie ewaluacji 2022-2025 korelacje te były szeroko wykorzystywane w diagnostyce klinicznej na całym świecie, przyczyniając się bezpośrednio do diagnozy setek pacjentów.
\end{abstract}

\section{Metodologia}
Dane do niniejszego raportu zostały pobrane z bazy \href{https://www.ncbi.nlm.nih.gov/clinvar/}{ClinVar} (National Center for Biotechnology Information) przy użyciu narzędzi Entrez E-utilities. Proces automatycznego pobierania i filtrowania danych obejmował następujące kroki:

\begin{enumerate}
    \item \textbf{Pobieranie danych}: Dla zdefiniowanej listy genów wyszukano zgłoszenia (submissions) spełniające kryteria:
    \begin{itemize}
        \item Status kliniczny: \textit{Pathogenic} lub \textit{Likely Pathogenic}.
        \item Data zgłoszenia: 1 stycznia 2022 -- obecnie (2025).
    \end{itemize}
    \item \textbf{Filtrowanie}: Z surowych danych wykluczono:
    \begin{itemize}
        \item Duże zmiany strukturalne (CNV) o wielkości powyżej 500 kpz (500,000 par zasad), aby wyeliminować duże delecje/duplikacje obejmujące wiele genów (np. zespoły mikrodelecji), które nie są specyficznym wynikiem dla analizowanego genu (np. delecje 22q11.21 dla \textit{TANGO2}).
        \item Zgłoszenia, których opis fenotypu sugerował znane zespoły mikrodelecji (np. "22q11.2 deletion syndrome").
    \end{itemize}
    \item \textbf{Analiza}: Pozostałe zgłoszenia zostały zliczone i przypisane do odpowiednich genów oraz ośrodków zgłaszających.
\end{enumerate}

\section{Dlaczego odkrycia były możliwe - wkład PW/TG}
Odkrycia opisane w niniejszym raporcie były możliwe dzięki zastosowaniu nowatorskich metod obliczeniowych i algorytmicznych, opracowanych lub współtworzonych przez Tomasza Gambina. Kluczowe elementy to:

\begin{itemize}
    \item \textbf{Potoki do analizy wariantów i integracja danych}: Wdrożenie zintegrowanych systemów analizy danych NGS (WES/WGS) pozwalających na efektywne łączenie informacji o wariantach SNV i CNV.
    \begin{itemize}
        \item \href{https://pubmed.ncbi.nlm.nih.gov/26195989/}{Gambin et al. (2015) - Secondary findings and carrier test frequencies...}
    \end{itemize}
    \item \textbf{Reanalizy danych}: Systematyczne reanalizy "negatywnych" przypadków, które doprowadziły do nowych odkryć, np. w pracach:
    \begin{itemize}
        \item \href{https://pubmed.ncbi.nlm.nih.gov/28934986/}{Gambin et al. (2017) - Identification of novel candidate disease genes...}
        \item \href{https://pubmed.ncbi.nlm.nih.gov/25259927/}{Yamamoto et al. (2014) - ANKLE2}
    \end{itemize}
    \item \textbf{Narzędzia do detekcji CNV (HMZDelFinder)}: Autorskie narzędzie pozwalające na detekcję homo/hemi-zygotycznych CNV w danych eksomowych, co było kluczowe np. dla genu \textit{TANGO2}.
    \begin{itemize}
        \item \href{https://pubmed.ncbi.nlm.nih.gov/27980096/}{Gambin et al. (2017) - Homozygous and hemizygous CNV detection...}
    \end{itemize}
    \item \textbf{Konstrukcje mikromacierzy}: Projektowanie dedykowanych mikromacierzy (w tym z pokryciem eksonowym, np. V8), które do 2017 roku zostały użyte w badaniu ponad 46,000 przypadków (kluczowe np. dla \textit{FOXF1}).
\end{itemize}

\section{Szczegółowy opis genów i publikacji}

\subsection{Nowe Geny}
Poniższa tabela przedstawia listę nowych genów chorobowych zidentyfikowanych przy udziale Tomasza Gambina. Są to geny, dla których po raz pierwszy opisano związek z chorobą u ludzi.

"""
    
    # Helper to create table
    def create_gene_table(genes):
        table = "\\begin{longtable}{|>{\\itshape}l|l|p{7cm}|c|}\n"
        table += "\\hline\n"
        table += "\\large\\textbf{Gen} & \\large\\textbf{OMIM} & \\large\\textbf{Publikacje} & \\large\\textbf{Afiliacja PW} \\\\\n"
        table += "\\hline\n"
        table += "\\endhead\n"
        
        for gene in genes:
            if gene not in GENE_INFO: continue
            info = GENE_INFO[gene]
            
            omim_link = f"\\href{{https://omim.org/entry/{info['omim']}}}{{{info['omim']}}}"
            
            pubs = []
            for url, label in info['pubs']:
                pubs.append(f"\\href{{{url}}}{{{escape_latex(label)}}}")
            pubs_str = " \\newline ".join(pubs)
            
            affil = "Tak" if info.get('pw') else "-"
            
            table += f"{gene} & {omim_link} & {pubs_str} & {affil} \\\\\n"
            table += "\\hline\n"
            
        table += "\\end{longtable}\n"
        return table

    # New Genes
    new_genes = ["TANGO2", "PSMD12", "TRIP12", "ANKLE2", "TUBGCP2", "COPA", "DVL1", "SOHLH1", "MIPEP", "PRUNE1", "VARS1", "DHX37", "RDH11"]
    latex_content += create_gene_table(new_genes)

    # Phenotype Expansion
    latex_content += "\\subsection{Poszerzenie Fenotypu}\n"
    latex_content += "W tej sekcji przedstawiono geny, dla których badania Tomasza Gambina przyczyniły się do istotnego poszerzenia spektrum fenotypowego lub lepszego zrozumienia mechanizmu choroby.\n\n"
    exp_genes = ["ACTG2", "PGM3", "CORO1A"]
    latex_content += create_gene_table(exp_genes)

    # Lung / Non-coding
    latex_content += "\\subsection{Rozwój płuc i sekwencje niekodujące}\n"
    latex_content += "Poniższa tabela zawiera geny kluczowe dla rozwoju płuc, w przypadku których badania koncentrowały się na roli sekwencji regulatorowych i niekodujących (CNV, SNV w regionach niekodujących).\n\n"
    lung_genes = ["FOXF1", "TBX4", "FGF10"]
    latex_content += create_gene_table(lung_genes)

    # Visuals
    latex_content += r"""
\section{Dowody Wizualne}
Poniższe wykresy ilustrują skalę i zasięg oddziaływania klinicznego w latach 2022-2025.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{images/impact_timeline_pl.png}
    \caption{Liczba zgłoszeń wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic w latach 2022-2025}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{images/impact_by_gene_pl.png}
    \caption{Liczba zgłoszeń wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic wg genu}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{images/impact_map_pl.png}
    \caption{Globalny zasięg ośrodków diagnostycznych}
\end{figure}

\section{Statystyki (2022-2025)}
Tabela przedstawia liczbę wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic w bazie ClinVar w okresie 2022-2025.

"""

    # Generate Table
    # Group by Gene and count
    gene_counts = df['Gene'].value_counts().reset_index()
    gene_counts.columns = ['Gene', 'Count']
    
    latex_content += "\\begin{longtable}{lr}\n"
    latex_content += "\\toprule\n"
    latex_content += "\\large\\textbf{Gen} & \\large\\textbf{Liczba zgłoszeń P/LP (2022-2025)} \\\\\n"
    latex_content += "\\midrule\n"
    
    total_count = 0
    for _, row in gene_counts.iterrows():
        latex_content += f"\\textit{{{row['Gene']}}} & {row['Count']} \\\\\n"
        total_count += row['Count']
        
    latex_content += "\\midrule\n"
    latex_content += f"\\textbf{{SUMA}} & \\textbf{{{total_count}}} \\\\\n"
    latex_content += "\\bottomrule\n"
    latex_content += "\\end{longtable}\n"

    latex_content += r"""
\end{document}
"""

    with open("Raport_Wplywu_2022-2025.tex", "w") as f:
        f.write(latex_content)
    
    print("LaTeX report generated: Raport_Wplywu_2022-2025.tex")

if __name__ == "__main__":
    generate_latex()
