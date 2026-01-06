#!/usr/bin/env python3
import json
import pandas as pd
import os
import csv
from datetime import datetime
import dotenv

# Load categories configuration
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'categories.json')
with open(config_path) as f:
    categories_dict = json.load(f)

def categorize_transaction(description, categories_dict):
    """Categorize a transaction based on its description"""
    if pd.isna(description):
        return "Uncategorized"
    
    description_lower = str(description).lower()
    for category, keywords in categories_dict.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return "Uncategorized"

def analyze_monthly_spending(df, month):
    """Analyze and display spending for a specific month"""
    monthly_df = df[df['Month'] == month].copy()
    
    if len(monthly_df) == 0:
        return
    
    total_spent = monthly_df['Positive_Amount'].sum()
    
    print(f"\n=== {month} ===")
    print(f"Total spent: £{total_spent:.2f}")
    print("-" * 40)
    
    # Group by category
    category_totals = monthly_df.groupby('Category')['Positive_Amount'].sum()
    category_totals = category_totals.sort_values(ascending=False)
    
    for category, amount in category_totals.items():
        percentage = (amount / total_spent) * 100
        print(f"- {category}: £{amount:.2f} ({percentage:.1f}%)")
    
    # Show uncategorized transactions if any
    uncategorized = monthly_df[monthly_df['Category'] == 'Uncategorized']
    if len(uncategorized) > 0:
        print(f"\nUncategorized transactions ({len(uncategorized)}):")
        for _, row in uncategorized.head(5).iterrows():  # Show first 5
            print(f"  - {row['Description']}: £{row['Positive_Amount']:.2f}")
        if len(uncategorized) > 5:
            print(f"  ... and {len(uncategorized) - 5} more")

def process_bank_statements(path):
    """Process all bank statement CSV files in the given path"""
    
    # Get all CSV files
    files_list = os.listdir(path)
    csv_files = [file for file in files_list if file.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {path}")
        return None
    
    print(f"Found {len(csv_files)} CSV file(s)")
    
    all_transactions = []
    
    for file in csv_files:
        print(f"\nProcessing: {file}")
        
        try:
            # Read CSV file
            file_path = os.path.join(path, file)
            file_df = pd.read_csv(file_path, delimiter=',', quotechar='"', 
                                  quoting=csv.QUOTE_MINIMAL, low_memory=False)
            
            # Convert Amount to numeric
            file_df['Amount'] = pd.to_numeric(file_df['Amount'], errors='coerce')
            
            # Filter only outgoing transactions (negative amounts)
            outgoing_df = file_df[file_df['Amount'] < 0].copy()
            
            if len(outgoing_df) == 0:
                print(f"  No outgoing transactions found in {file}")
                continue
            
            # Create positive amount column
            outgoing_df['Positive_Amount'] = outgoing_df['Amount'].abs()
            
            # Apply categorization
            outgoing_df['Category'] = outgoing_df['Description'].apply(
                lambda desc: categorize_transaction(desc, categories_dict)
            )
            
            # Parse date and extract month
            # Try Completed Date first, fall back to Started Date
            date_column = 'Completed Date' if 'Completed Date' in outgoing_df.columns else 'Started Date'
            outgoing_df['Date'] = pd.to_datetime(outgoing_df[date_column], errors='coerce')
            
            # Drop rows with invalid dates
            outgoing_df = outgoing_df.dropna(subset=['Date'])
            
            # Create month column (YYYY-MM format)
            outgoing_df['Month'] = outgoing_df['Date'].dt.strftime('%Y-%m')
            
            # Add filename for reference
            outgoing_df['Source_File'] = file
            
            # Select relevant columns
            relevant_columns = ['Date', 'Month', 'Description', 'Category', 
                              'Positive_Amount', 'Currency', 'Type', 'Source_File']
            available_columns = [col for col in relevant_columns if col in outgoing_df.columns]
            
            file_transactions = outgoing_df[available_columns]
            all_transactions.append(file_transactions)
            
            print(f"  Outgoing transactions: {len(outgoing_df)}")
            print(f"  Total outgoing: £{outgoing_df['Positive_Amount'].sum():.2f}")
            
        except Exception as e:
            print(f"  Error processing {file}: {e}")
            continue
    
    if not all_transactions:
        print("\nNo outgoing transactions found in any file.")
        return None
    
    # Combine all transactions
    combined_df = pd.concat(all_transactions, ignore_index=True)
    
    # Sort by date
    combined_df = combined_df.sort_values('Date')
    
    print(f"\n{'='*50}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*50}")
    print(f"Total files processed: {len(csv_files)}")
    print(f"Total outgoing transactions: {len(combined_df)}")
    print(f"Total amount spent: £{combined_df['Positive_Amount'].sum():.2f}")
    
    # Analyze by month
    months = sorted(combined_df['Month'].unique())
    print(f"\nMonths analyzed: {', '.join(months)}")
    
    # Show monthly breakdown
    for month in months:
        analyze_monthly_spending(combined_df, month)
    
    # Summary across all months
    print(f"\n{'='*50}")
    print("OVERALL CATEGORY BREAKDOWN")
    print(f"{'='*50}")
    
    overall_totals = combined_df.groupby('Category')['Positive_Amount'].sum()
    overall_totals = overall_totals.sort_values(ascending=False)
    grand_total = combined_df['Positive_Amount'].sum()
    
    for category, amount in overall_totals.items():
        percentage = (amount / grand_total) * 100
        print(f"- {category}: £{amount:.2f} ({percentage:.1f}%)")
    
    return combined_df

if __name__ == "__main__":
    dotenv.load_dotenv()
    bank_statements_path = os.getenv("BANK_STATEMENTS_PATH")
    if bank_statements_path:
        if not os.path.exists(bank_statements_path):
            print(f"Error: Path does not exist: {bank_statements_path}")
        else:
            print(f"Loading bank statements from: {bank_statements_path}")
            result_df = process_bank_statements(bank_statements_path)
            
            #  Save processed data to CSV
            # if result_df is not None:
            #     output_path = os.path.join(os.path.dirname(__file__), "processed_transactions.csv")
            #     result_df.to_csv(output_path, index=False)
            #     print(f"\nProcessed data saved to: {output_path}")
    else:
        raise ValueError("BANK_STATEMENTS_PATH environment variable is not set.")