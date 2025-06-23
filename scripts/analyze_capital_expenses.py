#!/usr/bin/env python3
"""
Analyze capital vs operating expenses to understand what constitutes capital spending.
"""

import json
import pandas as pd
from collections import defaultdict

def load_raw_data():
    """Load the raw JSON data"""
    with open('PublicAccountsPDFs/2024/f4801adb-b00a-4798-9802-005231e275ee (1).json', 'r') as f:
        data = json.load(f)
    
    # Extract field names and records
    fields = [field['id'] for field in data['fields']]
    records = data['records']
    
    # Create DataFrame
    df = pd.DataFrame(records, columns=fields)
    
    # Convert Amount to numeric
    df['Amount $'] = pd.to_numeric(df['Amount $'])
    
    return df

def analyze_capital_expenses(df):
    """Analyze what constitutes capital expenses"""
    print("=== CAPITAL VS OPERATING EXPENSES ANALYSIS ===\n")
    
    # Filter for capital expenses only
    capital_df = df[df['Expenditure Category (Operating / Capital)'] == 'Capital Expense'].copy()
    
    print(f"Total Capital Expenses: ${capital_df['Amount $'].sum():,.0f}")
    print(f"Total Capital Expenses: ${capital_df['Amount $'].sum()/1e9:.2f}B\n")
    
    # Group by Standard Account (what type of expense)
    print("=== CAPITAL EXPENSES BY ACCOUNT TYPE ===")
    account_totals = capital_df.groupby('Standard Account (Expense/Asset Name)')['Amount $'].sum().sort_values(ascending=False)
    
    for account, amount in account_totals.items():
        billions = amount / 1e9
        percentage = (amount / capital_df['Amount $'].sum()) * 100
        print(f"{account}: ${billions:.2f}B ({percentage:.1f}%) - ${amount:,.0f}")
    
    # Group by Ministry for capital expenses
    print("\n=== CAPITAL EXPENSES BY MINISTRY ===")
    ministry_capital = capital_df.groupby('Ministry Name')['Amount $'].sum().sort_values(ascending=False)
    
    for ministry, amount in ministry_capital.head(10).items():
        billions = amount / 1e9
        percentage = (amount / capital_df['Amount $'].sum()) * 100
        print(f"{ministry}: ${billions:.2f}B ({percentage:.1f}%)")
    
    # Look at some specific examples
    print("\n=== EXAMPLES OF CAPITAL EXPENSES ===")
    
    # Show top 20 largest capital expense line items
    capital_sorted = capital_df.nlargest(20, 'Amount $')
    
    for idx, row in capital_sorted.iterrows():
        amount = row['Amount $']
        ministry = row['Ministry Name']
        program = row['Program Name']
        activity = row['Activity / Item']
        account = row['Standard Account (Expense/Asset Name)']
        details = row['Account Details (Expense/Asset Details)']
        
        print(f"${amount/1e6:.1f}M - {ministry}")
        print(f"  Program: {program}")
        print(f"  Activity: {activity}")
        print(f"  Account: {account}")
        if details != "No Value":
            print(f"  Details: {details}")
        print()

def compare_operating_accounts(df):
    """Compare what account types appear in operating vs capital"""
    print("\n=== ACCOUNT TYPES: OPERATING VS CAPITAL ===\n")
    
    operating_df = df[df['Expenditure Category (Operating / Capital)'] == 'Operating Expense']
    capital_df = df[df['Expenditure Category (Operating / Capital)'] == 'Capital Expense']
    
    operating_accounts = set(operating_df['Standard Account (Expense/Asset Name)'].unique())
    capital_accounts = set(capital_df['Standard Account (Expense/Asset Name)'].unique())
    
    print("Accounts that appear in BOTH operating and capital:")
    both_accounts = operating_accounts.intersection(capital_accounts)
    for account in sorted(both_accounts):
        op_total = operating_df[operating_df['Standard Account (Expense/Asset Name)'] == account]['Amount $'].sum()
        cap_total = capital_df[capital_df['Standard Account (Expense/Asset Name)'] == account]['Amount $'].sum()
        print(f"  {account}: Operating ${op_total/1e9:.2f}B, Capital ${cap_total/1e9:.2f}B")
    
    print(f"\nAccounts ONLY in operating ({len(operating_accounts - capital_accounts)}):")
    for account in sorted(operating_accounts - capital_accounts):
        total = operating_df[operating_df['Standard Account (Expense/Asset Name)'] == account]['Amount $'].sum()
        if total > 1e9:  # Only show if > $1B
            print(f"  {account}: ${total/1e9:.2f}B")
    
    print(f"\nAccounts ONLY in capital ({len(capital_accounts - operating_accounts)}):")
    for account in sorted(capital_accounts - operating_accounts):
        total = capital_df[capital_df['Standard Account (Expense/Asset Name)'] == account]['Amount $'].sum()
        print(f"  {account}: ${total/1e9:.2f}B")

def main():
    df = load_raw_data()
    analyze_capital_expenses(df)
    compare_operating_accounts(df)

if __name__ == "__main__":
    main() 