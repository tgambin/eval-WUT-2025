import pandas as pd
import json
import os
import sys
from datetime import datetime

# Add current directory to path to allow importing from sibling modules if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_bibliography import get_bibliography, escape_latex

def generate_latex():
    # Polish date formatting
    MONTHS_PL = {
        1: "stycznia", 2: "lutego", 3: "marca", 4: "kwietnia", 5: "maja", 6: "czerwca",
        7: "lipca", 8: "sierpnia", 9: "września", 10: "października", 11: "listopada", 12: "grudnia"
    }
    now = datetime.now()
    current_date_pl = f"{now.day} {MONTHS_PL[now.month]} {now.year}"

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
    BIBLIOGRAPHY = get_bibliography(
        os.path.join(config_dir, "config_dois.json"), 
        os.path.join(cache_dir, "bibliography_cache.json")
    )

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
    
    # Helper function to generate gene table
    def create_gene_table(gene_list):
        table = "\\begin{longtable}{|p{2cm}|p{2cm}|p{11cm}|}\n"
        table += "\\hline\n"
        table += f"\\textbf{{{TEXTS['table_header_gene']}}} & \\textbf{{{TEXTS['table_header_omim']}}} & \\textbf{{{TEXTS['table_header_publications']}}} \\\\\n"
        table += "\\hline\n"
        table += "\\endhead\n"
        
        for gene in gene_list:
            if gene not in GENE_OMIM:
                continue
            omim_id = GENE_OMIM[gene]
            omim_link = f"\\href{{https://omim.org/entry/{omim_id}}}{{{omim_id}}}"
            pubs = BIBLIOGRAPHY.get(gene, [TEXTS['table_no_publications']])
            pub_text = " \\newline \\newline ".join(pubs)
            table += f"\\textit{{{gene}}} & {omim_link} & {pub_text} \\\\\n"
            table += "\\hline\n"
            
        table += "\\end{longtable}\n"
        return table
    
    # Generate LaTeX document
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
\date{""" + current_date_pl + r"""}
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

""" + TEXTS['methodology_text_2'] + r"""
\begin{itemize}
"""
    for bullet in TEXTS['methodology_bullets']:
        latex_content += f"    \\item {bullet}\n"
    latex_content += r"""\end{itemize}

""" + TEXTS['methodology_process_intro'] + r"""

\begin{enumerate}
    \item \textbf{""" + TEXTS['methodology_step1_title'] + r"""}: 
    """ + TEXTS['methodology_step1_desc'] + r"""
    \begin{itemize}
"""
    for criterion in TEXTS['methodology_step1_criteria']:
        latex_content += f"        \\item {criterion}\n"
    
    # Build gene list string
    gene_list_str = ", ".join([f"\\textit{{{g}}}" for g in TEXTS['new_genes_list'] + TEXTS['phenotype_genes_list'] + TEXTS['lung_genes_list']])
    
    latex_content += r"""    \end{itemize}
    
    """ + TEXTS['methodology_step1_genes_intro'] + " " + gene_list_str + r""".
    
    """ + TEXTS['methodology_step1_genes_rationale'] + r"""
    
    \item \textbf{""" + TEXTS['methodology_step2_title'] + r"""}: 
    """ + TEXTS['methodology_step2_desc'].replace("{current_date}", current_date_pl) + r"""
    
    \item \textbf{""" + TEXTS['methodology_step3_title'] + r"""}: 
    """ + TEXTS['methodology_step3_desc'] + r"""
    \begin{itemize}
"""
    for item in TEXTS['methodology_step3_items']:
        latex_content += f"        \\item {item}\n"
    latex_content += r"""    \end{itemize}

    \item \textbf{""" + TEXTS['methodology_step4_title'] + r"""}: 
    """ + TEXTS['methodology_step4_desc'] + r"""
    \begin{itemize}
"""
    for item in TEXTS['methodology_step4_items']:
        latex_content += f"        \\item {item}\n"
    latex_content += r"""    \end{itemize}

    \item \textbf{""" + TEXTS['methodology_step5_title'] + r"""}: 
    """ + TEXTS['methodology_step5_desc'] + r"""
    \begin{itemize}
"""
    for item in TEXTS['methodology_step5_items']:
        latex_content += f"        \\item {item}\n"
    latex_content += r"""    \end{itemize}
\end{enumerate}

\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=2cm]
\tikzstyle{startstop} = [rectangle, rounded corners, minimum width=3cm, minimum height=1cm,text centered, draw=black, fill=red!30]
\tikzstyle{process} = [rectangle, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=orange!30]
\tikzstyle{decision} = [diamond, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=green!30]
\tikzstyle{arrow} = [thick,->,>=stealth]

