#!/usr/bin/env python3
"""
Database migration script to add voluntary_life_insurance column to paycheck table.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def add_voluntary_life_insurance_column():
    """Add voluntary_life_insurance column to paycheck table."""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.engine.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='paycheck' 
                AND column_name='voluntary_life_insurance'
            """)
            
            if result.fetchone():
                print("Column 'voluntary_life_insurance' already exists in paycheck table")
                return
            
            # Add the new column
            db.engine.execute("""
                ALTER TABLE paycheck 
                ADD COLUMN voluntary_life_insurance DOUBLE PRECISION DEFAULT 0.0
            """)
            
            print("Successfully added voluntary_life_insurance column to paycheck table")
            
        except Exception as e:
            print(f"Error adding column: {e}")
            raise

if __name__ == "__main__":
    add_voluntary_life_insurance_column()