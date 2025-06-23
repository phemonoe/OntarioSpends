#!/usr/bin/env python3
"""
Debug exactly what our Sankey aggregation is doing wrong.
We know the input is correct, so the bug is in our processing logic.
"""

import pandas as pd
import json

def debug_sankey_aggregation():
    print("🐛 DEBUGGING SANKEY AGGREGATION LOGIC")
    print("=" * 60)
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    print(f"Input CSV total: ${df['amount_dollars'].sum():,.0f}")
    print(f"Input CSV records: {len(df)}")
    
    # Step through the exact logic from our create_compact_sankey.py
    total_from_aggregation = 0
    total_records_processed = 0
    ministry_totals = {}
    
    for ministry_name, ministry_group in df.groupby('Ministry Name'):
        ministry_total = 0
        
        for program_name, program_group in ministry_group.groupby('Program Name'):
            
            # Initialize totals for this program
            operational_total = 0
            substantive_categories = {}
            
            # Process each record in the program
            for _, row in program_group.iterrows():
                account_name = row['Standard Account (Expense/Asset Name)']
                account_details = row['Account Details (Expense/Asset Details)']
                expenditure_category = row['Expenditure Category (Operating / Capital)']
                activity = row['Activity / Item']
                sub_item = row['Sub Item']
                amount = float(row['amount_dollars']) / 1e9  # Convert to billions
                
                total_records_processed += 1
                
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
                    
                    # Create unique key to avoid merging distinct spending items
                    unique_key = f"{category_name}|{expenditure_category}|{activity}|{sub_item}"
                    
                    # Aggregate amounts only for truly identical categories
                    if unique_key in substantive_categories:
                        substantive_categories[unique_key]['amount'] += amount
                    else:
                        substantive_categories[unique_key] = {
                            'name': category_name,
                            'amount': amount,
                            'expenditure_category': expenditure_category,
                            'activity': activity,
                            'sub_item': sub_item
                        }
            
            # Calculate what goes into the Sankey for this program
            program_sankey_total = 0
            
            # Add operations if > 0
            if operational_total > 0:
                program_sankey_total += operational_total
            
            # Add substantive categories
            for unique_key, category_data in substantive_categories.items():
                amount = category_data['amount']
                if amount > 0.001:  # $1M threshold
                    program_sankey_total += amount
                else:
                    # These go into "Other" - but we should still include them!
                    program_sankey_total += amount
            
            ministry_total += program_sankey_total
        
        ministry_totals[ministry_name] = ministry_total
        total_from_aggregation += ministry_total
    
    print(f"\n📊 AGGREGATION RESULTS:")
    print(f"   Records processed: {total_records_processed}")
    print(f"   Total from aggregation: ${total_from_aggregation * 1e9:,.0f}")
    print(f"   Expected total: ${df['amount_dollars'].sum():,.0f}")
    print(f"   Difference: ${df['amount_dollars'].sum() - (total_from_aggregation * 1e9):,.0f}")
    
    # Compare ministry by ministry
    print(f"\n🔍 MINISTRY-BY-MINISTRY COMPARISON:")
    df_ministry_totals = df.groupby('Ministry Name')['amount_dollars'].sum()
    
    print(f"{'Ministry':<40} {'Expected':<12} {'Calculated':<12} {'Difference':<12}")
    print(f"{'-'*80}")
    
    total_diff = 0
    for ministry, expected in df_ministry_totals.head(10).items():
        calculated = ministry_totals.get(ministry, 0) * 1e9
        diff = expected - calculated
        total_diff += diff
        
        if abs(diff) > 1e6:  # Show significant differences
            print(f"{ministry:<40} ${expected/1e9:>6.2f}B  ${calculated/1e9:>6.2f}B  ${diff/1e6:>6.1f}M")
    
    print(f"{'-'*80}")
    print(f"{'TOTAL DIFFERENCE':<40}                    ${total_diff/1e6:>6.1f}M")
    
    # Check if the issue is in our actual Sankey file vs this calculation
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        sankey_data = json.load(f)
    
    actual_sankey_total = sankey_data['spending'] * 1e9
    
    print(f"\n🔍 COMPARISON WITH ACTUAL SANKEY FILE:")
    print(f"   Our calculation: ${total_from_aggregation * 1e9:,.0f}")
    print(f"   Actual Sankey:   ${actual_sankey_total:,.0f}")
    print(f"   Difference:      ${(total_from_aggregation * 1e9) - actual_sankey_total:,.0f}")
    
    if abs((total_from_aggregation * 1e9) - actual_sankey_total) > 1000:
        print(f"   ❌ MISMATCH! Our calculation differs from actual Sankey file!")
    else:
        print(f"   ✅ Our calculation matches the Sankey file.")

def find_problematic_records():
    """Find specific records that might be causing issues"""
    
    print(f"\n{'='*60}")
    print(f"🔍 FINDING PROBLEMATIC RECORDS")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Look for records with unusual characteristics that might cause aggregation issues
    
    # 1. Records with missing or empty key fields
    print(f"Records with potential aggregation issues:")
    
    missing_activity = df[df['Activity / Item'].isna() | (df['Activity / Item'] == '')]
    print(f"   Missing Activity/Item: {len(missing_activity)} records, ${missing_activity['amount_dollars'].sum():,.0f}")
    
    missing_sub_item = df[df['Sub Item'].isna() | (df['Sub Item'] == '')]
    print(f"   Missing Sub Item: {len(missing_sub_item)} records, ${missing_sub_item['amount_dollars'].sum():,.0f}")
    
    missing_details = df[df['Account Details (Expense/Asset Details)'].isna() | (df['Account Details (Expense/Asset Details)'] == '')]
    print(f"   Missing Account Details: {len(missing_details)} records, ${missing_details['amount_dollars'].sum():,.0f}")
    
    # 2. Look for very large amounts that might be getting lost
    print(f"\nLargest individual records:")
    largest = df.nlargest(10, 'amount_dollars')
    for _, row in largest.iterrows():
        amount = row['amount_dollars']
        ministry = row['Ministry Name']
        program = row['Program Name']
        account = row['Standard Account (Expense/Asset Name)']
        details = row['Account Details (Expense/Asset Details)']
        
        print(f"   ${amount/1e9:.3f}B - {ministry} - {program}")
        print(f"      {account}")
        if pd.notna(details) and details != '':
            print(f"      └─ {details}")

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

def main():
    debug_sankey_aggregation()
    find_problematic_records()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"If our calculation matches the Sankey file, the bug is in our generation script.")
    print(f"If our calculation differs from the Sankey file, the bug is in this logic.")

if __name__ == "__main__":
    main() 