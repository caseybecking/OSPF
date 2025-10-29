#!/usr/bin/env python3
"""
Migration script to create the paycheck table for tracking detailed paycheck information
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
        print("Creating paycheck table...")
        
        # Create the paycheck table
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS paycheck (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT NOT NULL REFERENCES "user"(id),
                employer VARCHAR(255) NOT NULL,
                pay_period_start DATE NOT NULL,
                pay_period_end DATE NOT NULL,
                pay_date DATE NOT NULL,
                gross_income FLOAT NOT NULL,
                net_pay FLOAT NOT NULL,
                federal_tax FLOAT DEFAULT 0.0,
                state_tax FLOAT DEFAULT 0.0,
                social_security_tax FLOAT DEFAULT 0.0,
                medicare_tax FLOAT DEFAULT 0.0,
                other_taxes FLOAT DEFAULT 0.0,
                health_insurance FLOAT DEFAULT 0.0,
                dental_insurance FLOAT DEFAULT 0.0,
                vision_insurance FLOAT DEFAULT 0.0,
                retirement_401k FLOAT DEFAULT 0.0,
                retirement_403b FLOAT DEFAULT 0.0,
                retirement_ira FLOAT DEFAULT 0.0,
                other_deductions FLOAT DEFAULT 0.0,
                hours_worked FLOAT,
                hourly_rate FLOAT,
                overtime_hours FLOAT DEFAULT 0.0,
                overtime_rate FLOAT,
                bonus FLOAT DEFAULT 0.0,
                commission FLOAT DEFAULT 0.0,
                notes TEXT
            );
        """))
        
        print("✓ Created paycheck table")
        
        # Create indexes for better performance
        print("Creating indexes...")
        
        # Index on user_id for filtering user's paychecks
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_paycheck_user_id 
            ON paycheck(user_id);
        """))
        print("✓ Created index on user_id")
        
        # Index on pay_date for date range queries and sorting
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_paycheck_pay_date 
            ON paycheck(pay_date);
        """))
        print("✓ Created index on pay_date")
        
        # Index on employer for filtering by employer
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_paycheck_employer 
            ON paycheck(employer);
        """))
        print("✓ Created index on employer")
        
        # Composite index for user-specific date range queries (most common query pattern)
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_paycheck_user_date 
            ON paycheck(user_id, pay_date DESC);
        """))
        print("✓ Created composite index on user_id and pay_date")
        
        # Index for analytics queries on gross income
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_paycheck_user_gross 
            ON paycheck(user_id, gross_income);
        """))
        print("✓ Created index on user_id and gross_income")
        
        # Create trigger to automatically update the updated_at timestamp
        print("Creating update trigger...")
        db.session.execute(text("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        db.session.execute(text("""
            DROP TRIGGER IF EXISTS update_paycheck_updated_at ON paycheck;
            CREATE TRIGGER update_paycheck_updated_at
                BEFORE UPDATE ON paycheck
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """))
        print("✓ Created update trigger for updated_at timestamp")
        
        # Add constraints (check if they exist first to avoid errors)
        print("Adding data integrity constraints...")
        
        # Check and add constraint to ensure pay_period_start <= pay_period_end
        try:
            db.session.execute(text("""
                ALTER TABLE paycheck 
                ADD CONSTRAINT chk_paycheck_period_dates 
                CHECK (pay_period_start <= pay_period_end);
            """))
            print("✓ Added constraint to ensure valid pay period dates")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Constraint for valid pay period dates already exists")
            else:
                print(f"⚠ Warning: Could not add period dates constraint: {e}")
        
        # Check and add constraint to ensure positive gross income and net pay
        try:
            db.session.execute(text("""
                ALTER TABLE paycheck 
                ADD CONSTRAINT chk_paycheck_positive_amounts 
                CHECK (gross_income >= 0 AND net_pay >= 0);
            """))
            print("✓ Added constraint to ensure positive income amounts")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Constraint for positive amounts already exists")
            else:
                print(f"⚠ Warning: Could not add positive amounts constraint: {e}")
        
        # Check and add constraint to ensure net pay doesn't exceed gross income
        try:
            db.session.execute(text("""
                ALTER TABLE paycheck 
                ADD CONSTRAINT chk_paycheck_net_vs_gross 
                CHECK (net_pay <= gross_income);
            """))
            print("✓ Added constraint to ensure net pay doesn't exceed gross income")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Constraint for net vs gross already exists")
            else:
                print(f"⚠ Warning: Could not add net vs gross constraint: {e}")
        
        # Commit all changes
        db.session.commit()
        print("\nPaycheck table migration completed successfully!")
        print("\nTable structure:")
        print("- Basic Info: employer, pay_period_start, pay_period_end, pay_date")
        print("- Income: gross_income, net_pay, bonus, commission")
        print("- Taxes: federal_tax, state_tax, social_security_tax, medicare_tax, other_taxes")
        print("- Insurance: health_insurance, dental_insurance, vision_insurance")
        print("- Retirement: retirement_401k, retirement_403b, retirement_ira")
        print("- Work Details: hours_worked, hourly_rate, overtime_hours, overtime_rate")
        print("- Other: other_deductions, notes")
        print("\nIndexes created for optimal performance on:")
        print("- User-specific queries")
        print("- Date range filtering and sorting")
        print("- Employer filtering")
        print("- Analytics queries")
        print("\nConstraints added for data integrity:")
        print("- Valid pay period date ranges")
        print("- Positive income amounts")
        print("- Net pay not exceeding gross income")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        db.session.rollback()
        sys.exit(1)