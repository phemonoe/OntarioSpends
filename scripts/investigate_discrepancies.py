#!/usr/bin/env python3
"""
Investigate specific discrepancies between raw spending data and our Sankey data.
Focus on Health ($73.36B vs $72.63B = $730M difference) and Transportation.
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

def load_processed_data():
    """Load our processed data that we used to create the Sankey"""
    df_expenses = pd.read_csv('clean_expenses_2024.csv')
    df_revenue = pd.read_csv('clean_revenue_2024.csv')
    return df_expenses, df_revenue

def sum_ministry_amounts_sankey(ministry_data):
    """Recursively sum all amounts in a ministry's hierarchy from Sankey data"""
    total = 0
    
    if 'amount' in ministry_data:
        return ministry_data['amount'] * 1e9  # Convert back to dollars
    
    if 'children' in ministry_data:
        for child in ministry_data['children']:
            total += sum_ministry_amounts_sankey(child)
    
    return total

def load_sankey_data():
    """Load our Sankey data"""
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        return json.load(f)

def investigate_ministry_discrepancy(ministry_name, raw_df, processed_df, sankey_data):
    """Deep dive into a specific ministry's discrepancy"""
    
    print(f"\n{'='*60}")
    print(f"🔍 INVESTIGATING {ministry_name.upper()} DISCREPANCY")
    print(f"{'='*60}")
    
    # Raw data total for this ministry
    raw_ministry_data = raw_df[raw_df['Ministry Name'] == ministry_name]
    raw_total = raw_ministry_data['Amount $'].sum()
    
    # Processed data total for this ministry
    processed_ministry_data = processed_df[processed_df['Ministry Name'] == ministry_name]
    processed_total = processed_ministry_data['amount_dollars'].sum()
    
    # Sankey data total for this ministry
    sankey_ministry = None
    for ministry in sankey_data['spending_data']['children']:
        if ministry['name'] == ministry_name:
            sankey_ministry = ministry
            break
    
    sankey_total = sum_ministry_amounts_sankey(sankey_ministry) if sankey_ministry else 0
    
    print(f"💰 TOTALS:")
    print(f"   Raw data:       ${raw_total:,.0f} (${raw_total/1e9:.3f}B)")
    print(f"   Processed data: ${processed_total:,.0f} (${processed_total/1e9:.3f}B)")
    print(f"   Sankey data:    ${sankey_total:,.0f} (${sankey_total/1e9:.3f}B)")
    
    print(f"\n📊 DIFFERENCES:")
    diff_raw_processed = raw_total - processed_total
    diff_processed_sankey = processed_total - sankey_total
    diff_raw_sankey = raw_total - sankey_total
    
    print(f"   Raw → Processed:  ${diff_raw_processed:,.0f} (${diff_raw_processed/1e6:.1f}M)")
    print(f"   Processed → Sankey: ${diff_processed_sankey:,.0f} (${diff_processed_sankey/1e6:.1f}M)")
    print(f"   Raw → Sankey:     ${diff_raw_sankey:,.0f} (${diff_raw_sankey/1e6:.1f}M)")
    
    # Check if there are records in raw data that are missing from processed data
    print(f"\n🔍 DETAILED ANALYSIS:")
    print(f"   Raw data records: {len(raw_ministry_data)}")
    print(f"   Processed data records: {len(processed_ministry_data)}")
    
    # Check for negative amounts that might be filtered out
    raw_negative = raw_ministry_data[raw_ministry_data['Amount $'] < 0]
    if len(raw_negative) > 0:
        negative_total = raw_negative['Amount $'].sum()
        print(f"   Negative amounts in raw: {len(raw_negative)} records, total: ${negative_total:,.0f}")
    
    # Check if processed data has any filtering
    processed_negative = processed_ministry_data[processed_ministry_data['amount_dollars'] < 0]
    if len(processed_negative) > 0:
        negative_total = processed_negative['amount_dollars'].sum()
        print(f"   Negative amounts in processed: {len(processed_negative)} records, total: ${negative_total:,.0f}")
    
    # Look for specific large items that might be missing
    print(f"\n💸 LARGEST RAW ITEMS (top 10):")
    raw_sorted = raw_ministry_data.nlargest(10, 'Amount $')
    for idx, row in raw_sorted.iterrows():
        amount = row['Amount $']
        program = row['Program Name']
        account = row['Standard Account (Expense/Asset Name)']
        details = row['Account Details (Expense/Asset Details)']
        print(f"   ${amount/1e6:.1f}M - {program} - {account}")
        if details != "No Value":
            print(f"        └─ {details}")
    
    # Check if these large items exist in processed data
    print(f"\n🔄 CHECKING IF LARGE ITEMS EXIST IN PROCESSED DATA:")
    for idx, row in raw_sorted.head(5).iterrows():
        amount = row['Amount $']
        program = row['Program Name']
        account = row['Standard Account (Expense/Asset Name)']
        details = row['Account Details (Expense/Asset Details)']
        
        # Try to find this in processed data
        matches = processed_ministry_data[
            (processed_ministry_data['Program Name'] == program) &
            (processed_ministry_data['Standard Account (Expense/Asset Name)'] == account)
        ]
        
        if details != "No Value":
            matches = matches[matches['Account Details (Expense/Asset Details)'] == details]
        
        if len(matches) > 0:
            processed_amount = matches['amount_dollars'].sum()
            print(f"   ✅ Found: ${amount/1e6:.1f}M → ${processed_amount/1e6:.1f}M (diff: ${(amount-processed_amount)/1e6:.1f}M)")
        else:
            print(f"   ❌ MISSING: ${amount/1e6:.1f}M - {program} - {account}")

