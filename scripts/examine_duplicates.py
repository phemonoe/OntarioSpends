#!/usr/bin/env python3
"""
Examine the duplicate categories in detail to understand the data structure.
"""

import pandas as pd
import json

def examine_duplicates():
    print("🔍 EXAMINING DUPLICATE CATEGORIES IN DETAIL")
    print("=" * 60)
    
    # Load the processed data
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Load raw data for comparison
    with open('PublicAccountsPDFs/2024/f4801adb-b00a-4798-9802-005231e275ee (1).json', 'r') as f:
        raw_data = json.load(f)
    
    fields = [field['id'] for field in raw_data['fields']]
    raw_df = pd.DataFrame(raw_data['records'], columns=fields)
    raw_df['Amount $'] = pd.to_numeric(raw_df['Amount $'])
    
    # Focus on the problematic duplicates
    problematic_cases = [
        ('Municipal Affairs and Housing', 'Transfer payments', 'Homelessness Programs'),
        ('Municipal Affairs and Housing', 'Transfer payments', 'National Housing Strategy Programs'),
        ('Transportation', 'Transfer payments', 'Municipal Transit'),
        ('Transportation', 'Transfer payments', 'Ontario Northland Transportation Commission'),
    ]
    
    for ministry, account, details in problematic_cases:
        print(f"\n{'='*60}")
        print(f"🔍 EXAMINING: {ministry} → {account} → {details}")
        print(f"{'='*60}")
        
        # Find these records in processed data
        processed_matches = df[
            (df['Ministry Name'] == ministry) &
            (df['Standard Account (Expense/Asset Name)'] == account) &
            (df['Account Details (Expense/Asset Details)'] == details)
        ]
        
        # Find these records in raw data
        raw_matches = raw_df[
            (raw_df['Ministry Name'] == ministry) &
            (raw_df['Standard Account (Expense/Asset Name)'] == account) &
            (raw_df['Account Details (Expense/Asset Details)'] == details)
        ]
        
        print(f"📊 PROCESSED DATA:")
        print(f"   Records found: {len(processed_matches)}")
        print(f"   Total amount: ${processed_matches['amount_dollars'].sum():,.0f}")
        
        print(f"\n📊 RAW DATA:")
        print(f"   Records found: {len(raw_matches)}")
        print(f"   Total amount: ${raw_matches['Amount $'].sum():,.0f}")
        
        print(f"\n📋 DETAILED BREAKDOWN:")
        for idx, (_, row) in enumerate(processed_matches.iterrows()):
            print(f"   Record {idx+1}:")
            print(f"      Amount: ${row['amount_dollars']:,.0f}")
            print(f"      Program: {row['Program Name']}")
            print(f"      Activity: {row['Activity / Item']}")
            print(f"      Sub Item: {row['Sub Item']}")
            print(f"      Expenditure Category: {row['Expenditure Category (Operating / Capital)']}")
        
        # Check if these are legitimate separate items or should be consolidated
        unique_programs = processed_matches['Program Name'].unique()
        unique_activities = processed_matches['Activity / Item'].unique()
        unique_categories = processed_matches['Expenditure Category (Operating / Capital)'].unique()
        
        print(f"\n🔍 ANALYSIS:")
        print(f"   Unique Programs: {list(unique_programs)}")
        print(f"   Unique Activities: {list(unique_activities)}")
        print(f"   Unique Categories: {list(unique_categories)}")
        
        # Check if amounts are suspiciously similar (might be duplicates)
        amounts = processed_matches['amount_dollars'].tolist()
        if len(amounts) > 1:
            print(f"   Individual amounts: {[f'${amt:,.0f}' for amt in amounts]}")
            if len(set(amounts)) == 1:
                print(f"   ⚠️  ALL AMOUNTS ARE IDENTICAL - LIKELY DUPLICATES!")
            elif len(set(amounts)) < len(amounts):
                print(f"   ⚠️  SOME AMOUNTS ARE IDENTICAL - POSSIBLE DUPLICATES!")

def examine_health_missing_amount():
    """Try to find where Health's missing $734M went"""
    
    print(f"\n{'='*60}")
    print(f"🔍 SEARCHING FOR HEALTH'S MISSING $734M")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Find all Health records
    health_records = df[df['Ministry Name'] == 'Health']
    
    print(f"Total Health records: {len(health_records)}")
    print(f"Total Health amount: ${health_records['amount_dollars'].sum():,.0f}")
    
    # Look for any Health spending that might be categorized elsewhere
    potential_health_keywords = [
        'health', 'hospital', 'medical', 'drug', 'physician', 'healthcare', 
        'ontario health', 'ohip', 'clinic', 'cancer', 'mental health'
    ]
    
    print(f"\n🔍 SEARCHING OTHER MINISTRIES FOR HEALTH-RELATED SPENDING:")
    
    non_health_records = df[df['Ministry Name'] != 'Health']
    
    for keyword in potential_health_keywords:
        # Search in various fields
        keyword_matches = non_health_records[
            non_health_records['Program Name'].str.contains(keyword, case=False, na=False) |
            non_health_records['Activity / Item'].str.contains(keyword, case=False, na=False) |
            non_health_records['Account Details (Expense/Asset Details)'].str.contains(keyword, case=False, na=False)
        ]
        
        if len(keyword_matches) > 0:
            total_amount = keyword_matches['amount_dollars'].sum()
            if total_amount > 1e6:  # Only report significant amounts
                print(f"   '{keyword}' found in other ministries: ${total_amount:,.0f}")
                for ministry in keyword_matches['Ministry Name'].unique():
                    ministry_amount = keyword_matches[keyword_matches['Ministry Name'] == ministry]['amount_dollars'].sum()
                    print(f"      {ministry}: ${ministry_amount:,.0f}")

def check_sankey_aggregation_logic():
    """Check if our Sankey aggregation logic is losing data"""
    
    print(f"\n{'='*60}")
    print(f"🔍 CHECKING SANKEY AGGREGATION LOGIC")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Test the aggregation logic from our compact sankey script
    total_before_aggregation = df['amount_dollars'].sum()
    print(f"Total before aggregation: ${total_before_aggregation:,.0f}")
    
    # Group by the same keys we use in the Sankey generation
    aggregated = df.groupby([
        'Ministry Name', 
        'Program Name', 
        'Standard Account (Expense/Asset Name)', 
        'Account Details (Expense/Asset Details)'
    ])['amount_dollars'].sum().reset_index()
    
    total_after_aggregation = aggregated['amount_dollars'].sum()
    print(f"Total after aggregation: ${total_after_aggregation:,.0f}")
    print(f"Difference: ${total_before_aggregation - total_after_aggregation:,.0f}")
    
    if abs(total_before_aggregation - total_after_aggregation) < 1:
        print("✅ Aggregation preserves total (no data loss)")
    else:
        print("❌ Aggregation loses data!")
    
    # Check record count reduction
    print(f"Records before aggregation: {len(df)}")
    print(f"Records after aggregation: {len(aggregated)}")
    print(f"Records eliminated: {len(df) - len(aggregated)}")

def main():
    examine_duplicates()
    examine_health_missing_amount()
    check_sankey_aggregation_logic()

if __name__ == "__main__":
    main() 