\node (start) [startstop] {""" + TEXTS['flowchart_start'] + " " + str(total_count) + r"""};
\node (date) [process, below of=start] {""" + TEXTS['flowchart_date_filter'] + r"""};
\node (size) [process, below of=date] {""" + TEXTS['flowchart_size_filter'] + r"""};
\node (syndrome) [process, below of=size] {""" + TEXTS['flowchart_syndrome_filter'] + r"""};
\node (final) [startstop, below of=syndrome, fill=green!30] {""" + TEXTS['flowchart_final'] + " " + str(final_count) + r"""};

\node (rej_date) [process, right of=date, xshift=4cm, fill=gray!30] {""" + TEXTS['flowchart_rejected'] + " " + str(date_rejected) + r"""};
\node (rej_size) [process, right of=size, xshift=4cm, fill=gray!30] {""" + TEXTS['flowchart_rejected'] + " " + str(size_rejected) + r"""};
\node (rej_syndrome) [process, right of=syndrome, xshift=4cm, fill=gray!30] {""" + TEXTS['flowchart_rejected'] + " " + str(syndrome_rejected) + r"""};

\draw [arrow] (start) -- (date);
\draw [arrow] (date) -- (size);
\draw [arrow] (size) -- (syndrome);
\draw [arrow] (syndrome) -- (final);

\draw [arrow] (date) -- (rej_date);
\draw [arrow] (size) -- (rej_size);
\draw [arrow] (syndrome) -- (rej_syndrome);

\end{tikzpicture}
\caption{""" + TEXTS['flowchart_caption'] + r"""}
\label{fig:flowchart}
\end{figure}

""" + TEXTS['methodology_repo_link'] + r"""

\section{""" + TEXTS['contribution_section'] + r"""}
""" + TEXTS['contribution_intro'] + r"""

\begin{itemize}
"""
    # Generate contribution items from config
    for item in TEXTS['contribution_items']:
        latex_content += f"    \\item \\textbf{{{item['title']}}}: {item['desc']}\n"
        latex_content += "    \\begin{itemize}\n"
        if 'pub_key' in item:
            pub = BIBLIOGRAPHY.get(item['pub_key'], [f"{item['pub_key']}"])[0]
            latex_content += f"        \\item {pub}\n"
        elif 'pub_keys' in item:
            for pk in item['pub_keys']:
                pub = BIBLIOGRAPHY.get(pk, [f"{pk}"])[0]
                latex_content += f"        \\item {pub}\n"
        latex_content += "    \\end{itemize}\n"
    
    latex_content += r"""\end{itemize}

\section{""" + TEXTS['genes_section'] + r"""}

\subsection{""" + TEXTS['new_genes_subsection'] + r"""}
""" + TEXTS['new_genes_desc'] + r"""

"""
    latex_content += create_gene_table(TEXTS['new_genes_list'])
    
    latex_content += r"""
\subsection{""" + TEXTS['phenotype_subsection'] + r"""}
""" + TEXTS['phenotype_desc'] + r"""

"""
    latex_content += create_gene_table(TEXTS['phenotype_genes_list'])

    latex_content += r"""
\subsection{""" + TEXTS['lung_subsection'] + r"""}
""" + TEXTS['lung_desc'] + r"""

"""
    latex_content += create_gene_table(TEXTS['lung_genes_list'])

    latex_content += r"""
\section{""" + TEXTS['stats_section'] + r"""}
""" + TEXTS['stats_intro'] + r"""

\subsection{""" + TEXTS['stats_timeline_subsection'] + r"""}
""" + TEXTS['stats_timeline_intro'] + r"""

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{cache/impact_timeline_pl.png}
    \caption{""" + TEXTS['stats_timeline_caption'] + r"""}
    \label{fig:timeline}
\end{figure}

\subsection{""" + TEXTS['stats_by_gene_subsection'] + r"""}
""" + TEXTS['stats_by_gene_intro'] + r"""

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{cache/impact_by_gene_pl.png}
    \caption{""" + TEXTS['stats_by_gene_caption'] + r"""}
    \label{fig:by_gene}
\end{figure}

