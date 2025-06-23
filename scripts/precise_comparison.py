#!/usr/bin/env python3
"""
Precise comparison between raw data and compact Sankey for Health and Transportation.
We WILL find that missing $321M.
"""

import json
import pandas as pd

def load_raw_data():
    """Load the raw JSON data"""
    with open('PublicAccountsPDFs/2024/f4801adb-b00a-4798-9802-005231e275ee (1).json', 'r') as f:
        data = json.load(f)
    
    fields = [field['id'] for field in data['fields']]
    records = data['records']
    df = pd.DataFrame(records, columns=fields)
    df['Amount $'] = pd.to_numeric(df['Amount $'])
    return df

def load_processed_data():
    """Load our processed CSV data"""
    return pd.read_csv('clean_expenses_2024.csv')

def load_sankey_data():
    """Load our Sankey data"""
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        return json.load(f)

def sum_ministry_amounts_sankey(ministry_data):
    """Recursively sum all amounts in a ministry's hierarchy from Sankey data"""
    total = 0
    
    if 'amount' in ministry_data:
        return ministry_data['amount'] * 1e9  # Convert back to dollars
    
    if 'children' in ministry_data:
        for child in ministry_data['children']:
            total += sum_ministry_amounts_sankey(child)
    
    return total

def precise_ministry_comparison(ministry_name):
    """Do a line-by-line comparison for a specific ministry"""
    
    print(f"\n{'='*80}")
    print(f"🔍 PRECISE COMPARISON: {ministry_name.upper()}")
    print(f"{'='*80}")
    
    # Load all data sources
    raw_df = load_raw_data()
    processed_df = load_processed_data()
    sankey_data = load_sankey_data()
    
    # Filter for this ministry
    raw_ministry = raw_df[raw_df['Ministry Name'] == ministry_name]
    processed_ministry = processed_df[processed_df['Ministry Name'] == ministry_name]
    
    # Get Sankey total for this ministry
    sankey_ministry = None
    for ministry in sankey_data['spending_data']['children']:
        if ministry['name'] == ministry_name:
            sankey_ministry = ministry
            break
    
    sankey_total = sum_ministry_amounts_sankey(sankey_ministry) if sankey_ministry else 0
    
    print(f"📊 TOTALS:")
    raw_total = raw_ministry['Amount $'].sum()
    processed_total = processed_ministry['amount_dollars'].sum()
    
    print(f"   Raw JSON:       ${raw_total:>15,.0f}")
    print(f"   Processed CSV:  ${processed_total:>15,.0f}")
    print(f"   Compact Sankey: ${sankey_total:>15,.0f}")
    
    print(f"\n💰 DIFFERENCES:")
    diff_raw_processed = raw_total - processed_total
    diff_processed_sankey = processed_total - sankey_total
    diff_raw_sankey = raw_total - sankey_total
    
    print(f"   Raw → Processed:    ${diff_raw_processed:>12,.0f}")
    print(f"   Processed → Sankey: ${diff_processed_sankey:>12,.0f}")
    print(f"   Raw → Sankey:       ${diff_raw_sankey:>12,.0f}")
    
    if abs(diff_raw_processed) > 1000:
        print(f"   ⚠️  DATA LOST IN PROCESSING!")
        investigate_processing_loss(raw_ministry, processed_ministry, ministry_name)
    
    if abs(diff_processed_sankey) > 1000:
        print(f"   ⚠️  DATA LOST IN SANKEY GENERATION!")
        investigate_sankey_loss(processed_ministry, sankey_ministry, ministry_name)
    
    return {
        'ministry': ministry_name,
        'raw_total': raw_total,
        'processed_total': processed_total,
        'sankey_total': sankey_total,
        'raw_processed_diff': diff_raw_processed,
        'processed_sankey_diff': diff_processed_sankey,
        'raw_sankey_diff': diff_raw_sankey
    }

def investigate_processing_loss(raw_ministry, processed_ministry, ministry_name):
    """Investigate data loss between raw and processed data"""
    
    print(f"\n🔍 INVESTIGATING PROCESSING LOSS FOR {ministry_name}:")
    
    raw_records = len(raw_ministry)
    processed_records = len(processed_ministry)
    
    print(f"   Raw records: {raw_records}")
    print(f"   Processed records: {processed_records}")
    print(f"   Records lost: {raw_records - processed_records}")
    
    if raw_records != processed_records:
        print(f"   ❌ RECORD COUNT MISMATCH!")
        
        # Check for specific differences
        raw_programs = set(raw_ministry['Program Name'].unique())
        processed_programs = set(processed_ministry['Program Name'].unique())
        
        missing_programs = raw_programs - processed_programs
        if missing_programs:
            print(f"   Missing programs: {missing_programs}")
            for program in missing_programs:
                lost_amount = raw_ministry[raw_ministry['Program Name'] == program]['Amount $'].sum()
                print(f"      {program}: ${lost_amount:,.0f}")

