#!/usr/bin/env python3
"""
Transform cleaned expense data into Sankey format with unique hierarchical names.

This script solves the duplicate name issue in the Sankey diagram by creating
unique node names based on the full hierarchical path.
"""

import pandas as pd
import json
import sys
from typing import Dict, List, Any

def create_hierarchical_name(row: pd.Series, level: str) -> str:
    """Create a unique hierarchical name based on the full path."""
    parts = []
    
    if level == 'ministry':
        return row['Ministry Name']
    
    parts.append(row['Ministry Name'])
    
    if level == 'program':
        return f"{parts[0]} → {row['Program Name']}"
    
    parts.append(row['Program Name'])
    
    if level == 'activity' and pd.notna(row['Activity / Item']) and row['Activity / Item'] != '':
        return f"{parts[0]} → {parts[1]} → {row['Activity / Item']}"
    
    if level == 'sub_item' and pd.notna(row['Sub Item']) and row['Sub Item'] != '':
        if pd.notna(row['Activity / Item']) and row['Activity / Item'] != '':
            return f"{parts[0]} → {parts[1]} → {row['Activity / Item']} → {row['Sub Item']}"
        else:
            return f"{parts[0]} → {parts[1]} → {row['Sub Item']}"
    
    if level == 'account':
        path_parts = [parts[0], parts[1]]
        
        if pd.notna(row['Activity / Item']) and row['Activity / Item'] != '':
            path_parts.append(row['Activity / Item'])
        
        if pd.notna(row['Sub Item']) and row['Sub Item'] != '':
            path_parts.append(row['Sub Item'])
        
        # Add the account name
        account_name = row['Standard Account (Expense/Asset Name)']
        if pd.notna(row['Account Details (Expense/Asset Details)']) and row['Account Details (Expense/Asset Details)'] != '':
            account_name = f"{account_name}: {row['Account Details (Expense/Asset Details)']}"
        
        path_parts.append(account_name)
        return ' → '.join(path_parts)
    
    return row['Ministry Name']  # fallback

