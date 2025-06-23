#!/usr/bin/env python3

import json

def calculate_ministry_total(ministry_data):
    """Recursively calculate total amount for a ministry"""
    total = 0
    
    def traverse(node):
        nonlocal total
        if 'amount' in node:
            total += node['amount']
        if 'children' in node:
            for child in node['children']:
                traverse(child)
    
    traverse(ministry_data)
    return total

def main():
    print("🧮 CALCULATING TRANSPORTATION TOTAL IN SANKEY DATA")
    print("=" * 60)
    
    with open('public/data/sankey_2024_compact.json', 'r') as f:
        data = json.load(f)
    
    # Find Transportation ministry in spending data
    spending_data = data['spending_data']
    transportation_data = None
    
    for ministry in spending_data['children']:
        if ministry['name'] == 'Transportation':
            transportation_data = ministry
            break
    
    if transportation_data:
        total_billions = calculate_ministry_total(transportation_data)
        total_dollars = total_billions * 1_000_000_000
        
        print(f"💰 Transportation Total in Sankey:")
        print(f"   Billions: {total_billions:.6f}B")
        print(f"   Dollars:  ${total_dollars:,.0f}")
        
        # Compare with expected
        expected = 12_073_573_913
        difference = total_dollars - expected
        
        print(f"\n📊 Comparison:")
        print(f"   Expected: ${expected:,.0f}")
        print(f"   Actual:   ${total_dollars:,.0f}")
        print(f"   Difference: ${difference:,.0f}")
        
        if abs(difference) > 1000:  # More than $1000 difference
            print(f"\n❌ SIGNIFICANT DIFFERENCE FOUND!")
        else:
            print(f"\n✅ Amounts match closely")
            
    else:
        print("❌ Transportation ministry not found in Sankey data!")

if __name__ == "__main__":
    main() 