#!/usr/bin/env python3
"""
Script to demonstrate net pay calculation and validate existing paychecks.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from api.paycheck.models import PaycheckModel
from api.user.models import User

def validate_net_pay_calculations():
    """Validate and show net pay calculations for all paychecks."""
    
    app = create_app()
    
    with app.app_context():
        # Find the user
        user = User.query.filter_by(email='me@user.com').first()
        
        if not user:
            print("User 'me@user.com' not found.")
            return
        
        # Get all paychecks for the user
        paychecks = PaycheckModel.query.filter_by(user_id=user.id).order_by(PaycheckModel.pay_date.desc()).all()
        
        if not paychecks:
            print("ℹ️  No paychecks found for this user.")
            return
        
        print(f"Net Pay Calculation Analysis for {user.first_name} {user.last_name}")
        print("=" * 80)
        
        for i, paycheck in enumerate(paychecks, 1):
            print(f"\n Paycheck #{i} - {paycheck.pay_date} ({paycheck.employer})")
            print("-" * 60)
            print(f"Gross Income:              ${paycheck.gross_income:>10,.2f}")
            print()
            print("DEDUCTIONS:")
            print(f"  Federal Tax:             ${paycheck.federal_tax:>10,.2f}")
            print(f"  State Tax:               ${paycheck.state_tax:>10,.2f}")
            print(f"  Social Security:         ${paycheck.social_security_tax:>10,.2f}")
            print(f"  Medicare:                ${paycheck.medicare_tax:>10,.2f}")
            print(f"  Other Taxes:             ${paycheck.other_taxes:>10,.2f}")
            print(f"  Health Insurance:        ${paycheck.health_insurance:>10,.2f}")
            print(f"  Dental Insurance:        ${paycheck.dental_insurance:>10,.2f}")
            print(f"  Vision Insurance:        ${paycheck.vision_insurance:>10,.2f}")
            print(f"  Voluntary Life Ins:      ${paycheck.voluntary_life_insurance:>10,.2f}")
            print(f"  401k Contribution:       ${paycheck.retirement_401k:>10,.2f}")
            print(f"  403b Contribution:       ${paycheck.retirement_403b:>10,.2f}")
            print(f"  IRA Contribution:        ${paycheck.retirement_ira:>10,.2f}")
            print(f"  Other Deductions:        ${paycheck.other_deductions:>10,.2f}")
            print(f"                           {'-' * 12}")
            print(f"  Total Deductions:        ${paycheck.total_deductions:>10,.2f}")
            print()
            print("NET PAY CALCULATION:")
            print(f"  Entered Net Pay:         ${paycheck.net_pay:>10,.2f}")
            print(f"  Calculated Net Pay:      ${paycheck.calculated_net_pay:>10,.2f}")
            print(f"  Difference:              ${paycheck.net_pay_difference:>10,.2f}")
            print(f"  Matches: {'YES' if paycheck.net_pay_matches else 'NO'}")
            
            if not paycheck.net_pay_matches:
                print(f"Net pay discrepancy of ${abs(paycheck.net_pay_difference):.2f}")
            
            print()
            print("TAX ANALYSIS:")
            print(f"  Taxable Income:          ${paycheck.taxable_income:>10,.2f}")
            print(f"  Effective Tax Rate:      {paycheck.effective_tax_rate:>9.2f}%")
            print(f"  Federal Tax Rate:        {paycheck.federal_tax_rate:>9.2f}%")
            print(f"  State Tax Rate:          {paycheck.state_tax_rate:>9.2f}%")
            print(f"  Retirement Rate:         {paycheck.retirement_contribution_rate:>9.2f}%")
            
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        total_paychecks = len(paychecks)
        matching_paychecks = sum(1 for p in paychecks if p.net_pay_matches)
        total_gross = sum(p.gross_income for p in paychecks)
        total_net_entered = sum(p.net_pay for p in paychecks)
        total_net_calculated = sum(p.calculated_net_pay for p in paychecks)
        
        print(f"Total Paychecks:           {total_paychecks}")
        print(f"Net Pay Matches:           {matching_paychecks}/{total_paychecks}")
        print(f"Total Gross Income:        ${total_gross:,.2f}")
        print(f"Total Net (Entered):       ${total_net_entered:,.2f}")
        print(f"Total Net (Calculated):    ${total_net_calculated:,.2f}")
        print(f"Overall Difference:        ${total_net_entered - total_net_calculated:,.2f}")

if __name__ == "__main__":
    validate_net_pay_calculations()