def build_hierarchy_tree(df: pd.DataFrame) -> Dict[str, Any]:
    """Build a hierarchical tree structure for the Sankey diagram."""
    
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
                'name': create_hierarchical_name(program_group.iloc[0], 'program'),
                'children': []
            }
            
            # Group by activity within program
            activity_groups = program_group.groupby(['Activity / Item'], dropna=False)
            
            for activity_name, activity_group in activity_groups:
                # Handle cases where Activity / Item might be NaN or empty
                if pd.isna(activity_name) or activity_name == '' or activity_name == 'No Value':
                    # No activity level, group by sub item
                    sub_item_groups = activity_group.groupby(['Sub Item'], dropna=False)
                    
                    for sub_item_name, sub_item_group in sub_item_groups:
                        if pd.isna(sub_item_name) or sub_item_name == '' or sub_item_name == 'No Value':
                            # No sub item level, go directly to accounts
                            account_groups = sub_item_group.groupby(['Standard Account (Expense/Asset Name)', 'Account Details (Expense/Asset Details)'], dropna=False)
                            
                            for (account_name, account_details), account_group in account_groups:
                                account_node = {
                                    'name': create_hierarchical_name(account_group.iloc[0], 'account'),
                                    'amount': float(account_group['amount_dollars'].sum()) / 1e9  # Convert to billions
                                }
                                program_node['children'].append(account_node)
                        else:
                            # Has sub item level
                            sub_item_node = {
                                'name': create_hierarchical_name(sub_item_group.iloc[0], 'sub_item'),
                                'children': []
                            }
                            
                            account_groups = sub_item_group.groupby(['Standard Account (Expense/Asset Name)', 'Account Details (Expense/Asset Details)'], dropna=False)
                            
                            for (account_name, account_details), account_group in account_groups:
                                account_node = {
                                    'name': create_hierarchical_name(account_group.iloc[0], 'account'),
                                    'amount': float(account_group['amount_dollars'].sum()) / 1e9  # Convert to billions
                                }
                                sub_item_node['children'].append(account_node)
                            
                            program_node['children'].append(sub_item_node)
                else:
                    # Has activity level
                    activity_node = {
                        'name': create_hierarchical_name(activity_group.iloc[0], 'activity'),
                        'children': []
                    }
                    
                    # Group by sub item within activity
                    sub_item_groups = activity_group.groupby(['Sub Item'], dropna=False)
                    
                    for sub_item_name, sub_item_group in sub_item_groups:
                        if pd.isna(sub_item_name) or sub_item_name == '' or sub_item_name == 'No Value':
                            # No sub item level, go directly to accounts
                            account_groups = sub_item_group.groupby(['Standard Account (Expense/Asset Name)', 'Account Details (Expense/Asset Details)'], dropna=False)
                            
                            for (account_name, account_details), account_group in account_groups:
                                account_node = {
                                    'name': create_hierarchical_name(account_group.iloc[0], 'account'),
                                    'amount': float(account_group['amount_dollars'].sum()) / 1e9  # Convert to billions
                                }
                                activity_node['children'].append(account_node)
                        else:
                            # Has sub item level
                            sub_item_node = {
                                'name': create_hierarchical_name(sub_item_group.iloc[0], 'sub_item'),
                                'children': []
                            }
                            
                            account_groups = sub_item_group.groupby(['Standard Account (Expense/Asset Name)', 'Account Details (Expense/Asset Details)'], dropna=False)
                            
                            for (account_name, account_details), account_group in account_groups:
                                account_node = {
                                    'name': create_hierarchical_name(account_group.iloc[0], 'account'),
                                    'amount': float(account_group['amount_dollars'].sum()) / 1e9  # Convert to billions
                                }
                                sub_item_node['children'].append(account_node)
                            
                            activity_node['children'].append(sub_item_node)
                    
                    program_node['children'].append(activity_node)
            
            ministry_node['children'].append(program_node)
        
        ministries[ministry_name] = ministry_node
    
    return {
        'name': 'Spending',
        'children': list(ministries.values())
    }

def load_revenue_data() -> Dict[str, Any]:
    """Load and transform revenue data with hierarchical names."""
    df = pd.read_csv('clean_revenue_2024.csv')
    
    # Group by revenue type
    revenue_types = {}
    
    for revenue_type, type_group in df.groupby('revenue_type'):
        type_node = {
            'name': revenue_type,
            'children': []
        }
        
        # Group by revenue detail within type
        for revenue_detail, detail_group in type_group.groupby('revenue_detail'):
            if revenue_detail == revenue_type:
                # No sub-category, create direct amount node
                type_node['amount'] = float(detail_group['amount_dollars'].sum()) / 1e9
            else:
                # Has sub-category
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
    print("Loading expense data...")
    df = pd.read_csv('clean_expenses_2024.csv')
    
    print("Building spending hierarchy...")
    spending_data = build_hierarchy_tree(df)
    
    print("Loading revenue data...")
    revenue_data = load_revenue_data()
    
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
    
    print(f"Spending total: ${spending_total:.2f}B")
    print(f"Revenue total: ${revenue_total:.2f}B")
    
    # Create final Sankey data structure
    sankey_data = {
        'total': max(spending_total, revenue_total),
        'spending': spending_total,
        'revenue': revenue_total,
        'spending_data': spending_data,
        'revenue_data': revenue_data
    }
    
    # Write to file
    output_file = 'public/data/sankey_2024_fixed.json'
    print(f"Writing Sankey data to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(sankey_data, f, indent=2)
    
    print("✅ Sankey data transformation complete!")
    print(f"   • Revenue nodes: {count_nodes(revenue_data)}")
    print(f"   • Spending nodes: {count_nodes(spending_data)}")
    print(f"   • All nodes now have unique hierarchical names")

def count_nodes(node):
    """Count total nodes in tree."""
    count = 1
    if 'children' in node:
        for child in node['children']:
            count += count_nodes(child)
    return count

if __name__ == '__main__':
    main() 