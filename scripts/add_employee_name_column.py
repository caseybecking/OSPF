#!/usr/bin/env python3
"""
Migration script to add employee_name column to paychecks table
"""

import sys
import os

# Add the parent directory to sys.path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def add_employee_name_column():
    """Add employee_name column to paychecks table with default value 'Self'"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'paycheck' 
                    AND column_name = 'employee_name'
                """))
                
                if result.fetchone():
                    print("employee_name column already exists in paycheck table")
                    return
                
                # Add the column
                print("Adding employee_name column to paycheck table...")
                conn.execute(text('ALTER TABLE paycheck ADD COLUMN employee_name VARCHAR(100) DEFAULT \'Self\' NOT NULL'))
                conn.commit()
                
                # Update any existing NULL values to 'Self' (shouldn't be any due to DEFAULT, but just in case)
                result = conn.execute(text('UPDATE paycheck SET employee_name = \'Self\' WHERE employee_name IS NULL'))
                conn.commit()
                print(f"Updated {result.rowcount} records with default employee_name")
                
                print("Successfully added employee_name column to paycheck table")
            
        except Exception as e:
            print(f"Error adding employee_name column: {str(e)}")
            raise

if __name__ == '__main__':
    add_employee_name_column()