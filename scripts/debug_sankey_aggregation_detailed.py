#!/usr/bin/env python3

import pandas as pd
import json

def debug_transportation_aggregation():
    print("🔬 DETAILED TRANSPORTATION SANKEY AGGREGATION DEBUG")
    print("=" * 80)
    
    # Load raw data
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Filter Transportation records
    transport_df = df[df['Ministry Name'] == 'Transportation'].copy()
    
    print(f"📊 Transportation records: {len(transport_df)}")
    print(f"💰 Raw total: ${transport_df['amount_dollars'].sum():,.0f}")
    print()
    
    # Simulate the exact aggregation logic from create_compact_sankey.py
    print("🔄 SIMULATING SANKEY AGGREGATION LOGIC...")
    print("-" * 60)
    
    ministry_total = 0
    
    for program_name, program_group in transport_df.groupby('Program Name', dropna=False):
        program_total = 0
        operational_total = 0
        substantive_categories = {}
        
        print(f"\n📋 PROGRAM: {program_name}")
        print(f"   Records: {len(program_group)}")
        
        for _, row in program_group.iterrows():
            account_name = row['Standard Account (Expense/Asset Name)']
            account_details = row['Account Details (Expense/Asset Details)']
            expenditure_category = row['Expenditure Category (Operating / Capital)']
            activity = row['Activity / Item']
            sub_item = row['Sub Item']
            amount = float(row['amount_dollars'])
            
            program_total += amount
            
            # Check if this should be consolidated as operational
            should_consolidate = should_consolidate_category(account_name, account_details)
            
            if should_consolidate:
                operational_total += amount
                print(f"   ✓ OPERATIONAL: ${amount:,.0f} - {account_name}")
            else:
                # This is substantive program spending
                if 'transfer payments' in account_name.lower() and pd.notna(account_details) and account_details != '':
                    category_name = account_details
                elif pd.notna(account_details) and account_details != '':
                    category_name = f"{account_name}: {account_details}"
                else:
                    category_name = account_name
                
                # Create unique key - THIS IS THE CRITICAL PART
                unique_key = f"{category_name}|{expenditure_category}|{activity}|{sub_item}"
                
                if unique_key in substantive_categories:
                    print(f"   🔄 MERGING: ${amount:,.0f} into existing {category_name}")
                    print(f"      Previous: ${substantive_categories[unique_key]['amount']:,.0f}")
                    substantive_categories[unique_key]['amount'] += amount
                    print(f"      New total: ${substantive_categories[unique_key]['amount']:,.0f}")
                else:
                    print(f"   ➕ SUBSTANTIVE: ${amount:,.0f} - {category_name}")
                    substantive_categories[unique_key] = {
                        'name': category_name,
                        'amount': amount,
                        'expenditure_category': expenditure_category,
                        'activity': activity,
                        'sub_item': sub_item
                    }
        
        print(f"   💰 Program total: ${program_total:,.0f}")
        print(f"   📊 Operational: ${operational_total:,.0f}")
        print(f"   📊 Substantive items: {len(substantive_categories)}")
        
        # Calculate substantive total
        substantive_total = sum(cat['amount'] for cat in substantive_categories.values())
        print(f"   📊 Substantive total: ${substantive_total:,.0f}")
        
        ministry_total += program_total
    
    print(f"\n💰 MINISTRY TOTAL AFTER AGGREGATION: ${ministry_total:,.0f}")
    
    # Compare with raw total
    raw_total = transport_df['amount_dollars'].sum()
    difference = ministry_total - raw_total
    
    print(f"💰 RAW TOTAL: ${raw_total:,.0f}")
    print(f"📊 DIFFERENCE: ${difference:,.0f}")
    
    if abs(difference) > 1000:
        print("❌ AGGREGATION ERROR DETECTED!")
    else:
        print("✅ Aggregation is correct")
    
    print("\n" + "=" * 80)

def should_consolidate_category(account_name: str, account_details: str) -> bool:
    """Determine if this should be consolidated into Operations (copied from create_compact_sankey.py)."""
    
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

if __name__ == "__main__":
    debug_transportation_aggregation() 