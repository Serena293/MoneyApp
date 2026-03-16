#!/usr/bin/env python3
import json
import pandas as pd
import os
import csv
from datetime import datetime
import dotenv
import sys
import matplotlib.pyplot as plt

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
    """Process all bank statement CSV files in a folder"""
    
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
    
    if combined_df is not None and len(combined_df) > 0:
        output_path = os.path.join(os.path.dirname(__file__), "processed_transactions.csv")
        combined_df.to_csv(output_path, index=False)
        print(f"\nProcessed data saved to: {output_path}")
    
    return combined_df
def plot_category_spending(df, output_path=None):
    """Create a bar chart of spending per category"""
    if df is None or len(df) == 0:
        return
    
    category_totals = df.groupby('Category')['Positive_Amount'].sum()
    category_totals = category_totals.sort_values(ascending=False)
    
    plt.figure(figsize=(10,6))
    category_totals.plot(kind='bar', color='skyblue')
    plt.title("Spending by Category")
    plt.ylabel("Amount (£)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        print(f"Category spending chart saved to: {output_path}")
    else:
        plt.show()

if __name__ == "__main__":
    dotenv.load_dotenv()

    # Use command-line argument if provided, else fall back to environment variable
    bank_statements_path = sys.argv[1] if len(sys.argv) > 1 else os.getenv("BANK_STATEMENTS_PATH")

    if not bank_statements_path:
        raise ValueError("No path provided. Use an argument or set BANK_STATEMENTS_PATH.")

    bank_statements_path = os.path.abspath(bank_statements_path)

    if not os.path.exists(bank_statements_path):
        print(f"Error: Path does not exist: {bank_statements_path}")
        sys.exit(1)

    print(f"Loading bank statements from: {bank_statements_path}")
    process_bank_statements(bank_statements_path)
    combined_df = process_bank_statements(bank_statements_path)

    # Save chart
    chart_path = os.path.join(os.path.dirname(__file__), "category_spending.png")
    plot_category_spending(combined_df, chart_path)