#!/usr/bin/env python3

import pandas as pd
import json

def debug_transportation_aggregation():
    print("🚀 DEBUGGING TRANSPORTATION AGGREGATION")
    print("=" * 80)
    
    # Load raw data
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Filter Transportation records
    transport_df = df[df['Ministry Name'] == 'Transportation'].copy()
    print(f"📊 Total Transportation records: {len(transport_df)}")
    
    # Calculate totals by type
    operating = transport_df[transport_df['Expenditure Category (Operating / Capital)'] == 'Operating Expense']
    capital = transport_df[transport_df['Expenditure Category (Operating / Capital)'] == 'Capital Expense']
    
    print(f"   Operating records: {len(operating)}")
    print(f"   Capital records: {len(capital)}")
    print()
    
    operating_total = operating['amount_dollars'].sum()
    capital_total = capital['amount_dollars'].sum()
    raw_total = transport_df['amount_dollars'].sum()
    
    print(f"💰 RAW TOTALS:")
    print(f"   Operating: ${operating_total:,.0f}")
    print(f"   Capital:   ${capital_total:,.0f}")
    print(f"   Total:     ${raw_total:,.0f}")
    print()
    
    # Now simulate Sankey aggregation
    print("🔄 SIMULATING SANKEY AGGREGATION...")
    print("-" * 50)
    
    # Group by the same keys as create_compact_sankey.py
    # This mimics the aggregation logic
    grouped = transport_df.groupby([
        'Ministry Name',
        'Expenditure Category (Operating / Capital)', 
        'Program Name',
        'Standard Account (Expense/Asset Name)'
    ])['amount_dollars'].sum().reset_index()
    
    sankey_total = grouped['amount_dollars'].sum()
    print(f"💰 SANKEY TOTALS:")
    print(f"   Aggregated: ${sankey_total:,.0f}")
    print(f"   Difference: ${sankey_total - raw_total:,.0f}")
    print()
    
    # Look for potential duplicates
    print("🔍 CHECKING FOR DUPLICATE ENTITIES...")
    print("-" * 50)
    
    # Look at the large Metrolinx items specifically
    metrolinx_items = transport_df[transport_df['Account Details (Expense/Asset Details)'].str.contains('Metrolinx', na=False)]
    print("📋 METROLINX ITEMS:")
    for _, row in metrolinx_items.iterrows():
        print(f"   {row['Expenditure Category (Operating / Capital)']}: ${row['amount_dollars']:,.0f} - {row['Account Details (Expense/Asset Details)']}")
    print(f"   Total Metrolinx: ${metrolinx_items['amount_dollars'].sum():,.0f}")
    print()
    
    # Look at Municipal Transit items
    municipal_items = transport_df[transport_df['Account Details (Expense/Asset Details)'].str.contains('Municipal Transit', na=False)]
    print("📋 MUNICIPAL TRANSIT ITEMS:")
    for _, row in municipal_items.iterrows():
        print(f"   {row['Expenditure Category (Operating / Capital)']}: ${row['amount_dollars']:,.0f} - {row['Account Details (Expense/Asset Details)']}")
    print(f"   Total Municipal Transit: ${municipal_items['amount_dollars'].sum():,.0f}")
    print()
    
    # Load and check Sankey data
    print("📊 CHECKING SANKEY OUTPUT...")
    print("-" * 50)
    
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        sankey_data = json.load(f)
    
    # Find Transportation in the Sankey
    transport_sankey_total = 0
    for link in sankey_data['links']:
        source_name = sankey_data['nodes'][link['source']]['name']
        if source_name == 'Transportation':
            transport_sankey_total += link['value']
    
    print(f"💰 SANKEY FILE TOTALS:")
    print(f"   Transportation: ${transport_sankey_total:,.0f}")
    print(f"   Raw vs Sankey: ${transport_sankey_total - raw_total:,.0f}")
    print()
    
    if transport_sankey_total != raw_total:
        print("❌ MISMATCH FOUND!")
        print("   This explains the discrepancy.")
        
        # Try to identify specific issues
        print("\n🔍 DETAILED ANALYSIS...")
        print("-" * 50)
        
        # Check if it's an aggregation issue with the grouping
        test_grouping = transport_df.groupby([
            'Ministry Name',
            'Program Name', 
            'Account Details (Expense/Asset Details)'
        ])['amount_dollars'].sum().reset_index()
        
        test_total = test_grouping['amount_dollars'].sum()
        print(f"Alternative grouping total: ${test_total:,.0f}")
        
        # Look for NaN values that might be causing issues
        nan_programs = transport_df[transport_df['Program Name'].isna()]
        if len(nan_programs) > 0:
            print(f"\n⚠️  Found {len(nan_programs)} records with NaN Program Names:")
            for _, row in nan_programs.iterrows():
                print(f"   ${row['amount_dollars']:,.0f} - {row['Account Details (Expense/Asset Details)']}")
    else:
        print("✅ No mismatch - issue is elsewhere")

if __name__ == "__main__":
    debug_transportation_aggregation() 