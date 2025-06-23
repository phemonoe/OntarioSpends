#!/usr/bin/env python3
"""
Trace the exact Sankey generation logic to find data loss.
"""

import pandas as pd
import json

def trace_sankey_generation():
    print("🔍 TRACING SANKEY GENERATION LOGIC")
    print("=" * 60)
    
    # Load the processed data
    df = pd.read_csv('clean_expenses_2024.csv')
    print(f"Input CSV total: ${df['amount_dollars'].sum():,.0f}")
    print(f"Input CSV records: {len(df)}")
    
    # Manually step through the Sankey generation logic
    total_included_in_sankey = 0
    total_operational = 0
    total_substantive = 0
    records_processed = 0
    
    # Group by ministry first
    for ministry_name, ministry_group in df.groupby('Ministry Name'):
        ministry_total = 0
        
        # Group by program within ministry
        for program_name, program_group in ministry_group.groupby('Program Name'):
            program_total = 0
            
            # Process each record in the program
            for _, row in program_group.iterrows():
                account_name = row['Standard Account (Expense/Asset Name)']
                account_details = row['Account Details (Expense/Asset Details)']
                expenditure_category = row['Expenditure Category (Operating / Capital)']
                activity = row['Activity / Item']
                sub_item = row['Sub Item']
                amount = float(row['amount_dollars'])
                
                records_processed += 1
                
                # Apply the consolidation logic
                if should_consolidate_category(account_name, account_details):
                    # This goes into operations
                    total_operational += amount
                    program_total += amount
                else:
                    # This is substantive spending
                    total_substantive += amount
                    program_total += amount
            
            ministry_total += program_total
        
        total_included_in_sankey += ministry_total
    
    print(f"\n📊 MANUAL TRACE RESULTS:")
    print(f"   Records processed: {records_processed}")
    print(f"   Total operational: ${total_operational:,.0f}")
    print(f"   Total substantive: ${total_substantive:,.0f}")
    print(f"   Total included in Sankey: ${total_included_in_sankey:,.0f}")
    print(f"   Difference from input: ${df['amount_dollars'].sum() - total_included_in_sankey:,.0f}")
    
    # Load actual Sankey data for comparison
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        sankey_data = json.load(f)
    
    actual_sankey_total = sankey_data['spending'] * 1e9
    print(f"\n🔍 COMPARISON WITH ACTUAL SANKEY:")
    print(f"   Manual calculation: ${total_included_in_sankey:,.0f}")
    print(f"   Actual Sankey file: ${actual_sankey_total:,.0f}")
    print(f"   Difference: ${total_included_in_sankey - actual_sankey_total:,.0f}")

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

def check_individual_ministry_totals():
    """Check if individual ministry totals match between raw and Sankey"""
    
    print(f"\n{'='*60}")
    print(f"🔍 CHECKING INDIVIDUAL MINISTRY TOTALS")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        sankey_data = json.load(f)
    
    # Calculate raw totals by ministry
    raw_ministry_totals = df.groupby('Ministry Name')['amount_dollars'].sum().sort_values(ascending=False)
    
    # Calculate Sankey totals by ministry
    def sum_ministry_amounts(ministry_data):
        total = 0
        if 'amount' in ministry_data:
            return ministry_data['amount'] * 1e9
        if 'children' in ministry_data:
            for child in ministry_data['children']:
                total += sum_ministry_amounts(child)
        return total
    
    sankey_ministry_totals = {}
    for ministry in sankey_data['spending_data']['children']:
        ministry_name = ministry['name']
        ministry_total = sum_ministry_amounts(ministry)
        sankey_ministry_totals[ministry_name] = ministry_total
    
    print(f"{'Ministry':<40} {'Raw Total':<15} {'Sankey Total':<15} {'Difference':<15}")
    print(f"{'-'*85}")
    
    total_diff = 0
    for ministry, raw_total in raw_ministry_totals.head(10).items():
        sankey_total = sankey_ministry_totals.get(ministry, 0)
        diff = raw_total - sankey_total
        total_diff += diff
        
        print(f"{ministry:<40} ${raw_total/1e9:>6.3f}B     ${sankey_total/1e9:>6.3f}B     ${diff/1e6:>6.1f}M")
    
    print(f"{'-'*85}")
    print(f"{'TOTAL DIFFERENCE':<40}                               ${total_diff/1e6:>6.1f}M")

def main():
    trace_sankey_generation()
    check_individual_ministry_totals()

if __name__ == "__main__":
    main() 