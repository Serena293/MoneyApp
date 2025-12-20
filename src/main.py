#!/usr/bin/env python3
import json
import pandas as pd
import os
import csv



config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'categories.json')
with open(config_path) as f:
    categories_dic = json.loads(f.read())

def categorize_transaction(description, categories_dic):
    # Function to categorize a transaction based on its description
    description_lower = description.lower()
    for category, keywords in categories_dic.items():
        for keyword in keywords:
            if keyword in description_lower:  
                return category
    return "Uncategorized"

def process_bank_statements(path):
    # Function to process bank statements  
    files_list = os.listdir(path) 
    csv_files = [file for file in files_list if file.endswith('.csv')]
    for file in csv_files:
        # print(f"Processing file: {file}")
        file_df = pd.read_csv(os.path.join(path, file), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # file_df.info()
        

if __name__ == "__main__":
 bank_statements_path = os.getenv("BANK_STATEMENTS_PATH")

 if bank_statements_path:
    # print(f"Loading bank statements from: {bank_statements_path}")
    process_bank_statements(bank_statements_path)
 elif not bank_statements_path:
    raise ValueError("BANK_STATMENTS_PATH environment variable is not set.")


