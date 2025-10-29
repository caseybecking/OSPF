#!/usr/bin/env python3
"""
Script to create multiple test paychecks for testing trends and analytics.
"""

import sys
import os
from datetime import date, datetime, timedelta
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from api.paycheck.models import PaycheckModel
from api.user.models import User

def create_multiple_test_paychecks():
    """Create multiple realistic test paychecks for trend analysis."""
    
    app = create_app()
    
    with app.app_context():
        # Find the existing user (Casey Becking)
        user = User.query.filter_by(email='me@user.com').first()
        
        if not user:
            print("User 'me@user.com' not found. Please run the create_user script first.")
            return
        
        # Create paychecks for the last 6 months (bi-weekly = ~13 paychecks)
        # Include both user (Self) and spouse paychecks to test employee_name functionality
        base_date = date(2025, 5, 1)  # Start in May
        paychecks_created = 0
        
        # Create paychecks for Self (user) - 13 bi-weekly paychecks
        for i in range(13):  # 13 bi-weekly paychecks over ~6 months
            pay_period_start = base_date + timedelta(days=i*14)
            pay_period_end = pay_period_start + timedelta(days=13)
            pay_date = pay_period_end + timedelta(days=3)  # Pay 3 days after period ends
            
            # Add some variation to make it realistic
            base_gross = 5000.00
            gross_variation = random.uniform(-100, 200)  # -$100 to +$200 variation
            gross_income = base_gross + gross_variation
            
            # Calculate taxes and deductions based on gross
            federal_tax = gross_income * 0.18  # ~18% federal
            state_tax = gross_income * 0.07    # ~7% state
            social_security_tax = gross_income * 0.062  # 6.2%
            medicare_tax = gross_income * 0.0145        # 1.45%
            other_taxes = random.uniform(40, 60)        # Variable other taxes
            
            # Pre-tax deductions
            health_insurance = 178.50 if i < 6 else 185.25  # Insurance increase mid-year
            dental_insurance = 24.00
            vision_insurance = 8.50
            voluntary_life_insurance = 15.75
            retirement_401k = gross_income * 0.10  # 10% to 401k
            
            # Calculate net pay
            total_taxes = federal_tax + state_tax + social_security_tax + medicare_tax + other_taxes
            total_pre_tax = health_insurance + dental_insurance + vision_insurance + voluntary_life_insurance + retirement_401k
            net_pay = gross_income - total_taxes - total_pre_tax
            
            # Add some bonus/overtime occasionally
            bonus = 0.0
            overtime_hours = 0.0
            overtime_rate = None
            
            if i % 4 == 0:  # Every 4th paycheck has some overtime
                overtime_hours = random.uniform(2, 8)
                overtime_rate = 93.75  # 1.5x base rate
                overtime_pay = overtime_hours * overtime_rate
                gross_income += overtime_pay
                net_pay += overtime_pay * 0.65  # Rough after-tax addition
            
            if i == 6:  # Mid-year bonus
                bonus = 2500.00
                gross_income += bonus
                net_pay += bonus * 0.60  # Rough after-tax bonus
            
            paycheck = PaycheckModel(
                user_id=user.id,
                employer='OSPF Technologies',
                employee_name='Self',  # User's own paychecks
                pay_period_start=pay_period_start,
                pay_period_end=pay_period_end,
                pay_date=pay_date,
                gross_income=round(gross_income, 2),
                net_pay=round(net_pay, 2),
                federal_tax=round(federal_tax, 2),
                state_tax=round(state_tax, 2),
                social_security_tax=round(social_security_tax, 2),
                medicare_tax=round(medicare_tax, 2),
                other_taxes=round(other_taxes, 2),
                health_insurance=health_insurance,
                dental_insurance=dental_insurance,
                vision_insurance=vision_insurance,
                voluntary_life_insurance=voluntary_life_insurance,
                retirement_401k=round(retirement_401k, 2),
                retirement_403b=0.00,
                retirement_ira=0.00,
                other_deductions=0.00,
                hours_worked=80.0 + overtime_hours,
                hourly_rate=62.50,
                overtime_hours=overtime_hours,
                overtime_rate=overtime_rate,
                bonus=bonus,
                commission=0.00,
                notes=f'Self paycheck #{i+1} - {"with overtime" if overtime_hours > 0 else ""}{"with bonus" if bonus > 0 else ""}regular pay period'
            )
            
            try:
                paycheck.save()
                paychecks_created += 1
                print(f"Created Self paycheck #{i+1}: {paycheck.pay_date} - ${paycheck.gross_income:,.2f} gross")
                
            except Exception as e:
                print(f"Error creating Self paycheck #{i+1}: {e}")
                db.session.rollback()
        
        # Create spouse paychecks (monthly - 6 paychecks)
        spouse_base_date = date(2025, 5, 15)  # Start mid-May
        for i in range(6):  # 6 monthly paychecks
            pay_period_start = spouse_base_date + timedelta(days=i*30)
            pay_period_end = pay_period_start + timedelta(days=29)
            pay_date = pay_period_end + timedelta(days=2)  # Pay 2 days after period ends
            
            # Spouse has different salary structure
            base_gross = 3800.00  # Lower base salary
            gross_variation = random.uniform(-50, 150)
            gross_income = base_gross + gross_variation
            
            # Calculate taxes and deductions for spouse
            federal_tax = gross_income * 0.16  # ~16% federal (lower bracket)
            state_tax = gross_income * 0.06    # ~6% state
            social_security_tax = gross_income * 0.062
            medicare_tax = gross_income * 0.0145
            other_taxes = random.uniform(25, 40)
            
            # Spouse's benefits
            health_insurance = 0.0  # Covered under user's plan
            dental_insurance = 0.0  # Covered under user's plan
            vision_insurance = 0.0  # Covered under user's plan
            voluntary_life_insurance = 12.50
            retirement_401k = gross_income * 0.08  # 8% to 401k
            
            total_taxes = federal_tax + state_tax + social_security_tax + medicare_tax + other_taxes
            total_deductions = voluntary_life_insurance + retirement_401k
            net_pay = gross_income - total_taxes - total_deductions
            
            # Occasional bonus for spouse
            bonus = 500.0 if i == 3 else 0.0  # Quarterly bonus
            if bonus > 0:
                gross_income += bonus
                net_pay += bonus * 0.65
            
            spouse_paycheck = PaycheckModel(
                user_id=user.id,
                employer='Remote Marketing Solutions',
                employee_name='Spouse',  # Spouse's paychecks
                pay_period_start=pay_period_start,
                pay_period_end=pay_period_end,
                pay_date=pay_date,
                gross_income=round(gross_income, 2),
                net_pay=round(net_pay, 2),
                federal_tax=round(federal_tax, 2),
                state_tax=round(state_tax, 2),
                social_security_tax=round(social_security_tax, 2),
                medicare_tax=round(medicare_tax, 2),
                other_taxes=round(other_taxes, 2),
                health_insurance=health_insurance,
                dental_insurance=dental_insurance,
                vision_insurance=vision_insurance,
                voluntary_life_insurance=voluntary_life_insurance,
                retirement_401k=round(retirement_401k, 2),
                retirement_403b=0.00,
                retirement_ira=0.00,
                other_deductions=0.00,
                hours_worked=160.0,  # Monthly hours
                hourly_rate=23.75,   # Lower hourly rate
                overtime_hours=0.0,
                overtime_rate=None,
                bonus=bonus,
                commission=0.00,
                notes=f'Spouse paycheck #{i+1} - {"with bonus" if bonus > 0 else ""}monthly salary'
            )
            
            try:
                spouse_paycheck.save()
                paychecks_created += 1
                print(f"Created Spouse paycheck #{i+1}: {spouse_paycheck.pay_date} - ${spouse_paycheck.gross_income:,.2f} gross")
                
            except Exception as e:
                print(f"Error creating Spouse paycheck #{i+1}: {e}")
                db.session.rollback()
        
        print(f"\nSuccessfully created {paychecks_created} test paychecks!")
        print(f"   User: {user.first_name} {user.last_name}")
        print(f"   Date range: {base_date} to {pay_date}")
        
        # Show breakdown by employee
        self_total = PaycheckModel.query.filter_by(user_id=user.id, employee_name='Self').with_entities(db.func.sum(PaycheckModel.gross_income)).scalar() or 0
        spouse_total = PaycheckModel.query.filter_by(user_id=user.id, employee_name='Spouse').with_entities(db.func.sum(PaycheckModel.gross_income)).scalar() or 0
        total_gross = self_total + spouse_total
        
        print(f"   Self gross income: ${self_total:,.2f}")
        print(f"   Spouse gross income: ${spouse_total:,.2f}")
        print(f"   Total household gross income: ${total_gross:,.2f}")
        
        print("\nYou can now test:")
        print("   • Paycheck listing page with multiple entries for both Self and Spouse")
        print("   • Individual paycheck details with tax calculations") 
        print("   • Trends and analytics with month-over-month data")
        print("   • Comparison features between different time periods")
        print("   • Employee-specific filtering (Self vs Spouse paychecks)")
        print("   • Household income tracking across multiple employees")

if __name__ == "__main__":
    create_multiple_test_paychecks()