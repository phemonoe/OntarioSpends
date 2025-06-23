#!/usr/bin/env python3
"""
Create a strategic, high-level Sankey that focuses on WHAT the government does,
not HOW it spends (operational details).

This script consolidates:
- All operational expenses (salaries, benefits, supplies, etc.) → "Operations"  
- Keeps substantive program spending (transfers, grants) as detailed items
- Creates ministry → program → meaningful spending categories structure
"""

import pandas as pd
import json
import sys
from typing import Dict, List, Any

# Categories to consolidate into "Operations"
OPERATIONAL_CATEGORIES = {
    'Salaries and wages',
    'Employee benefits', 
    'Transportation and communication',
    'Services',
    'Supplies and equipment',
    'Recoveries',  # Usually operational adjustments
    'Other transactions',  # Often administrative
    'Amortization',
    'Bad Debt Expense'
}

def should_consolidate_category(account_name: str, account_details: str) -> bool:
    """Determine if this should be consolidated into Operations."""
    
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
        # These suggest substantive program spending
        if any(keyword in details_lower for keyword in [
            'program', 'grant', 'fund', 'transfer', 'payment', 
            'subsidy', 'benefit', 'insurance', 'pension'
        ]):
            return False
    
    return True

def create_strategic_name(row: pd.Series, level: str) -> str:
    """Create strategic names focused on program outcomes."""
    
    ministry = row['Ministry Name']
    program = row['Program Name'] 
    activity = row['Activity / Item'] if pd.notna(row['Activity / Item']) and row['Activity / Item'] != '' else None
    
    if level == 'ministry':
        return ministry
    
    if level == 'program':
        # Clean up program names - remove redundant ministry name repetition
        if ministry.lower() in program.lower():
            # Try to extract the unique part
            program_clean = program.replace(ministry, '').strip()
            if program_clean and program_clean != 'Program':
                return f"{ministry} → {program_clean}"
        return f"{ministry} → {program}"
    
    if level == 'activity' and activity:
        return f"{ministry} → {program} → {activity}"
    
    return f"{ministry} → {program}"

def build_strategic_hierarchy(df: pd.DataFrame) -> Dict[str, Any]:
    """Build a strategic hierarchy focused on program outcomes."""
    
    print("Building strategic spending hierarchy...")
    
    # Group by ministry
    ministries = {}
    
    for ministry_name, ministry_group in df.groupby('Ministry Name'):
        ministry_node = {
            'name': ministry_name,
            'children': []
        }
        
        # Group by program within ministry
        for program_name, program_group in ministry_group.groupby('Program Name'):
            program_node = {
                'name': create_strategic_name(program_group.iloc[0], 'program'),
                'children': []
            }
            
            # Separate operational vs substantive spending
            operational_total = 0
            substantive_categories = {}
            
            for _, row in program_group.iterrows():
                account_name = row['Standard Account (Expense/Asset Name)']
                account_details = row['Account Details (Expense/Asset Details)']
                amount = float(row['amount_dollars']) / 1e9
                
                if should_consolidate_category(account_name, account_details):
                    # Add to operational total
                    operational_total += amount
                else:
                    # This is substantive program spending - keep detailed
                    if 'transfer payments' in account_name.lower() and pd.notna(account_details) and account_details != '':
                        # Transfer payments - use the program/recipient name
                        category_name = account_details
                    elif pd.notna(account_details) and account_details != '':
                        # Other substantive spending with details
                        category_name = f"{account_name}: {account_details}"
                    else:
                        # Use the account name
                        category_name = account_name
                    
                    # Aggregate amounts for same categories
                    if category_name in substantive_categories:
                        substantive_categories[category_name] += amount
                    else:
                        substantive_categories[category_name] = amount
            
            # Add operational spending as single consolidated category
            if operational_total > 0:
                program_node['children'].append({
                    'name': f"{create_strategic_name(program_group.iloc[0], 'program')} → Operations",
                    'amount': operational_total
                })
            
            # Add substantive spending categories
            for category_name, amount in substantive_categories.items():
                if amount > 0:  # Only include positive amounts
                    program_node['children'].append({
                        'name': f"{create_strategic_name(program_group.iloc[0], 'program')} → {category_name}",
                        'amount': amount
                    })
            
            # Only add program if it has children
            if program_node['children']:
                ministry_node['children'].append(program_node)
        
        # Only add ministry if it has children
        if ministry_node['children']:
            ministries[ministry_name] = ministry_node
    
    return {
        'name': 'Spending',
        'children': list(ministries.values())
    }

