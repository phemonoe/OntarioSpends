#!/usr/bin/env python3
"""
Find the exact records that are being lost or processed incorrectly.
"""

import pandas as pd
import json

def find_missing_records():
    print("🔍 FINDING MISSING/PROBLEMATIC RECORDS")
    print("=" * 60)
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    print(f"Total records in CSV: {len(df)}")
    print(f"Total amount in CSV: ${df['amount_dollars'].sum():,.0f}")
    
    # Check for any data quality issues
    print(f"\n📊 DATA QUALITY CHECKS:")
    
    # Check for null amounts
    null_amounts = df[df['amount_dollars'].isna()]
    print(f"   Records with null amounts: {len(null_amounts)}")
    
    # Check for zero amounts
    zero_amounts = df[df['amount_dollars'] == 0]
    print(f"   Records with zero amounts: {len(zero_amounts)}")
    
    # Check for negative amounts
    negative_amounts = df[df['amount_dollars'] < 0]
    print(f"   Records with negative amounts: {len(negative_amounts)}")
    if len(negative_amounts) > 0:
        neg_total = negative_amounts['amount_dollars'].sum()
        print(f"      Total negative amount: ${neg_total:,.0f}")
        print("      Negative records by ministry:")
        for ministry, ministry_neg in negative_amounts.groupby('Ministry Name'):
            ministry_total = ministry_neg['amount_dollars'].sum()
            print(f"         {ministry}: ${ministry_total:,.0f} ({len(ministry_neg)} records)")
    
    # Check for records with missing key fields
    missing_ministry = df[df['Ministry Name'].isna() | (df['Ministry Name'] == '')]
    missing_program = df[df['Program Name'].isna() | (df['Program Name'] == '')]
    missing_account = df[df['Standard Account (Expense/Asset Name)'].isna() | (df['Standard Account (Expense/Asset Name)'] == '')]
    
    print(f"   Records with missing Ministry Name: {len(missing_ministry)}")
    print(f"   Records with missing Program Name: {len(missing_program)}")
    print(f"   Records with missing Account Name: {len(missing_account)}")
    
    # Look specifically at the $734.8M difference in Health
    find_health_discrepancy(df)
    
    # Look specifically at the Transportation issue
    find_transportation_discrepancy(df)

def find_health_discrepancy(df):
    print(f"\n{'='*60}")
    print(f"🔍 INVESTIGATING HEALTH'S $734.8M DISCREPANCY")
    print(f"{'='*60}")
    
    health_records = df[df['Ministry Name'] == 'Health']
    print(f"Health records: {len(health_records)}")
    print(f"Health total: ${health_records['amount_dollars'].sum():,.0f}")
    
    # Check if any Health records have issues
    health_negative = health_records[health_records['amount_dollars'] < 0]
    if len(health_negative) > 0:
        print(f"Health negative records: {len(health_negative)}")
        print(f"Health negative total: ${health_negative['amount_dollars'].sum():,.0f}")
        
        for _, row in health_negative.iterrows():
            print(f"   ${row['amount_dollars']:,.0f} - {row['Program Name']} - {row['Standard Account (Expense/Asset Name)']}")
    
    # Check if there are any large Health records that might be filtered out
    print(f"\nLargest Health records:")
    health_sorted = health_records.nlargest(5, 'amount_dollars')
    for _, row in health_sorted.iterrows():
        print(f"   ${row['amount_dollars']:,.0f} - {row['Program Name']} - {row['Standard Account (Expense/Asset Name)']} - {row['Account Details (Expense/Asset Details)']}")
    
    # Check if Health has any records that might be classified as operational when they shouldn't be
    health_operations = 0
    health_substantive = 0
    
    for _, row in health_records.iterrows():
        account_name = row['Standard Account (Expense/Asset Name)']
        account_details = row['Account Details (Expense/Asset Details)']
        amount = row['amount_dollars']
        
        if should_consolidate_category(account_name, account_details):
            health_operations += amount
        else:
            health_substantive += amount
    
    print(f"\nHealth spending breakdown:")
    print(f"   Operations: ${health_operations:,.0f}")
    print(f"   Substantive: ${health_substantive:,.0f}")
    print(f"   Total: ${health_operations + health_substantive:,.0f}")
    print(f"   Expected total: ${health_records['amount_dollars'].sum():,.0f}")
    print(f"   Difference: ${health_records['amount_dollars'].sum() - (health_operations + health_substantive):,.0f}")

def find_transportation_discrepancy(df):
    print(f"\n{'='*60}")
    print(f"🔍 INVESTIGATING TRANSPORTATION'S +$327M DISCREPANCY")
    print(f"{'='*60}")
    
    transport_records = df[df['Ministry Name'] == 'Transportation']
    print(f"Transportation records: {len(transport_records)}")
    print(f"Transportation total: ${transport_records['amount_dollars'].sum():,.0f}")
    
    # Check for negative amounts in Transportation
    transport_negative = transport_records[transport_records['amount_dollars'] < 0]
    if len(transport_negative) > 0:
        print(f"Transportation negative records: {len(transport_negative)}")
        print(f"Transportation negative total: ${transport_negative['amount_dollars'].sum():,.0f}")
        
        print(f"Negative Transportation records:")
        for _, row in transport_negative.iterrows():
            print(f"   ${row['amount_dollars']:,.0f} - {row['Program Name']} - {row['Standard Account (Expense/Asset Name)']} - {row['Account Details (Expense/Asset Details)']}")

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

def compare_with_sankey_links():
    """Check if the Sankey links add up correctly"""
    
    print(f"\n{'='*60}")
    print(f"🔍 CHECKING SANKEY LINKS")
    print(f"{'='*60}")
    
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        sankey_data = json.load(f)
    
    # Sum all links
    total_from_links = 0
    revenue_links = 0
    spending_links = 0
    
    for link in sankey_data['links']:
        value = link['value'] * 1e9
        source_name = sankey_data['nodes'][link['source']]['name']
        target_name = sankey_data['nodes'][link['target']]['name']
        
        total_from_links += value
        
        # Check if this is revenue or spending
        if 'Revenue' in source_name or source_name in ['Total Federal Transfers', 'Other Revenue']:
            revenue_links += value
        else:
            spending_links += value
    
    print(f"Total from all links: ${total_from_links:,.0f}")
    print(f"Revenue links total: ${revenue_links:,.0f}")
    print(f"Spending links total: ${spending_links:,.0f}")
    print(f"Sankey summary spending: ${sankey_data['spending'] * 1e9:,.0f}")
    print(f"Sankey summary revenue: ${sankey_data['revenue'] * 1e9:,.0f}")

def main():
    find_missing_records()
    compare_with_sankey_links()

if __name__ == "__main__":
    main() 