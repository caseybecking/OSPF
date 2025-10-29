#!/usr/bin/env python3
"""
Simple script to add voluntary_life_insurance column if it doesn't exist.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app import create_app, db

def main():
    app = create_app()
    with app.app_context():
        try:
            # Test if column exists
            result = db.session.execute(text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name='paycheck' AND column_name='voluntary_life_insurance'"))
            count = result.scalar()
            
            if count > 0:
                print("voluntary_life_insurance column already exists")
                return
            
            # Add the column
            print("Adding voluntary_life_insurance column...")
            db.session.execute(text("ALTER TABLE paycheck ADD COLUMN voluntary_life_insurance FLOAT DEFAULT 0.0"))
            db.session.commit()
            print("voluntary_life_insurance column added successfully")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    main()