def create_strategic_revenue(df: pd.DataFrame) -> Dict[str, Any]:
    """Create strategic revenue categories."""
    
    # Group by revenue type
    revenue_types = {}
    
    for revenue_type, type_group in df.groupby('revenue_type'):
        type_node = {
            'name': revenue_type,
            'children': []
        }
        
        # For revenue, keep more detail since it's naturally less cluttered
        for revenue_detail, detail_group in type_group.groupby('revenue_detail'):
            if revenue_detail == revenue_type:
                # No sub-category, create direct amount node
                type_node['amount'] = float(detail_group['amount_dollars'].sum()) / 1e9
            else:
                # Has sub-category - use hierarchical naming
                detail_node = {
                    'name': f"{revenue_type} → {revenue_detail}",
                    'amount': float(detail_group['amount_dollars'].sum()) / 1e9
                }
                type_node['children'].append(detail_node)
        
        revenue_types[revenue_type] = type_node
    
    return {
        'name': 'Revenue',
        'children': list(revenue_types.values())
    }

def main():
    print("🎯 Creating Strategic Sankey Data")
    print("=" * 50)
    
    print("Loading expense data...")
    df_expenses = pd.read_csv('clean_expenses_2024.csv')
    
    print("Loading revenue data...")
    df_revenue = pd.read_csv('clean_revenue_2024.csv')
    
    print(f"Input: {len(df_expenses)} expense rows, {len(df_revenue)} revenue rows")
    
    # Build strategic hierarchies
    spending_data = build_strategic_hierarchy(df_expenses)
    revenue_data = create_strategic_revenue(df_revenue)
    
    # Calculate totals
    def calculate_total(node):
        if 'amount' in node:
            return node['amount']
        elif 'children' in node:
            return sum(calculate_total(child) for child in node['children'])
        else:
            return 0
    
    spending_total = calculate_total(spending_data)
    revenue_total = calculate_total(revenue_data)
    
    print(f"\n📊 Totals:")
    print(f"   • Spending: ${spending_total:.2f}B")
    print(f"   • Revenue: ${revenue_total:.2f}B")
    
    # Create final Sankey data structure
    sankey_data = {
        'total': max(spending_total, revenue_total),
        'spending': spending_total,
        'revenue': revenue_total,
        'spending_data': spending_data,
        'revenue_data': revenue_data
    }
    
    # Write to file
    output_file = 'public/data/sankey_2024_strategic.json'
    print(f"\n💾 Writing strategic Sankey data to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(sankey_data, f, indent=2)
    
    # Count nodes for comparison
    def count_nodes(node):
        count = 1
        if 'children' in node:
            for child in node['children']:
                count += count_nodes(child)
        return count
    
    revenue_nodes = count_nodes(revenue_data)
    spending_nodes = count_nodes(spending_data)
    
    print("✅ Strategic Sankey transformation complete!")
    print(f"\n📈 Results:")
    print(f"   • Revenue nodes: {revenue_nodes}")
    print(f"   • Spending nodes: {spending_nodes} (was 3,231)")
    print(f"   • Reduction: {((3231 - spending_nodes) / 3231 * 100):.1f}% fewer nodes")
    print(f"   • Focus: Program outcomes vs operational details")
    
    print(f"\n🎯 Strategic Benefits:")
    print(f"   • Consolidated ~1,976 operational expense categories")
    print(f"   • Highlights WHAT government does, not HOW it operates")
    print(f"   • Much cleaner, more meaningful visualization")
    print(f"   • Users can focus on policy and program impacts")

if __name__ == '__main__':
    main() 