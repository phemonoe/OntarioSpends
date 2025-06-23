#!/usr/bin/env python3
"""
Find the exact record that's being skipped in our Sankey processing.
We know 1 record out of 2295 is not being processed.
"""

import pandas as pd

def find_missing_record():
    print("🔍 FINDING THE MISSING RECORD")
    print("=" * 60)
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    print(f"Total records in CSV: {len(df)}")
    print(f"Total amount in CSV: ${df['amount_dollars'].sum():,.0f}")
    
    # Track which records get processed
    processed_records = set()
    total_records_processed = 0
    
    for ministry_name, ministry_group in df.groupby('Ministry Name'):
        for program_name, program_group in ministry_group.groupby('Program Name'):
            for idx, row in program_group.iterrows():
                processed_records.add(idx)
                total_records_processed += 1
    
    print(f"Records processed: {total_records_processed}")
    print(f"Records missing: {len(df) - total_records_processed}")
    
    # Find the missing record(s)
    all_indices = set(df.index)
    missing_indices = all_indices - processed_records
    
    print(f"\nMissing record indices: {missing_indices}")
    
    for idx in missing_indices:
        missing_record = df.loc[idx]
        amount = missing_record['amount_dollars']
        ministry = missing_record['Ministry Name']
        program = missing_record['Program Name']
        account = missing_record['Standard Account (Expense/Asset Name)']
        details = missing_record['Account Details (Expense/Asset Details)']
        
        print(f"\n🎯 FOUND THE MISSING RECORD:")
        print(f"   Index: {idx}")
        print(f"   Amount: ${amount:,.0f}")
        print(f"   Ministry: {ministry}")
        print(f"   Program: {program}")
        print(f"   Account: {account}")
        print(f"   Details: {details}")
        
        # Check if this record has any issues that would cause it to be skipped
        print(f"\n🔍 RECORD ANALYSIS:")
        print(f"   Ministry Name: '{ministry}' (type: {type(ministry)})")
        print(f"   Program Name: '{program}' (type: {type(program)})")
        print(f"   Is Ministry None/NaN: {pd.isna(ministry)}")
        print(f"   Is Program None/NaN: {pd.isna(program)}")
        print(f"   Ministry is empty string: {ministry == ''}")
        print(f"   Program is empty string: {program == ''}")
    
    # Also check for any records with problematic grouping keys
    print(f"\n🔍 CHECKING FOR PROBLEMATIC GROUPING KEYS:")
    
    # Check for NaN values in grouping columns
    ministry_nulls = df[df['Ministry Name'].isna()]
    program_nulls = df[df['Program Name'].isna()]
    
    print(f"   Records with null Ministry Name: {len(ministry_nulls)}")
    print(f"   Records with null Program Name: {len(program_nulls)}")
    
    if len(ministry_nulls) > 0:
        for idx, row in ministry_nulls.iterrows():
            print(f"      Index {idx}: Amount ${row['amount_dollars']:,.0f}")
    
    if len(program_nulls) > 0:
        for idx, row in program_nulls.iterrows():
            print(f"      Index {idx}: Amount ${row['amount_dollars']:,.0f}")
    
    # Test the exact iteration logic
    print(f"\n🧪 TESTING ITERATION LOGIC:")
    iteration_count = 0
    
    try:
        for ministry_name, ministry_group in df.groupby('Ministry Name'):
            if pd.isna(ministry_name):
                print(f"   Found NaN ministry group with {len(ministry_group)} records")
                for idx, row in ministry_group.iterrows():
                    print(f"      Record {idx}: ${row['amount_dollars']:,.0f}")
                continue
                
            for program_name, program_group in ministry_group.groupby('Program Name'):
                if pd.isna(program_name):
                    print(f"   Found NaN program in {ministry_name} with {len(program_group)} records")
                    for idx, row in program_group.iterrows():
                        print(f"      Record {idx}: ${row['amount_dollars']:,.0f}")
                    continue
                    
                for idx, row in program_group.iterrows():
                    iteration_count += 1
        
        print(f"   Total iterations completed: {iteration_count}")
        print(f"   Expected iterations: {len(df)}")
        print(f"   Missing iterations: {len(df) - iteration_count}")
        
    except Exception as e:
        print(f"   ❌ Error during iteration: {e}")

def check_groupby_behavior():
    """Check how pandas groupby handles NaN values"""
    
    print(f"\n{'='*60}")
    print(f"🔍 CHECKING GROUPBY BEHAVIOR WITH NaN VALUES")
    print(f"{'='*60}")
    
    df = pd.read_csv('clean_expenses_2024.csv')
    
    # Check the default behavior of groupby with NaN
    print(f"Default groupby behavior:")
    ministry_groups = df.groupby('Ministry Name', dropna=True)  # Default is dropna=True
    total_in_groups = sum(len(group) for _, group in ministry_groups)
    print(f"   Records in groups (dropna=True): {total_in_groups}")
    
    ministry_groups_keep_na = df.groupby('Ministry Name', dropna=False)
    total_in_groups_keep_na = sum(len(group) for _, group in ministry_groups_keep_na)
    print(f"   Records in groups (dropna=False): {total_in_groups_keep_na}")
    
    # Check for NaN values in Ministry Name
    nan_ministries = df[df['Ministry Name'].isna()]
    print(f"   Records with NaN Ministry Name: {len(nan_ministries)}")
    
    # Check for NaN values in Program Name
    nan_programs = df[df['Program Name'].isna()]
    print(f"   Records with NaN Program Name: {len(nan_programs)}")
    
    if len(nan_programs) > 0:
        print(f"\n📋 NaN Program Records:")
        for idx, row in nan_programs.iterrows():
            amount = row['amount_dollars']
            ministry = row['Ministry Name']
            account = row['Standard Account (Expense/Asset Name)']
            print(f"      Index {idx}: ${amount:,.0f} - {ministry} - {account}")

def main():
    find_missing_record()
    check_groupby_behavior()

if __name__ == "__main__":
    main() 