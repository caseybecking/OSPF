#!/usr/bin/env python3
"""
Migration script to add original_statement, notes, and tags columns to transaction table
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
        # Add the new columns if they don't exist
        db.session.execute(text("""
            ALTER TABLE transaction
            ADD COLUMN IF NOT EXISTS original_statement VARCHAR(255);
        """))
        db.session.execute(text("""
            ALTER TABLE transaction
            ADD COLUMN IF NOT EXISTS notes TEXT;
        """))
        db.session.execute(text("""
            ALTER TABLE transaction
            ADD COLUMN IF NOT EXISTS tags VARCHAR(255);
        """))
        db.session.commit()
        print("✓ Successfully added original_statement, notes, and tags columns to transaction table")
    except Exception as e:
        print(f"✗ Error adding columns: {e}")
        db.session.rollback()
