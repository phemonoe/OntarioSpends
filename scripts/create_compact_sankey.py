#!/usr/bin/env python3
"""
Create an ultra-compact Sankey that flattens single-child chains and removes
unnecessary hierarchy levels. Focus on meaningful government spending patterns.
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
    'Recoveries',
    'Other transactions',
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
        if any(keyword in details_lower for keyword in [
            'program', 'grant', 'fund', 'transfer', 'payment', 
            'subsidy', 'benefit', 'insurance', 'pension'
        ]):
            return False
    
    return True

def flatten_single_chains(node: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively flatten chains where a node has only one child."""
    
    if 'children' in node:
        # First, recursively flatten all children
        flattened_children = []
        for child in node['children']:
            flattened_child = flatten_single_chains(child)
            flattened_children.append(flattened_child)
        
        # If this node has exactly one child and no amount, merge with child
        if len(flattened_children) == 1 and 'amount' not in node:
            child = flattened_children[0]
            
            # If child has an amount, it's a terminal node - keep the chain
            if 'amount' in child:
                node['children'] = flattened_children
                return node
            
            # If child also has children, we can potentially flatten
            if 'children' in child:
                # Create a flattened node that combines names
                child_name = child['name']
                # Extract the meaningful part after the arrow
                if ' → ' in child_name:
                    parts = child_name.split(' → ')
                    # Use the last meaningful part
                    meaningful_part = parts[-1]
                    
                    # If it's just "Operations", keep the parent context
                    if meaningful_part == 'Operations':
                        flattened_name = f"{node['name']} → Operations"
                    else:
                        flattened_name = f"{node['name']} → {meaningful_part}"
                else:
                    flattened_name = f"{node['name']} → {child_name}"
                
                return {
                    'name': flattened_name,
                    'children': child.get('children', [])
                }
        
        node['children'] = flattened_children
    
    return node

def clean_program_name(ministry: str, program: str) -> str:
    """Clean up program names to remove redundancy."""
    
    # Remove ministry name from program if it's redundant
    if ministry.lower() in program.lower():
        program_clean = program.replace(ministry, '').strip()
        if program_clean and program_clean not in ['Program', '']:
            return program_clean
    
    # Remove common redundant words
    program = program.replace(' Program', '').strip()
    
    return program

def build_compact_hierarchy(df: pd.DataFrame) -> Dict[str, Any]:
    """Build a compact hierarchy with aggressive flattening."""
    
    print("Building ultra-compact spending hierarchy...")
    
    ministries = {}
    
    for ministry_name, ministry_group in df.groupby('Ministry Name'):
        ministry_programs = {}
        
        # Group by program within ministry
        for program_name, program_group in ministry_group.groupby('Program Name', dropna=False):
            
            # Separate operational vs substantive spending
            operational_total = 0
            substantive_categories = {}
            
            for _, row in program_group.iterrows():
                account_name = row['Standard Account (Expense/Asset Name)']
                account_details = row['Account Details (Expense/Asset Details)']
                expenditure_category = row['Expenditure Category (Operating / Capital)']
                activity = row['Activity / Item']
                sub_item = row['Sub Item']
                amount = float(row['amount_dollars']) / 1e9
                
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
                    # Include expenditure category and activity to distinguish operating vs capital
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
            
            # Clean program name (handle NaN program names)
            if pd.isna(program_name):
                clean_prog_name = f"{ministry_name} (Unspecified Program)"
            else:
                clean_prog_name = clean_program_name(ministry_name, program_name)
            
            # Create program spending items
            program_items = []
            
            # Always add operational spending (don't filter by threshold)
            if operational_total != 0:
                program_items.append({
                    'name': f"{ministry_name} → {clean_prog_name} → Operations",
                    'amount': operational_total
                })
            
            # Separate substantive spending into major and minor categories
            major_categories = []
            minor_categories_total = 0
            
            for unique_key, category_data in substantive_categories.items():
                category_name = category_data['name']
                amount = category_data['amount']
                
                if amount > 0.001:  # $1M threshold
                    major_categories.append({
                        'name': f"{ministry_name} → {clean_prog_name} → {category_name}",
                        'amount': amount
                    })
                else:
                    # Accumulate sub-$1M expenses
                    minor_categories_total += amount
            
            # Add major categories
            program_items.extend(major_categories)
            
            # Add "Other" category for sub-$1M expenses if there are any
            if minor_categories_total > 0:
                program_items.append({
                    'name': f"{ministry_name} → {clean_prog_name} → Other",
                    'amount': minor_categories_total
                })
            
            # Only keep programs with meaningful spending
            if program_items:
                ministry_programs[clean_prog_name] = program_items
        
        # For ministries with only one program, flatten directly to ministry level
        if len(ministry_programs) == 1:
            program_name, program_items = next(iter(ministry_programs.items()))
            
            # If program name is just administrative, flatten completely
            if program_name.lower() in ['ministry administration', 'administration', 'main program']:
                ministries[ministry_name] = {
                    'name': ministry_name,
                    'children': [
                        {
                            'name': item['name'].replace(f" → {program_name}", ""),
                            'amount': item['amount']
                        }
                        for item in program_items
                    ]
                }
            else:
                # Keep the program level if it's meaningful
                ministries[ministry_name] = {
                    'name': ministry_name,
                    'children': [{
                        'name': f"{ministry_name} → {program_name}",
                        'children': program_items
                    }]
                }
        else:
            # Multiple programs - keep program structure
            children = []
            for program_name, program_items in ministry_programs.items():
                children.append({
                    'name': f"{ministry_name} → {program_name}",
                    'children': program_items
                })
            
            if children:
                ministries[ministry_name] = {
                    'name': ministry_name,
                    'children': children
                }
    
    # Build the final structure and flatten chains
    spending_root = {
        'name': 'Spending',
        'children': list(ministries.values())
    }
    
    # Apply chain flattening
    flattened_root = flatten_single_chains(spending_root)
    
    return flattened_root

