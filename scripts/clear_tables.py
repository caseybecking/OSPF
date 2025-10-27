#!/usr/bin/env python3
"""
Script to clear all tables except user table
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
        # Clear tables in correct order (respecting foreign key constraints)
        print("Clearing tables...")

        # Delete transactions first (has foreign keys to categories and accounts)
        result = db.session.execute(text("DELETE FROM transaction"))
        print(f"✓ Cleared transaction table ({result.rowcount} rows)")

        # Delete accounts (has foreign key to institution)
        result = db.session.execute(text("DELETE FROM account"))
        print(f"✓ Cleared account table ({result.rowcount} rows)")

        # Delete institutions
        result = db.session.execute(text("DELETE FROM institution"))
        print(f"✓ Cleared institution table ({result.rowcount} rows)")

        # Delete categories (has foreign keys to categories_group and categories_type)
        result = db.session.execute(text("DELETE FROM categories"))
        print(f"✓ Cleared categories table ({result.rowcount} rows)")

        # Delete categories_group (has foreign key to categories_type)
        result = db.session.execute(text("DELETE FROM categories_group"))
        print(f"✓ Cleared categories_group table ({result.rowcount} rows)")

        # Delete categories_type
        result = db.session.execute(text("DELETE FROM categories_type"))
        print(f"✓ Cleared categories_type table ({result.rowcount} rows)")

        db.session.commit()
        print("\n✓ Successfully cleared all tables (except user table)")
        print("\nYou can now start fresh with importing categories and transactions!")

    except Exception as e:
        print(f"✗ Error clearing tables: {e}")
        db.session.rollback()