\begin{longtable}{llr}
\caption{""" + TEXTS['stats_table_caption'] + r"""} \label{tab:stats} \\
\toprule
\textbf{""" + TEXTS['table_header_lp'] + r"""} & \textbf{""" + TEXTS['table_header_gene'] + r"""} & \textbf{""" + TEXTS['table_header_count'] + r"""} \\
\midrule
\endfirsthead
\caption[]{""" + TEXTS['stats_table_caption'] + r""" (cd.)} \\
\toprule
\textbf{""" + TEXTS['table_header_lp'] + r"""} & \textbf{""" + TEXTS['table_header_gene'] + r"""} & \textbf{""" + TEXTS['table_header_count'] + r"""} \\
\midrule
\endhead
\midrule
\multicolumn{3}{r}{{""" + TEXTS['table_continued'] + r"""}} \\
\midrule
\endfoot
\bottomrule
\endlastfoot
"""
    
    # Stats Table - Sorted by Count Descending
    gene_counts = df['Gene'].value_counts().reset_index()
    gene_counts.columns = ['Gene', 'Count']
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
    latex_content += f" & \\textbf{{{TEXTS['table_sum']}}} & \\textbf{{{total_variants}}} \\\\\n"
    latex_content += "\\end{longtable}\n"

    latex_content += r"""
\subsection{""" + TEXTS['centers_section'] + r"""}
""" + TEXTS['centers_desc'] + r"""

""" + TEXTS['centers_table_intro'] + r"""
"""
    
    # Fill missing submitters
    df['Submitter'] = df['Submitter'].fillna(TEXTS['table_no_data'])
    df.loc[df['Submitter'] == 'N/A', 'Submitter'] = TEXTS['table_no_data']
    
    # Map Countries
    df['Country'] = df['Submitter'].map(CENTER_MAP).fillna(TEXTS['table_unknown'])
    
    center_counts = df.groupby(['Submitter', 'Country']).size().reset_index(name='Count')
    center_counts = center_counts.sort_values('Count', ascending=False)
    
    latex_content += "\\begin{longtable}{lp{10cm}p{3cm}r}\n"
    latex_content += f"\\caption{{{TEXTS['centers_table_caption']}}} \\label{{tab:centers}} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += f"\\textbf{{{TEXTS['table_header_lp']}}} & \\textbf{{{TEXTS['table_header_submitter']}}} & \\textbf{{{TEXTS['table_header_country']}}} & \\textbf{{{TEXTS['table_header_count_short']}}} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endfirsthead\n"
    latex_content += f"\\caption[]{{{TEXTS['centers_table_caption']} (cd.)}} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += f"\\textbf{{{TEXTS['table_header_lp']}}} & \\textbf{{{TEXTS['table_header_submitter']}}} & \\textbf{{{TEXTS['table_header_country']}}} & \\textbf{{{TEXTS['table_header_count_short']}}} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endhead\n"
    latex_content += "\\midrule\n"
    latex_content += f"\\multicolumn{{4}}{{r}}{{{{{TEXTS['table_continued']}}}}} \\\\\n"
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
    latex_content += f" & \\textbf{{{TEXTS['table_sum']}}} & & \\textbf{{{center_total}}} \\\\\n"
    latex_content += "\\end{longtable}\n"

    latex_content += r"""\newpage 
\subsection{""" + TEXTS['country_stats_section'] + r"""}
""" + TEXTS['country_stats_desc'] + r"""

""" + TEXTS['country_stats_table_intro'] + r"""
"""
    country_counts = df.groupby('Country').size().reset_index(name='Count')
    country_counts = country_counts.sort_values('Count', ascending=False)
    
    latex_content += "\\begin{longtable}{llr}\n"
    latex_content += f"\\caption{{{TEXTS['country_stats_table_caption']}}} \\label{{tab:countries}} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += f"\\textbf{{{TEXTS['table_header_lp']}}} & \\textbf{{{TEXTS['table_header_country']}}} & \\textbf{{{TEXTS['table_header_count_submissions']}}} \\\\\n"
    latex_content += "\\midrule\n"
    latex_content += "\\endfirsthead\n"
    latex_content += f"\\caption[]{{{TEXTS['country_stats_table_caption']} (cd.)}} \\\\\n"
    latex_content += "\\toprule\n"
    latex_content += f"\\textbf{{{TEXTS['table_header_lp']}}} & \\textbf{{{TEXTS['table_header_country']}}} & \\textbf{{{TEXTS['table_header_count_submissions']}}} \\\\\n"
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
\vspace{2.5cm}
\noindent Opracował: Tomasz Gambin
"""
    latex_content += r"""
\end{document}
"""
    
    output_path = os.path.join(output_dir, "Raport_Wplywu_2022-2025.tex")
    with open(output_path, "w") as f:
        f.write(latex_content)
    
    print(f"LaTeX report generated: {output_path}")

if __name__ == "__main__":
    generate_latex()
