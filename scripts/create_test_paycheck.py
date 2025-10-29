#!/usr/bin/env python3
"""
Script to create a realistic test paycheck for testing the paycheck details view.
"""

import sys
import os
from datetime import date, datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from api.paycheck.models import PaycheckModel
from api.user.models import User

def create_test_paycheck():
    """Create a realistic test paycheck for the existing user."""
    
    app = create_app()
    
    with app.app_context():
        # Find the existing user (Casey Becking)
        user = User.query.filter_by(email='me@caseybecking.com').first()
        
        if not user:
            print("User 'me@caseybecking.com' not found. Please run the create_user script first.")
            return
        
        # Create a realistic paycheck with comprehensive data
        # Based on a $130,000 annual salary (bi-weekly = ~$5000 gross)
        
        pay_period_start = date(2025, 10, 14)  # Recent pay period
        pay_period_end = date(2025, 10, 27)
        pay_date = date(2025, 10, 30)
        
        # Calculate deductions first
        gross_income = 5000.00
        
        # Taxes
        federal_tax = 752.50    # ~18.5% effective federal rate
        state_tax = 285.00      # ~7% effective state rate (California example)
        social_security_tax = 310.00  # 6.2% of gross
        medicare_tax = 72.50    # 1.45% of gross
        other_taxes = 45.00     # State disability insurance, etc.
        
        # Pre-tax Deductions (reduce taxable income)
        health_insurance = 178.50      # Medical premium
        dental_insurance = 24.00       # Dental premium  
        vision_insurance = 8.50        # Vision premium
        voluntary_life_insurance = 15.75  # Life insurance premium
        retirement_401k = 500.00       # 10% of gross to 401k
        retirement_403b = 0.00         # Not applicable
        retirement_ira = 0.00          # Using 401k instead
        
        # Other deductions (post-tax)
        other_deductions = 0.00
        
        # Calculate net pay: gross - all deductions
        total_deductions = (federal_tax + state_tax + social_security_tax + medicare_tax + 
                          other_taxes + health_insurance + dental_insurance + vision_insurance + 
                          voluntary_life_insurance + retirement_401k + retirement_403b + 
                          retirement_ira + other_deductions)
        calculated_net_pay = gross_income - total_deductions

        paycheck = PaycheckModel(
            user_id=user.id,
            employer='OSPF Technologies',
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=pay_date,
            
            # Income
            gross_income=gross_income,
            net_pay=calculated_net_pay,  # Calculated net pay
            
            # Federal and State Taxes (on taxable income)
            federal_tax=federal_tax,
            state_tax=state_tax,
            social_security_tax=social_security_tax,
            medicare_tax=medicare_tax,
            other_taxes=other_taxes,
            
            # Pre-tax Deductions (reduce taxable income)
            health_insurance=health_insurance,
            dental_insurance=dental_insurance,
            vision_insurance=vision_insurance,
            voluntary_life_insurance=voluntary_life_insurance,
            retirement_401k=retirement_401k,
            retirement_403b=retirement_403b,
            retirement_ira=retirement_ira,
            
            # Other deductions (post-tax)
            other_deductions=other_deductions,
            
            # Work details
            hours_worked=80.0,      # Standard bi-weekly hours
            hourly_rate=62.50,      # $130k annual / 2080 hours
            overtime_hours=0.0,     # No overtime this period
            overtime_rate=None,     # Would be $93.75 (1.5x)
            
            # Additional compensation
            bonus=0.00,            # No bonus this period
            commission=0.00,       # Not commission-based
            
            notes='Regular bi-weekly paycheck with standard deductions. Testing new tax rate calculations based on taxable income.'
        )
        
        try:
            paycheck.save()
            
            print("Test paycheck created successfully!")
            print(f"   Paycheck ID: {paycheck.id}")
            print(f"   User: {user.first_name} {user.last_name} ({user.email})")
            print(f"   Employer: {paycheck.employer}")
            print(f"   Pay Period: {paycheck.pay_period_start} to {paycheck.pay_period_end}")
            print(f"   Pay Date: {paycheck.pay_date}")
            print(f"   Gross Income: ${paycheck.gross_income:,.2f}")
            print(f"   Net Pay: ${paycheck.net_pay:,.2f}")
            print()
            print("Calculated Tax Rates (based on taxable income):")
            print(f"   Taxable Income: ${paycheck.taxable_income:,.2f}")
            print(f"   Effective Tax Rate: {paycheck.effective_tax_rate:.2f}%")
            print(f"   Federal Tax Rate: {paycheck.federal_tax_rate:.2f}%")
            print(f"   State Tax Rate: {paycheck.state_tax_rate:.2f}%")
            print(f"   Retirement Rate: {paycheck.retirement_contribution_rate:.2f}%")
            print()
            print("🌐 You can now view this paycheck in the web interface!")
            print("   Navigate to: /paycheck to see the list")
            print(f"   Direct link: /paycheck/{paycheck.id} for details")
            
        except Exception as e:
            print(f"Error creating paycheck: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_paycheck()