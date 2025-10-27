#!/usr/bin/env python3
"""
Convert Monarch categories JSON to CSV format for OSPF import
"""
import json
import csv
import os
import sys

# Change to project root directory (parent of scripts directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

# Read the JSON file
with open('data/monarch-categories.json', 'r') as f:
    data = json.load(f)

# Extract categories
categories = data['data']['categories']

# Create a set to track unique combinations (to avoid duplicates)
seen = set()
rows = []

for category in categories:
    # Skip disabled categories
    if category.get('isDisabled', False):
        continue

    category_name = category['name']
    group_name = category['group']['name']
    group_type = category['group']['type']

    # Capitalize first letter of type for consistency with existing data
    if group_type == 'income':
        type_name = 'Income'
    elif group_type == 'expense':
        type_name = 'Expense'
    elif group_type == 'transfer':
        type_name = 'Transfer'
    else:
        type_name = group_type.capitalize()

    # Create unique key
    key = (category_name, group_name, type_name)

    # Only add if not seen before
    if key not in seen:
        seen.add(key)
        rows.append({
            'categories': category_name,
            'categories_group': group_name,
            'categories_type': type_name
        })

# Sort by type, then group, then category
rows.sort(key=lambda x: (x['categories_type'], x['categories_group'], x['categories']))

# Write to CSV
with open('data/monarch-categories-data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['categories', 'categories_group', 'categories_type'])
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Successfully created monarch-categories-data.csv with {len(rows)} categories")
print(f"\nBreakdown:")
print(f"  - Income categories: {sum(1 for r in rows if r['categories_type'] == 'Income')}")
print(f"  - Expense categories: {sum(1 for r in rows if r['categories_type'] == 'Expense')}")
print(f"  - Transfer categories: {sum(1 for r in rows if r['categories_type'] == 'Transfer')}")