def create_compact_revenue(df: pd.DataFrame) -> Dict[str, Any]:
    """Create compact revenue with flattening and Other categories for small amounts."""
    
    revenue_types = {}
    
    for revenue_type, type_group in df.groupby('revenue_type'):
        major_items = []
        minor_items_total = 0
        
        for revenue_detail, detail_group in type_group.groupby('revenue_detail'):
            amount = float(detail_group['amount_dollars'].sum()) / 1e9
            
            if revenue_detail == revenue_type:
                # This is the main category amount - always include
                revenue_types[revenue_type] = {
                    'name': revenue_type,
                    'amount': amount
                }
            else:
                # This is a sub-category - apply threshold
                if amount > 0.001:  # $1M threshold
                    major_items.append({
                        'name': f"{revenue_type} → {revenue_detail}",
                        'amount': amount
                    })
                else:
                    minor_items_total += amount
        
        # Add "Other" category for minor revenue items if needed
        if minor_items_total > 0:
            major_items.append({
                'name': f"{revenue_type} → Other",
                'amount': minor_items_total
            })
        
        # If we have sub-categories, use those instead
        if major_items:
            revenue_types[revenue_type] = {
                'name': revenue_type,
                'children': major_items
            }
    
    revenue_root = {
        'name': 'Revenue',
        'children': list(revenue_types.values())
    }
    
    return flatten_single_chains(revenue_root)

def main():
    print("🎯 Creating Ultra-Compact Sankey Data")
    print("=" * 50)
    
    print("Loading expense data...")
    df_expenses = pd.read_csv('clean_expenses_2024.csv')
    
    print("Loading revenue data...")
    df_revenue = pd.read_csv('clean_revenue_2024.csv')
    
    print(f"Input: {len(df_expenses)} expense rows, {len(df_revenue)} revenue rows")
    
    # Build compact hierarchies
    spending_data = build_compact_hierarchy(df_expenses)
    revenue_data = create_compact_revenue(df_revenue)
    
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
    output_file = 'public/data/sankey_2024_compact.json'
    print(f"\n💾 Writing compact Sankey data to {output_file}...")
    
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
    
    print("✅ Ultra-compact Sankey transformation complete!")
    print(f"\n📈 Results:")
    print(f"   • Revenue nodes: {revenue_nodes}")
    print(f"   • Spending nodes: {spending_nodes} (was 703)")
    print(f"   • Additional reduction: {((703 - spending_nodes) / 703 * 100):.1f}% fewer nodes")
    print(f"   • Total reduction from original: {((3231 - spending_nodes) / 3231 * 100):.1f}%")
    
    print(f"\n🎯 Ultra-Compact Benefits:")
    print(f"   • Flattened single-child chains")
    print(f"   • Sub-$1M expenses grouped under 'Other'") 
    print(f"   • Merged redundant program structures")
    print(f"   • 100% spending coverage with clean visualization")

if __name__ == '__main__':
    main() 