#!/usr/bin/env python3
"""
Debug the Sankey generation process to find where data is being moved or miscounted.
"""

import pandas as pd
import json
from collections import defaultdict

def load_processed_data():
    """Load our processed data"""
    return pd.read_csv('clean_expenses_2024.csv')

def debug_ministry_processing(df, ministry_name):
    """Debug how a specific ministry is processed in our Sankey generation"""
    
    print(f"\n{'='*60}")
    print(f"🐛 DEBUGGING {ministry_name.upper()} SANKEY GENERATION")
    print(f"{'='*60}")
    
    ministry_data = df[df['Ministry Name'] == ministry_name].copy()
    
    print(f"📊 RAW MINISTRY DATA:")
    print(f"   Total amount: ${ministry_data['amount_dollars'].sum():,.0f}")
    print(f"   Number of records: {len(ministry_data)}")
    
    # Simulate the exact processing logic from create_compact_sankey.py
    
    # Group by program within ministry
    program_totals = {}
    ministry_total_calculated = 0
    
    for program_name, program_group in ministry_data.groupby('Program Name'):
        print(f"\n   Program: {program_name}")
        program_amount = program_group['amount_dollars'].sum()
        print(f"      Amount: ${program_amount:,.0f}")
        
        # Separate operational vs substantive spending (from our script logic)
        operational_total = 0
        substantive_categories = {}
        
        for _, row in program_group.iterrows():
            account_name = row['Standard Account (Expense/Asset Name)']
            account_details = row['Account Details (Expense/Asset Details)']
            amount = float(row['amount_dollars']) / 1e9  # Convert to billions like in script
            
            # Apply the same consolidation logic from should_consolidate_category
            if should_consolidate_category(account_name, account_details):
                operational_total += amount
            else:
                # This is substantive program spending
                if 'transfer payments' in account_name.lower() and pd.notna(account_details) and account_details != '':
                    category_name = account_details
                elif pd.notna(account_details) and account_details != '':
                    category_name = f"{account_name}: {account_details}"
                else:
                    category_name = account_name
                
                # Aggregate amounts for same categories
                if category_name in substantive_categories:
                    substantive_categories[category_name] += amount
                else:
                    substantive_categories[category_name] = amount
        
        # Calculate what would be included in Sankey
        program_sankey_total = 0
        
        # Operations
        if operational_total > 0:
            program_sankey_total += operational_total
            print(f"         Operations: ${operational_total * 1e9:,.0f}")
        
        # Major substantive categories (>$1M)
        major_total = 0
        minor_total = 0
        
        for category_name, amount in substantive_categories.items():
            if amount > 0.001:  # $1M threshold
                program_sankey_total += amount
                major_total += amount
                print(f"         {category_name}: ${amount * 1e9:,.0f}")
            else:
                minor_total += amount
        
        # Other category
        if minor_total > 0:
            program_sankey_total += minor_total
            print(f"         Other: ${minor_total * 1e9:,.0f}")
        
        program_totals[program_name] = {
            'raw_total': program_amount,
            'sankey_total': program_sankey_total * 1e9,
            'operational': operational_total * 1e9,
            'substantive_major': major_total * 1e9,
            'substantive_minor': minor_total * 1e9
        }
        
        ministry_total_calculated += program_sankey_total * 1e9
        
        print(f"      Sankey will include: ${program_sankey_total * 1e9:,.0f}")
        difference = program_amount - (program_sankey_total * 1e9)
        if abs(difference) > 1000:  # More than $1K difference
            print(f"      ⚠️  DIFFERENCE: ${difference:,.0f}")
    
    print(f"\n📊 MINISTRY SUMMARY:")
    print(f"   Raw total:        ${ministry_data['amount_dollars'].sum():,.0f}")
    print(f"   Calculated Sankey: ${ministry_total_calculated:,.0f}")
    print(f"   Difference:       ${ministry_data['amount_dollars'].sum() - ministry_total_calculated:,.0f}")
    
    return program_totals

