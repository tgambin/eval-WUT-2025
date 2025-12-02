#!/bin/bash
set -e

echo "Starting pipeline execution..."

# Check for uv
if command -v uv &> /dev/null; then
    echo "Using uv for dependency management..."
    if [ ! -d ".venv" ]; then
        uv venv
    fi
    source .venv/bin/activate
    uv pip install -r requirements.txt
else
    echo "uv not found, falling back to standard pip..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

echo "Dependencies installed."

# Run Python scripts
echo "Running fetch_clinvar_data.py..."
python3 src/fetch_clinvar_data.py

echo "Running filter_clinvar_data.py..."
python3 src/filter_clinvar_data.py

echo "Running generate_impact_report.py..."
python3 src/generate_impact_report.py

echo "Running generate_latex_report.py..."
python3 src/generate_latex_report.py

# Compile LaTeX
echo "Compiling PDF..."
mkdir -p output
pdflatex -output-directory output output/Raport_Wplywu_2022-2025.tex
pdflatex -output-directory output output/Raport_Wplywu_2022-2025.tex

echo "Pipeline completed successfully. Report available at output/Raport_Wplywu_2022-2025.pdf"
