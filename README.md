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
- `cache/`: Pliki tymczasowe, pobrane dane (CSV, JSON) oraz wygenerowane wykresy.

## Wymagania

- Python 3.x
- Biblioteki Python: `pandas`, `matplotlib`, `requests`
- LaTeX (pdflatex) z pakietami: `tikz`, `longtable`, `hyperref`, `booktabs`, `geometry`, `xcolor`, `float`, `array`, `graphicx`.

## Szybki Start

### Opcja 1: Skrypt (Linux/macOS)
Wymaga zainstalowanego Pythona 3 oraz LaTeX (pdflatex). Zalecane użycie `uv` do zarządzania zależnościami.

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

### Opcja 2: Docker (Zalecane)
Gwarantuje poprawne środowisko (w tym pakiety LaTeX dla języka polskiego).

```bash
docker build -t raport-wplywu .
docker run -v $(pwd)/output:/app/output raport-wplywu
```

## Autor

Tomasz Gambin

