import pandas as pd
import os
import csv

bank_statments_path = os.getenv("BANK_STATMENTS_PATH")

def process_bank_statements(path):
    # Function to process bank statements  
    files_list = os.listdir(path) 
    csv_files = [file for file in files_list if file.endswith('.csv')]
    for file in csv_files:
        print(f"Processing file: {file}")
        file_df = pd.read_csv(os.path.join(path, file), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_df.info()
        


if bank_statments_path:
    print(f"Loading bank statements from: {bank_statments_path}")
    process_bank_statements(bank_statments_path)
    
elif not bank_statments_path:
    raise ValueError("BANK_STATMENTS_PATH environment variable is not set.")


