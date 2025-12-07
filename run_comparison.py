import sys
import os

# Add src to path to import fetch_clinvar_data
sys.path.append(os.path.join(os.getcwd(), 'src'))

from fetch_clinvar_data import compare_results

backup_file = "cache/clinvar_results_backup.csv"
current_file = "cache/clinvar_results.csv"

if os.path.exists(backup_file) and os.path.exists(current_file):
    print("Comparing backup and current results...")
    compare_results(backup_file, current_file)
else:
    print("Backup or current file not found.")