def investigate_sankey_loss(processed_ministry, sankey_ministry, ministry_name):
    """Investigate data loss between processed data and Sankey"""
    
    print(f"\n🔍 INVESTIGATING SANKEY LOSS FOR {ministry_name}:")
    
    # Manual calculation of what should be in Sankey
    total_should_be_in_sankey = 0
    total_operational = 0
    total_substantive = 0
    records_processed = 0
    
    for _, row in processed_ministry.iterrows():
        account_name = row['Standard Account (Expense/Asset Name)']
        account_details = row['Account Details (Expense/Asset Details)']
        amount = row['amount_dollars']
        
        records_processed += 1
        
        if should_consolidate_category(account_name, account_details):
            total_operational += amount
        else:
            total_substantive += amount
        
        total_should_be_in_sankey += amount
    
    sankey_actual = sum_ministry_amounts_sankey(sankey_ministry) if sankey_ministry else 0
    
    print(f"   Records processed: {records_processed}")
    print(f"   Should be in Sankey: ${total_should_be_in_sankey:,.0f}")
    print(f"   Actually in Sankey:  ${sankey_actual:,.0f}")
    print(f"   Difference:          ${total_should_be_in_sankey - sankey_actual:,.0f}")
    print(f"   Operational total:   ${total_operational:,.0f}")
    print(f"   Substantive total:   ${total_substantive:,.0f}")
    
    if abs(total_should_be_in_sankey - sankey_actual) > 1000:
        print(f"   ❌ SANKEY GENERATION ERROR!")
        
        # Look for specific items that might be missing
        print(f"\n   Checking for missing large items...")
        large_items = processed_ministry.nlargest(10, 'amount_dollars')
        for _, row in large_items.iterrows():
            amount = row['amount_dollars']
            program = row['Program Name']
            account = row['Standard Account (Expense/Asset Name)']
            details = row['Account Details (Expense/Asset Details)']
            print(f"      ${amount/1e6:.1f}M - {program} - {account}")
            if pd.notna(details) and details != '':
                print(f"         └─ {details}")

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

def check_overall_totals():
    """Check overall totals across all data sources"""
    
    print(f"\n{'='*80}")
    print(f"🔍 OVERALL TOTALS CHECK")
    print(f"{'='*80}")
    
    raw_df = load_raw_data()
    processed_df = load_processed_data()
    sankey_data = load_sankey_data()
    
    raw_total = raw_df['Amount $'].sum()
    processed_total = processed_df['amount_dollars'].sum()
    sankey_total = sankey_data['spending'] * 1e9
    
    print(f"📊 GOVERNMENT-WIDE TOTALS:")
    print(f"   Raw JSON total:       ${raw_total:>15,.0f}")
    print(f"   Processed CSV total:  ${processed_total:>15,.0f}")
    print(f"   Compact Sankey total: ${sankey_total:>15,.0f}")
    
    print(f"\n💰 DIFFERENCES:")
    print(f"   Raw → Processed:      ${raw_total - processed_total:>12,.0f}")
    print(f"   Processed → Sankey:   ${processed_total - sankey_total:>12,.0f}")
    print(f"   Raw → Sankey:         ${raw_total - sankey_total:>12,.0f}")
    
    if abs(raw_total - processed_total) > 1000:
        print(f"   ⚠️  DATA LOST IN PROCESSING PIPELINE!")
    
    if abs(processed_total - sankey_total) > 1000:
        print(f"   ⚠️  DATA LOST IN SANKEY GENERATION!")
        print(f"       This is our ${(processed_total - sankey_total)/1e6:.1f}M problem!")

def main():
    print("🔍 PRECISE MINISTRY COMPARISON - FINDING THE MISSING $321M")
    print("=" * 80)
    
    # Check overall totals first
    check_overall_totals()
    
    # Precise comparison for problematic ministries
    results = []
    problematic_ministries = ['Health', 'Transportation']
    
    for ministry in problematic_ministries:
        result = precise_ministry_comparison(ministry)
        results.append(result)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"🎯 SUMMARY OF FINDINGS")
    print(f"{'='*80}")
    
    total_discrepancy = 0
    for result in results:
        ministry = result['ministry']
        diff = result['raw_sankey_diff']
        total_discrepancy += diff
        
        print(f"{ministry:<15}: ${diff:>12,.0f} difference (Raw → Sankey)")
    
    print(f"{'='*40}")
    print(f"{'TOTAL':<15}: ${total_discrepancy:>12,.0f}")
    
    if abs(total_discrepancy) > 100e6:  # More than $100M
        print(f"\n❌ UNACCEPTABLE DISCREPANCY!")
        print(f"We must find and fix this ${abs(total_discrepancy)/1e6:.1f}M difference.")
    else:
        print(f"\n✅ Discrepancy within acceptable bounds.")

if __name__ == "__main__":
    main() 