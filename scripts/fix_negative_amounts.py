#!/usr/bin/env python3
"""
Fix negative amount handling and regenerate clean data.
Negative amounts represent recoveries and should be properly netted.
"""

import pandas as pd
import json

def analyze_negative_amounts():
    print("🔍 ANALYZING NEGATIVE AMOUNTS")
    print("=" * 60)
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    negative_df = df[df['amount_dollars'] < 0]
    positive_df = df[df['amount_dollars'] >= 0]
    
    print(f"Total records: {len(df)}")
    print(f"Negative records: {len(negative_df)}")
    print(f"Positive records: {len(positive_df)}")
    
    print(f"\nAmounts:")
    print(f"Total amount (including negatives): ${df['amount_dollars'].sum():,.0f}")
    print(f"Positive amounts: ${positive_df['amount_dollars'].sum():,.0f}")
    print(f"Negative amounts: ${negative_df['amount_dollars'].sum():,.0f}")
    print(f"Net amount: ${positive_df['amount_dollars'].sum() + negative_df['amount_dollars'].sum():,.0f}")
    
    # Check what kinds of negative amounts we have
    print(f"\nNegative amounts by account type:")
    neg_by_account = negative_df.groupby('Standard Account (Expense/Asset Name)')['amount_dollars'].agg(['count', 'sum']).sort_values('sum')
    
    for account, data in neg_by_account.iterrows():
        print(f"   {account}: {data['count']} records, ${data['sum']:,.0f}")
    
    # Check if negatives are mostly recoveries
    recoveries = negative_df[negative_df['Standard Account (Expense/Asset Name)'].str.contains('Recoveries', case=False, na=False)]
    print(f"\nRecoveries:")
    print(f"   Records: {len(recoveries)}")
    print(f"   Amount: ${recoveries['amount_dollars'].sum():,.0f}")
    print(f"   Percentage of negatives: {len(recoveries)/len(negative_df)*100:.1f}%")

def check_ministry_netting():
    """Check if we should net negative amounts within each ministry/program"""
    
    print(f"\n{'='*60}")
    print(f"🔍 CHECKING MINISTRY-LEVEL NETTING")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Compare gross vs net totals by ministry
    print(f"{'Ministry':<40} {'Gross':<12} {'Net':<12} {'Difference':<12}")
    print(f"{'-'*80}")
    
    for ministry, ministry_df in df.groupby('Ministry Name'):
        gross_total = ministry_df[ministry_df['amount_dollars'] >= 0]['amount_dollars'].sum()
        net_total = ministry_df['amount_dollars'].sum()
        difference = gross_total - net_total
        
        if difference > 1e6:  # Only show significant differences
            print(f"{ministry:<40} ${gross_total/1e9:>6.2f}B  ${net_total/1e9:>6.2f}B  ${difference/1e6:>6.1f}M")

def create_fixed_data():
    """Create a version of the data with proper negative amount handling"""
    
    print(f"\n{'='*60}")
    print(f"🛠️  CREATING FIXED DATA")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    print(f"Original data:")
    print(f"   Total amount: ${df['amount_dollars'].sum():,.0f}")
    print(f"   Records: {len(df)}")
    
    # Option 1: Keep all data as-is (including negatives)
    # This is actually correct - negatives should reduce total spending
    
    # Option 2: Separate analysis to see if we should exclude certain negatives
    recoveries = df[df['Standard Account (Expense/Asset Name)'].str.contains('Recoveries', case=False, na=False)]
    non_recoveries = df[~df['Standard Account (Expense/Asset Name)'].str.contains('Recoveries', case=False, na=False)]
    
    print(f"\nBreakdown:")
    print(f"   Non-recovery spending: ${non_recoveries['amount_dollars'].sum():,.0f}")
    print(f"   Recoveries: ${recoveries['amount_dollars'].sum():,.0f}")
    print(f"   Net total: ${df['amount_dollars'].sum():,.0f}")
    
    # The data is actually correct as-is. The issue is our Sankey generation
    # might not be handling the negatives properly.
    
    return df

def test_sankey_with_negatives():
    """Test what happens when we process negatives correctly in Sankey"""
    
    print(f"\n{'='*60}")
    print(f"🧪 TESTING SANKEY WITH NEGATIVE HANDLING")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Test our consolidation logic with negatives
    total_operational = 0
    total_substantive = 0
    
    for _, row in df.iterrows():
        account_name = row['Standard Account (Expense/Asset Name)']
        account_details = row['Account Details (Expense/Asset Details)']
        amount = row['amount_dollars']
        
        if should_consolidate_category(account_name, account_details):
            total_operational += amount
        else:
            total_substantive += amount
    
    print(f"With negative amounts included:")
    print(f"   Operational total: ${total_operational:,.0f}")
    print(f"   Substantive total: ${total_substantive:,.0f}")
    print(f"   Grand total: ${total_operational + total_substantive:,.0f}")
    print(f"   Expected total: ${df['amount_dollars'].sum():,.0f}")
    print(f"   Difference: ${df['amount_dollars'].sum() - (total_operational + total_substantive):,.0f}")

def should_consolidate_category(account_name: str, account_details: str) -> bool:
    """Same logic as in our compact sankey script"""
    OPERATIONAL_CATEGORIES = {
        'Salaries and wages',
        'Employee benefits', 
        'Transportation and communication',
        'Services',
        'Supplies and equipment',
        'Recoveries',  # This should be operational!
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
    analyze_negative_amounts()
    check_ministry_netting()
    create_fixed_data()
    test_sankey_with_negatives()
    
    print(f"\n🎯 CONCLUSION:")
    print(f"The negative amounts are legitimate recoveries that should REDUCE net spending.")
    print(f"Our Sankey generation should handle them correctly.")
    print(f"The issue may be in how we're calculating or comparing totals.")

if __name__ == "__main__":
    main() 