def investigate_processing_pipeline():
    """Check if our data processing pipeline is losing data"""
    
    print(f"\n{'='*60}")
    print(f"🔍 INVESTIGATING DATA PROCESSING PIPELINE")
    print(f"{'='*60}")
    
    # Check if clean_expenses_2024.csv was created from the raw JSON correctly
    raw_df = load_raw_data()
    processed_df, _ = load_processed_data()
    
    raw_total = raw_df['Amount $'].sum()
    processed_total = processed_df['amount_dollars'].sum()
    
    print(f"💰 PIPELINE TOTALS:")
    print(f"   Raw JSON total:     ${raw_total:,.0f} (${raw_total/1e9:.3f}B)")
    print(f"   Processed CSV total: ${processed_total:,.0f} (${processed_total/1e9:.3f}B)")
    print(f"   Difference:         ${raw_total - processed_total:,.0f} (${(raw_total - processed_total)/1e6:.1f}M)")
    
    # Check record counts
    print(f"\n📊 RECORD COUNTS:")
    print(f"   Raw JSON records:     {len(raw_df)}")
    print(f"   Processed CSV records: {len(processed_df)}")
    print(f"   Records lost:         {len(raw_df) - len(processed_df)}")
    
    # Check for any systematic filtering
    if len(raw_df) != len(processed_df):
        print(f"\n⚠️  RECORDS WERE LOST IN PROCESSING!")
        
        # Find what types of records might be missing
        print(f"   Checking for patterns in missing records...")
        
        # Check if any ministries are completely missing
        raw_ministries = set(raw_df['Ministry Name'].unique())
        processed_ministries = set(processed_df['Ministry Name'].unique())
        
        missing_ministries = raw_ministries - processed_ministries
        if missing_ministries:
            print(f"   Missing ministries: {missing_ministries}")
        
        extra_ministries = processed_ministries - raw_ministries
        if extra_ministries:
            print(f"   Extra ministries: {extra_ministries}")

def main():
    print("🔍 INVESTIGATING SPENDING DISCREPANCIES")
    print("=" * 60)
    
    # Load all data
    raw_df = load_raw_data()
    processed_df, _ = load_processed_data()
    sankey_data = load_sankey_data()
    
    # First, check the overall processing pipeline
    investigate_processing_pipeline()
    
    # Then investigate specific ministries with large discrepancies
    problematic_ministries = [
        'Health',
        'Transportation',
        'Municipal Affairs and Housing'  # This one also showed differences
    ]
    
    for ministry in problematic_ministries:
        investigate_ministry_discrepancy(ministry, raw_df, processed_df, sankey_data)
    
    print(f"\n{'='*60}")
    print(f"🎯 SUMMARY")
    print(f"{'='*60}")
    print("This analysis should reveal exactly where the missing hundreds of millions went!")

if __name__ == "__main__":
    main() 