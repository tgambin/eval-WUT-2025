# Raport Wpływu: Użyteczność Kliniczna Zidentyfikowanych Korelacji Genotypowo-Fenotypowych (2022-2025)

Ten projekt generuje raport PDF podsumowujący wpływ kliniczny odkryć genetycznych w latach 2022-2025, oparty na danych z bazy ClinVar.

## Struktura Projektu

- `src/`: Skrypty źródłowe Python.
    - `fetch_clinvar_data.py`: Pobiera dane z ClinVar.
    - `filter_clinvar_data.py`: Filtruje dane (daty, wielkość CNV, fenotypy).
    - `fetch_bibliography.py`: Pobiera cytowania z CrossRef API.
    - `generate_impact_report.py`: Generuje wykresy statystyczne.
    - `generate_latex_report.py`: Generuje plik .tex raportu.
- `config/`: Pliki konfiguracyjne JSON.
    - `filtering.json`: Parametry filtrowania.
    - `report_text.json`: Teksty raportu.
    - `config_dois.json`: Lista DOI publikacji.
    - `config_centers.json`: Mapowanie ośrodków na kraje.
    - `gene_omim.json`: Mapowanie genów na ID OMIM.
- `cache/`: Pliki tymczasowe i pobrane dane (CSV, JSON).
- `output/`: Wygenerowane raporty (.tex, .pdf).
- `images/`: Wygenerowane wykresy.

## Wymagania

- Python 3.x
- Biblioteki Python: `pandas`, `matplotlib`, `requests`
- LaTeX (pdflatex) z pakietami: `tikz`, `longtable`, `hyperref`, `booktabs`, `geometry`, `xcolor`, `float`, `array`, `graphicx`.

## Instrukcja Generowania Raportu

1.  **Pobranie i filtrowanie danych**:
    ```bash
    python3 src/fetch_clinvar_data.py
    python3 src/filter_clinvar_data.py
    ```

2.  **Generowanie wykresów**:
    ```bash
    python3 src/generate_impact_report.py
    ```

3.  **Generowanie raportu LaTeX**:
    ```bash
    python3 src/generate_latex_report.py
    ```

4.  **Kompilacja PDF**:
    ```bash
    cd output
    pdflatex Raport_Wplywu_2022-2025.tex
    pdflatex Raport_Wplywu_2022-2025.tex  # Uruchom dwukrotnie dla poprawnych referencji
    ```

## Autorzy

Tomasz Gambin i współpracownicy.
