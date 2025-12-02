import pandas as pd
import json
import os
import sys

# Add current directory to path to allow importing from sibling modules if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_bibliography import get_bibliography, escape_latex

def generate_latex():
    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, "config")
    cache_dir = os.path.join(base_dir, "cache")
    output_dir = os.path.join(base_dir, "output")
    
    # Load Configs
    with open(os.path.join(config_dir, "config_centers.json"), "r") as f:
        CENTER_MAP = json.load(f)
    with open(os.path.join(config_dir, "config_dois.json"), "r") as f:
        DOI_CONFIG = json.load(f)
    with open(os.path.join(config_dir, "gene_omim.json"), "r") as f:
        GENE_OMIM = json.load(f)
    with open(os.path.join(config_dir, "report_text.json"), "r") as f:
        TEXTS = json.load(f)
        
    # Fetch Bibliography
    print("Fetching bibliography...")
    # Pass paths to get_bibliography
    BIBLIOGRAPHY = get_bibliography(
        os.path.join(config_dir, "config_dois.json"), 
        os.path.join(cache_dir, "bibliography_cache.json")
    )

    # Load Data
    df = pd.read_csv(os.path.join(cache_dir, "clinvar_filtered_2022_2025_final.csv"))
    
    # Helper to create table
    def create_gene_table(genes):
        # Fixed column widths to prevent header misalignment
        table = "\\begin{longtable}{|p{2cm}|p{2cm}|p{11cm}|}\n"
        table += "\\hline\n"
        table += "\\textbf{Gen} & \\textbf{OMIM} & \\textbf{Publikacje} \\\\\n"
        table += "\\hline\n"
        table += "\\endhead\n"
        
        for gene in genes:
            if gene not in GENE_OMIM: continue
            omim_id = GENE_OMIM[gene]
            
            omim_link = f"\\href{{https://omim.org/entry/{omim_id}}}{{{omim_id}}}"
            
            pubs = BIBLIOGRAPHY.get(gene, [])
            pubs_str = " \\newline \\newline ".join(pubs)
            
            # Italicize gene name
            gene_italic = f"\\textit{{{gene}}}"
            
            table += f"{gene_italic} & {omim_link} & {pubs_str} \\\\\n"
            table += "\\hline\n"
            
        table += "\\end{longtable}\n"
        return table

    # Load Data
    df = pd.read_csv(os.path.join(cache_dir, "clinvar_filtered_2022_2025_final.csv"))
    df_rejected = pd.read_csv(os.path.join(cache_dir, "rejected_variants.csv"))
    
    # Calculate Stats
    final_count = len(df)
    rejected_count = len(df_rejected)
    total_count = final_count + rejected_count
    
    # Breakdown Rejections
    date_rejected = df_rejected[df_rejected['Rejection Reason'].str.contains("Date out of range", na=False)].shape[0]
    size_rejected = df_rejected[df_rejected['Rejection Reason'].str.contains("Large Genomic Event", na=False)].shape[0]
    syndrome_rejected = df_rejected[df_rejected['Rejection Reason'].str.contains("Syndrome Phenotype", na=False)].shape[0]
    
    # Verify consistency
    # Note: If there are other reasons, they might be missed here. 
    # But our filter script only assigns these 3 reasons.
    
    # Generate LaTeX
    latex_content = r"""
\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{geometry}
\usepackage{longtable}
\usepackage{xcolor}
\usepackage{float}
\usepackage{array}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows, positioning}

\geometry{margin=2.5cm}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=blue,
}

\title{""" + TEXTS['title'] + r"""}
\date{2 grudnia 2025}
\renewcommand{\contentsname}{Spis treści}
\renewcommand{\figurename}{Rycina}
\renewcommand{\tablename}{Tabela}

\begin{document}

\maketitle

""" + TEXTS['abstract'] + r"""

\tableofcontents
\newpage

\section{""" + TEXTS['methodology_section'] + r"""}
""" + TEXTS['methodology_text_1'] + r"""

Proces filtracji wariantów przedstawiono na Ryc. \ref{fig:flowchart}.

\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=2cm]
\tikzstyle{startstop} = [rectangle, rounded corners, minimum width=3cm, minimum height=1cm,text centered, draw=black, fill=red!30]
\tikzstyle{process} = [rectangle, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=orange!30]
\tikzstyle{decision} = [diamond, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=green!30]
\tikzstyle{arrow} = [thick,->,>=stealth]

\node (start) [startstop] {Pobrane z ClinVar (""" + str(total_count) + r""")};
\node (date) [process, below of=start] {Filtracja daty (2022-2025)};
\node (size) [process, below of=date] {Filtracja wielkości (>500kb)};
\node (syndrome) [process, below of=size] {Filtracja fenotypów (Syndromy)};
\node (final) [startstop, below of=syndrome, fill=green!30] {Włączone do analizy (""" + str(final_count) + r""")};

\node (rej_date) [process, right of=date, xshift=4cm, fill=gray!30] {Odrzucone: """ + str(date_rejected) + r"""};
\node (rej_size) [process, right of=size, xshift=4cm, fill=gray!30] {Odrzucone: """ + str(size_rejected) + r"""};
\node (rej_syndrome) [process, right of=syndrome, xshift=4cm, fill=gray!30] {Odrzucone: """ + str(syndrome_rejected) + r"""};

\draw [arrow] (start) -- (date);
\draw [arrow] (date) -- (size);
\draw [arrow] (size) -- (syndrome);
\draw [arrow] (syndrome) -- (final);

\draw [arrow] (date) -- (rej_date);
\draw [arrow] (size) -- (rej_size);
\draw [arrow] (syndrome) -- (rej_syndrome);

\end{tikzpicture}
\caption{Schemat procesu filtracji wariantów}
\label{fig:flowchart}
\end{figure}

""" + TEXTS['methodology_text_2'] + r"""
\begin{itemize}
"""
    for bullet in TEXTS['methodology_bullets']:
        latex_content += f"    \\item {bullet}\n"
    latex_content += r"""\end{itemize}

""" + TEXTS['methodology_process_intro'] + r"""

\begin{enumerate}
    \item \textbf{Pobieranie danych}: Przy użyciu narzędzi NCBI Entrez E-utilities, dla zdefiniowanej listy genów wyszukano zgłoszenia (submissions) spełniające kryteria:
    \begin{itemize}
        \item Status kliniczny: \textit{Pathogenic} lub \textit{Likely Pathogenic}.
        \item Data zgłoszenia: 1 stycznia 2022 -- obecnie (2025).
    \end{itemize}
    \item \textbf{Filtrowanie}: Z surowych danych wykluczono:
    \begin{itemize}
        \item Duże zmiany strukturalne (CNV) o wielkości powyżej 500 kpz (500,000 par zasad). Celem tego filtru było wyeliminowanie dużych delecji/duplikacji chromosomalnych (np. zespoły mikrodelecji), które obejmują wiele genów i nie są specyficznym wynikiem dla analizowanego genu (np. delecje 22q11.21, które obejmują gen \textit{TANGO2}, ale są osobną jednostką chorobową).
        \item Zgłoszenia, których opis fenotypu sugerował znane zespoły mikrodelecji (np. "22q11.2 deletion syndrome").
    \end{itemize}
    \item \textbf{Analiza}: Pozostałe zgłoszenia zostały zliczone i przypisane do odpowiednich genów oraz ośrodków zgłaszających. Tabela z ośrodkami została wygenerowana na podstawie pola \textit{Submitter}. Przypisanie kraju do ośrodka wykonano na podstawie mapowania nazw ośrodków.
\end{enumerate}

Kod źródłowy użyty do wygenerowania tego raportu (pobieranie danych, filtrowanie, generacja wykresów i tabel) jest dostępny w repozytorium: \href{https://github.com/tgambin/eval-WUT-2025}{https://github.com/tgambin/eval-WUT-2025}.
"""

    # Get citations for Section 2
    gambin_2015 = BIBLIOGRAPHY.get('GAMBIN_2015', ["Gambin et al. (2015)"])[0]
    gambin_2017_novel = BIBLIOGRAPHY.get('GAMBIN_2017_NOVEL', ["Gambin et al. (2017)"])[0]
    ankle2_pub = BIBLIOGRAPHY.get('ANKLE2', ["Yamamoto et al. (2014)"])[0]
    gambin_2017_cnv = BIBLIOGRAPHY.get('GAMBIN_2017_CNV', ["Gambin et al. (2017)"])[0]
    # User requested Gambin 2017 Novel for V8 array point instead of Wiszniewska
    v8_pub = gambin_2017_novel

    latex_content += r"""
\section{""" + TEXTS['contribution_section'] + r"""}
""" + TEXTS['contribution_intro'] + r"""

\begin{itemize}
    \item \textbf{Potoki do analizy wariantów i integracja danych}: Wdrożenie zintegrowanych systemów analizy danych NGS (WES/WGS) pozwalających na efektywne łączenie informacji o wariantach SNV i CNV.
    \begin{itemize}
        \item """ + gambin_2015 + r"""
    \end{itemize}
    \item \textbf{Reanalizy danych}: Systematyczne reanalizy "negatywnych" przypadków, które doprowadziły do nowych odkryć, np. w pracach:
    \begin{itemize}
        \item """ + gambin_2017_novel + r"""
        \item """ + ankle2_pub + r"""
    \end{itemize}
    \item \textbf{Narzędzia do detekcji CNV (HMZDelFinder)}: Autorskie narzędzie pozwalające na detekcję homo/hemi-zygotycznych CNV w danych eksomowych, co było kluczowe np. dla genu \textit{TANGO2}.
    \begin{itemize}
        \item """ + gambin_2017_cnv + r"""
    \end{itemize}
    \item \textbf{Konstrukcje mikromacierzy}: Projektowanie dedykowanych mikromacierzy (w tym z pokryciem eksonowym, np. V8), które do 2017 roku zostały użyte w badaniu ponad 46,000 przypadków (kluczowe np. dla \textit{FOXF1}).
    \begin{itemize}
        \item """ + v8_pub + r"""
    \end{itemize}
\end{itemize}

\section{""" + TEXTS['genes_section'] + r"""}

\subsection{""" + TEXTS['new_genes_subsection'] + r"""}
""" + TEXTS['new_genes_desc'] + r"""

\begin{longtable}{|p{2cm}|p{2cm}|p{11cm}|}
\hline
\textbf{Gen} & \textbf{OMIM} & \textbf{Publikacje} \\
\hline
\endhead
"""
    # New Genes Table
    new_genes = ["TANGO2", "PSMD12", "TRIP12", "ANKLE2", "TUBGCP2", "COPA", "DVL1", "SOHLH1", "MIPEP", "PRUNE1", "VARS1", "DHX37", "RDH11"]
    for gene, omim_id in GENE_OMIM.items():
        if gene in new_genes:
            omim_link = f"\\href{{https://omim.org/entry/{omim_id}}}{{{omim_id}}}"
            pubs = BIBLIOGRAPHY.get(gene, ["Brak publikacji"])
            pub_text = " \\newline \\newline ".join(pubs)
            latex_content += f"\\textit{{{gene}}} & {omim_link} & {pub_text} \\\\\n"
            latex_content += "\\hline\n"
            
    latex_content += r"""\end{longtable}

\subsection{""" + TEXTS['phenotype_subsection'] + r"""}
""" + TEXTS['phenotype_desc'] + r"""

\begin{longtable}{|p{2cm}|p{2cm}|p{11cm}|}
\hline
\textbf{Gen} & \textbf{OMIM} & \textbf{Publikacje} \\
\hline
\endhead
"""
    # Phenotype Genes Table
    pheno_genes = ["ACTG2", "PGM3", "CORO1A"]
    for gene, omim_id in GENE_OMIM.items():
        if gene in pheno_genes:
            omim_link = f"\\href{{https://omim.org/entry/{omim_id}}}{{{omim_id}}}"
            pubs = BIBLIOGRAPHY.get(gene, ["Brak publikacji"])
            pub_text = " \\newline \\newline ".join(pubs)
            latex_content += f"\\textit{{{gene}}} & {omim_link} & {pub_text} \\\\\n"
            latex_content += "\\hline\n"

    latex_content += r"""\end{longtable}

\subsection{""" + TEXTS['lung_subsection'] + r"""}
""" + TEXTS['lung_desc'] + r"""

\begin{longtable}{|p{2cm}|p{2cm}|p{11cm}|}
\hline
\textbf{Gen} & \textbf{OMIM} & \textbf{Publikacje} \\
\hline
\endhead
"""
    # Lung Genes Table
    lung_genes = ["FOXF1", "TBX4", "FGF10"]
    for gene, omim_id in GENE_OMIM.items():
        if gene in lung_genes:
            omim_link = f"\\href{{https://omim.org/entry/{omim_id}}}{{{omim_id}}}"
            pubs = BIBLIOGRAPHY.get(gene, ["Brak publikacji"])
            pub_text = " \\newline \\newline ".join(pubs)
            latex_content += f"\\textit{{{gene}}} & {omim_link} & {pub_text} \\\\\n"
            latex_content += "\\hline\n"

    latex_content += r"""\end{longtable}

\section{Statystyki Zgłoszeń i Wpływu Klinicznego}
Poniższa sekcja przedstawia szczegółowe statystyki dotyczące zgłoszeń wariantów w latach 2022-2025.

\subsection{Zgłoszenia w czasie}
Rycina \ref{fig:timeline} przedstawia liczbę zgłoszeń w czasie.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{cache/impact_timeline_pl.png}
    \caption{Liczba zgłoszeń wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic w latach 2022-2025}
    \label{fig:timeline}
\end{figure}

\subsection{Zgłoszenia wg genów}
Rycina \ref{fig:by_gene} oraz Tabela \ref{tab:stats} przedstawiają rozkład zgłoszeń na poszczególne geny.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{cache/impact_by_gene_pl.png}
    \caption{Liczba zgłoszeń wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic wg genu}
    \label{fig:by_gene}
\end{figure}

\begin{longtable}{llr}
\caption{Liczba wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic w bazie ClinVar (2022-2025)} \label{tab:stats} \\
\toprule
\textbf{Lp.} & \textbf{Gen} & \textbf{Liczba zgłoszeń P/LP (2022-2025)} \\
\midrule
\endfirsthead
\caption[]{Liczba wariantów sklasyfikowanych jako Pathogenic lub Likely Pathogenic w bazie ClinVar (2022-2025) (cd.)} \\
\toprule
\textbf{Lp.} & \textbf{Gen} & \textbf{Liczba zgłoszeń P/LP (2022-2025)} \\
\midrule
\endhead
\midrule
\multicolumn{3}{r}{{Ciąg dalszy na następnej stronie}} \\
\midrule
\endfoot
\bottomrule
\endlastfoot
"""
    
    # Stats Table - Sorted by Count Descending
    gene_counts = df['Gene'].value_counts().reset_index()
    gene_counts.columns = ['Gene', 'Count']
    # Filter to only include genes in our list (though df should already be filtered, good to be safe)
    gene_counts = gene_counts[gene_counts['Gene'].isin(GENE_OMIM.keys())]
    
    total_variants = 0
    idx = 1
    for _, row in gene_counts.iterrows():
        gene = row['Gene']
        count = row['Count']
        latex_content += f"{idx} & \\textit{{{gene}}} & {count} \\\\\n"
        total_variants += count
        idx += 1
        
    latex_content += "\\midrule\n"
    latex_content += f" & \\textbf{{SUMA}} & \\textbf{{{total_variants}}} \\\\\n"
    latex_content += "\\end{longtable}\n"

    latex_content += r"""
\subsection{Ośrodki zgłaszające}
""" + TEXTS['centers_desc'] + r"""

Tabela \ref{tab:centers} prezentuje listę ośrodków diagnostycznych.
"""
    
    # Fill missing submitters
    df['Submitter'] = df['Submitter'].fillna("Brak danych")
    df.loc[df['Submitter'] == 'N/A', 'Submitter'] = "Brak danych"
    
    # Map Countries
    df['Country'] = df['Submitter'].map(CENTER_MAP).fillna("Nieznany")
    
    center_counts = df.groupby(['Submitter', 'Country']).size().reset_index(name='Count')
    center_counts = center_counts.sort_values('Count', ascending=False)
    
    latex_content += "\\begin{longtable}{lp{10cm}p{3cm}r}\n"
    latex_content += "\\caption{Lista ośrodków zgłaszających warianty patogenne (2022-2025)} \\label{tab:centers} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += "\\textbf{Lp.} & \\textbf{Ośrodek (Submitter)} & \\textbf{Kraj} & \\textbf{Liczba} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endfirsthead\n"
    latex_content += "\\caption[]{Lista ośrodków zgłaszających warianty patogenne (2022-2025) (cd.)} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += "\\textbf{Lp.} & \\textbf{Ośrodek (Submitter)} & \\textbf{Kraj} & \\textbf{Liczba} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endhead\n"
    latex_content += "\\midrule\n"
    latex_content += "\\multicolumn{4}{r}{{Ciąg dalszy na następnej stronie}} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endfoot\n"
    latex_content += "\\bottomrule\n"
    latex_content += "\\endlastfoot\n"
    
    center_total = 0
    idx = 1
    for _, row in center_counts.iterrows():
        submitter = escape_latex(row['Submitter'])
        country = escape_latex(row['Country'])
        count = row['Count']
        latex_content += f"{idx} & {submitter} & {country} & {count} \\\\\n"
        center_total += count
        idx += 1
        
    latex_content += "\\midrule\n"
    latex_content += f" & \\textbf{{SUMA}} & & \\textbf{{{center_total}}} \\\\\n"
    latex_content += "\\end{longtable}\n"

    latex_content += r"""
\subsection{Statystyki krajowe}
""" + TEXTS['country_stats_desc'] + r"""

Tabela \ref{tab:countries} przedstawia statystyki wg kraju.
"""
    country_counts = df.groupby('Country').size().reset_index(name='Count')
    country_counts = country_counts.sort_values('Count', ascending=False)
    
    latex_content += "\\begin{longtable}{llr}\n"
    latex_content += "\\caption{Liczba zgłoszeń wg kraju pochodzenia ośrodka} \\label{tab:countries} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += "\\textbf{Lp.} & \\textbf{Kraj} & \\textbf{Liczba zgłoszeń} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endfirsthead\n"
    latex_content += "\\caption[]{Liczba zgłoszeń wg kraju pochodzenia ośrodka (cd.)} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += "\\textbf{Lp.} & \\textbf{Kraj} & \\textbf{Liczba zgłoszeń} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endhead\n"
    
    idx = 1
    for _, row in country_counts.iterrows():
        country = escape_latex(row['Country'])
        count = row['Count']
        latex_content += f"{idx} & {country} & {count} \\\\\n"
        idx += 1
        
    latex_content += "\\bottomrule\n"
    latex_content += "\\end{longtable}\n"

    latex_content += r"""
\end{document}
"""
    
    output_path = os.path.join(output_dir, "Raport_Wplywu_2022-2025.tex")
    with open(output_path, "w") as f:
        f.write(latex_content)
    
    print(f"LaTeX report generated: {output_path}")

if __name__ == "__main__":
    generate_latex()
