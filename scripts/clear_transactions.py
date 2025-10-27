#!/usr/bin/env python3
"""
Script to clear only the transactions table
"""
import os
import sys

# Change to project root directory (parent of scripts directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.insert(0, project_root)

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Delete all transactions
        result = db.session.execute(text("DELETE FROM transaction"))
        db.session.commit()
        print(f"✓ Cleared transaction table ({result.rowcount} rows)")
        print("\nTransactions table is now empty. Ready for fresh import!")

    except Exception as e:
        print(f"✗ Error clearing transactions: {e}")
        db.session.rollback()
