#!/usr/bin/env python3
"""
Analyze raw spending data from the JSON file to calculate ministry totals and overall spending.
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

def analyze_spending(df):
    """Analyze spending by ministry and calculate totals"""
    print("=== RAW SPENDING DATA ANALYSIS ===\n")
    
    # Total spending across all ministries
    total_spending = df['Amount $'].sum()
    print(f"TOTAL GOVERNMENT SPENDING 2023-24: ${total_spending:,.0f}")
    print(f"TOTAL GOVERNMENT SPENDING 2023-24: ${total_spending/1e9:.2f} billion\n")
    
    # Group by Ministry and sum amounts
    ministry_totals = df.groupby('Ministry Name')['Amount $'].sum().sort_values(ascending=False)
    
    print("=== SPENDING BY MINISTRY (BILLIONS) ===")
    print("Direct children under spending (big categories):\n")
    
    for ministry, amount in ministry_totals.items():
        billions = amount / 1e9
        print(f"{ministry}: ${billions:.2f}B (${amount:,.0f})")
    
    print(f"\nTotal across all ministries: ${ministry_totals.sum()/1e9:.2f}B")
    
    # Operating vs Capital breakdown
    print("\n=== OPERATING VS CAPITAL BREAKDOWN ===")
    expense_type_totals = df.groupby('Expenditure Category (Operating / Capital)')['Amount $'].sum()
    for expense_type, amount in expense_type_totals.items():
        billions = amount / 1e9
        print(f"{expense_type}: ${billions:.2f}B (${amount:,.0f})")
    
    return ministry_totals, total_spending

def sum_ministry_amounts(ministry_data):
    """Recursively sum all amounts in a ministry's hierarchy"""
    total = 0
    
    if 'amount' in ministry_data:
        return ministry_data['amount'] * 1e9  # Convert back to dollars
    
    if 'children' in ministry_data:
        for child in ministry_data['children']:
            total += sum_ministry_amounts(child)
    
    return total

def compare_with_compact_data():
    """Load and analyze our compact Sankey data for comparison"""
    print("\n=== COMPACT SANKEY DATA ANALYSIS ===\n")
    
    try:
        with open('public/data/sankey_2024_compact.json', 'r') as f:
            sankey_data = json.load(f)
        
        # Get totals from the summary data
        total_spending_summary = sankey_data['spending'] * 1e9  # Convert to dollars
        total_revenue_summary = sankey_data['revenue'] * 1e9
        
        print(f"TOTAL SPENDING (from summary): ${total_spending_summary:,.0f}")
        print(f"TOTAL SPENDING (from summary): ${total_spending_summary/1e9:.2f} billion")
        print(f"TOTAL REVENUE (from summary): ${total_revenue_summary:,.0f}")
        print(f"TOTAL REVENUE (from summary): ${total_revenue_summary/1e9:.2f} billion\n")
        
        # Calculate ministry totals by summing the hierarchical data
        ministry_totals = []
        total_calculated = 0
        
        for ministry in sankey_data['spending_data']['children']:
            ministry_name = ministry['name']
            ministry_total = sum_ministry_amounts(ministry)
            ministry_totals.append((ministry_name, ministry_total))
            total_calculated += ministry_total
        
        print(f"TOTAL SPENDING (calculated): ${total_calculated:,.0f}")
        print(f"TOTAL SPENDING (calculated): ${total_calculated/1e9:.2f} billion\n")
        
        print("=== SANKEY SPENDING BY MINISTRY (BILLIONS) ===")
        ministry_totals.sort(key=lambda x: x[1], reverse=True)
        
        for ministry, amount in ministry_totals:
            billions = amount / 1e9
            print(f"{ministry}: ${billions:.2f}B (${amount:,.0f})")
        
        return total_calculated, ministry_totals
        
    except FileNotFoundError:
        print("Compact sankey data file not found!")
        return None, None

def main():
    # Load and analyze raw data
    df = load_raw_data()
    ministry_totals, total_raw = analyze_spending(df)
    
    # Compare with compact data
    total_sankey, sankey_spending = compare_with_compact_data()
    
    if total_sankey is not None:
        print("\n=== COMPARISON ===")
        difference = total_raw - total_sankey
        percentage_diff = (difference / total_raw) * 100
        
        print(f"Raw data total: ${total_raw/1e9:.2f}B")
        print(f"Sankey data total: ${total_sankey/1e9:.2f}B")
        print(f"Difference: ${difference/1e9:.2f}B ({percentage_diff:.2f}%)")
        
        if abs(percentage_diff) > 1:
            print(f"\n⚠️  SIGNIFICANT DISCREPANCY DETECTED: {percentage_diff:.2f}%")
        else:
            print(f"\n✅ Data appears consistent (difference < 1%)")

if __name__ == "__main__":
    main() 