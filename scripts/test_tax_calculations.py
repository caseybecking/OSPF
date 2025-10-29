#!/usr/bin/env python3
"""
Test script to verify tax rate calculations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.paycheck.models import PaycheckModel
from datetime import date

def test_tax_calculations():
    """Test the tax rate calculations"""
    
    # Create a test paycheck with known values
    paycheck = PaycheckModel(
        user_id='test-user',
        employer='Test Company',
        pay_period_start=date(2024, 1, 1),
        pay_period_end=date(2024, 1, 15), 
        pay_date=date(2024, 1, 20),
        gross_income=5000.00,  # $5000 gross
        net_pay=3500.00,
        federal_tax=600.00,    # $600 federal tax
        state_tax=200.00,      # $200 state tax
        social_security_tax=310.00,
        medicare_tax=72.50,
        retirement_401k=300.00,      # $300 pre-tax 401k
        health_insurance=150.00,     # $150 pre-tax insurance
        voluntary_life_insurance=25.00  # $25 pre-tax life insurance
    )
    
    print("=== Tax Rate Calculation Test ===")
    print(f"Gross Income: ${paycheck.gross_income:.2f}")
    
    # Calculate expected values
    expected_pre_tax = 300.00 + 150.00 + 25.00  # 401k + health + life = $475
    expected_taxable = 5000.00 - 475.00  # $4525
    expected_total_taxes = 600.00 + 200.00 + 310.00 + 72.50  # $1182.50
    expected_effective_rate = (1182.50 / 4525.00) * 100  # ~26.13%
    expected_federal_rate = (600.00 / 4525.00) * 100  # ~13.26%
    expected_state_rate = (200.00 / 4525.00) * 100  # ~4.42%
    
    print(f"Pre-tax Deductions: ${expected_pre_tax:.2f}")
    print(f"Expected Taxable Income: ${expected_taxable:.2f}")
    print(f"Actual Taxable Income: ${paycheck.taxable_income:.2f}")
    print(f"Match: {'' if abs(paycheck.taxable_income - expected_taxable) < 0.01 else ''}")
    
    print(f"\nTotal Taxes: ${paycheck.total_taxes:.2f}")
    print(f"Expected Effective Tax Rate: {expected_effective_rate:.2f}%")
    print(f"Actual Effective Tax Rate: {paycheck.effective_tax_rate:.2f}%")
    print(f"Match: {'' if abs(paycheck.effective_tax_rate - expected_effective_rate) < 0.01 else ''}")
    
    print(f"\nExpected Federal Tax Rate: {expected_federal_rate:.2f}%")
    print(f"Actual Federal Tax Rate: {paycheck.federal_tax_rate:.2f}%") 
    print(f"Match: {'' if abs(paycheck.federal_tax_rate - expected_federal_rate) < 0.01 else ''}")
    
    print(f"\nExpected State Tax Rate: {expected_state_rate:.2f}%")
    print(f"Actual State Tax Rate: {paycheck.state_tax_rate:.2f}%")
    print(f"Match: {'' if abs(paycheck.state_tax_rate - expected_state_rate) < 0.01 else ''}")
    
    # Test edge case: zero taxable income
    print("\n=== Edge Case: Zero Taxable Income ===")
    zero_paycheck = PaycheckModel(
        user_id='test-user-2',
        employer='Test Company 2',
        pay_period_start=date(2024, 1, 1),
        pay_period_end=date(2024, 1, 15),
        pay_date=date(2024, 1, 20),
        gross_income=1000.00,
        net_pay=0.00,
        federal_tax=0.00,
        retirement_401k=1000.00  # 401k equals gross income
    )
    
    print(f"Gross Income: ${zero_paycheck.gross_income:.2f}")
    print(f"401k Contribution: ${zero_paycheck.retirement_401k:.2f}")
    print(f"Taxable Income: ${zero_paycheck.taxable_income:.2f}")
    print(f"Effective Tax Rate: {zero_paycheck.effective_tax_rate:.2f}%")
    print(f"Should be 0%: {'' if zero_paycheck.effective_tax_rate == 0.0 else ''}")

if __name__ == "__main__":
    test_tax_calculations()