def should_consolidate_category(account_name: str, account_details: str) -> bool:
    """Same logic as in our compact sankey script"""
    OPERATIONAL_CATEGORIES = {
        'Salaries and wages',
        'Employee benefits', 
        'Transportation and communication',
        'Services',
        'Supplies and equipment',
        'Recoveries',
        'Other transactions',
        'Amortization',
        'Bad Debt Expense'
    }
    
    # Check if it's in our operational categories
    for op_cat in OPERATIONAL_CATEGORIES:
        if op_cat.lower() in account_name.lower():
            return True
    
    # Keep substantive program spending separate
    if 'transfer payments' in account_name.lower():
        return False
        
    if account_name.lower() in ['capital expense', 'capital']:
        return False
        
    # Check account details for specific programs/grants
    if pd.notna(account_details) and account_details != '':
        details_lower = account_details.lower()
        if any(keyword in details_lower for keyword in [
            'program', 'grant', 'fund', 'transfer', 'payment', 
            'subsidy', 'benefit', 'insurance', 'pension'
        ]):
            return False
    
    return True

def check_data_aggregation_issues(df):
    """Check if there are any data aggregation issues causing double counting"""
    
    print(f"\n{'='*60}")
    print(f"🔍 CHECKING FOR DATA AGGREGATION ISSUES")
    print(f"{'='*60}")
    
    # Look for duplicate records
    duplicates = df.duplicated().sum()
    print(f"Exact duplicate records: {duplicates}")
    
    # Look for near-duplicates (same ministry, program, account, details, similar amounts)
    print(f"\nChecking for potential duplicate categories...")
    
    # Group by ministry, program, account, details and look for multiple entries
    grouped = df.groupby(['Ministry Name', 'Program Name', 'Standard Account (Expense/Asset Name)', 'Account Details (Expense/Asset Details)']).agg({
        'amount_dollars': ['count', 'sum']
    }).reset_index()
    
    # Flatten column names
    grouped.columns = ['Ministry Name', 'Program Name', 'Standard Account', 'Account Details', 'Count', 'Total Amount']
    
    # Look for cases where count > 1 (multiple records for same category)
    multiple_records = grouped[grouped['Count'] > 1]
    
    if len(multiple_records) > 0:
        print(f"Found {len(multiple_records)} categories with multiple records:")
        for _, row in multiple_records.head(10).iterrows():
            print(f"   {row['Ministry Name']} - {row['Standard Account']} - {row['Account Details']}")
            print(f"      Count: {row['Count']}, Total: ${row['Total Amount']:,.0f}")
    else:
        print("No duplicate categories found.")

def compare_with_actual_sankey():
    """Compare our calculated values with actual Sankey data"""
    
    print(f"\n{'='*60}")
    print(f"🔍 COMPARING WITH ACTUAL SANKEY DATA")
    print(f"{'='*60}")
    
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        sankey_data = json.load(f)
    
    print(f"Sankey file totals:")
    print(f"   Spending (summary): ${sankey_data['spending'] * 1e9:,.0f}")
    print(f"   Revenue (summary): ${sankey_data['revenue'] * 1e9:,.0f}")
    
    # Check if our calculation matches the file
    df = load_processed_data()
    our_total = df['amount_dollars'].sum()
    sankey_total = sankey_data['spending'] * 1e9
    
    print(f"\nComparison:")
    print(f"   Our CSV total:     ${our_total:,.0f}")
    print(f"   Sankey file total: ${sankey_total:,.0f}")
    print(f"   Difference:        ${our_total - sankey_total:,.0f}")

def main():
    print("🐛 DEBUGGING SANKEY GENERATION PROCESS")
    print("=" * 60)
    
    df = load_processed_data()
    
    # Check for general data issues
    check_data_aggregation_issues(df)
    
    # Debug specific ministries
    problematic_ministries = ['Health', 'Transportation', 'Municipal Affairs and Housing']
    
    for ministry in problematic_ministries:
        debug_ministry_processing(df, ministry)
    
    # Compare with actual Sankey
    compare_with_actual_sankey()

if __name__ == "__main__":
    main() 