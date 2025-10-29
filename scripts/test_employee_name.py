#!/usr/bin/env python3
"""
Test script to verify employee_name functionality works correctly
"""

import sys
import os
from datetime import date

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from api.paycheck.models import PaycheckModel

def test_employee_name_functionality():
    """Test that employee_name functionality works as expected"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Testing employee_name functionality...")
            
            # Test 1: Create paycheck with default employee_name
            print("\n1. Testing default employee_name...")
            paycheck1 = PaycheckModel(
                user_id='test123',
                employer='Test Corp',
                pay_period_start=date(2024, 1, 1),
                pay_period_end=date(2024, 1, 15),
                pay_date=date(2024, 1, 20),
                gross_income=5000.0,
                net_pay=3800.0
            )
            print(f"   Default employee_name: '{paycheck1.employee_name}'")
            assert paycheck1.employee_name == 'Self', f"Expected 'Self', got '{paycheck1.employee_name}'"
            print("   Default employee_name is 'Self'")
            
            # Test 2: Create paycheck with specific employee_name
            print("\n2. Testing specific employee_name...")
            paycheck2 = PaycheckModel(
                user_id='test123',
                employer='Test Corp',
                pay_period_start=date(2024, 1, 1),
                pay_period_end=date(2024, 1, 15),
                pay_date=date(2024, 1, 20),
                gross_income=4000.0,
                net_pay=3200.0,
                employee_name='Spouse'
            )
            print(f"   Specified employee_name: '{paycheck2.employee_name}'")
            assert paycheck2.employee_name == 'Spouse', f"Expected 'Spouse', got '{paycheck2.employee_name}'"
            print("   Custom employee_name works correctly")
            
            # Test 3: Test to_dict includes employee_name
            print("\n3. Testing to_dict method...")
            paycheck_dict = paycheck1.to_dict()
            assert 'employee_name' in paycheck_dict, "employee_name not found in to_dict output"
            assert paycheck_dict['employee_name'] == 'Self', f"Expected 'Self' in dict, got '{paycheck_dict['employee_name']}'"
            print("   to_dict includes employee_name field")
            
            # Test 4: Test __repr__ includes employee_name
            print("\n4. Testing __repr__ method...")
            repr_str = repr(paycheck1)
            assert 'Self' in repr_str, f"Employee name 'Self' not found in repr: {repr_str}"
            print(f"   Repr string: {repr_str}")
            print("   __repr__ includes employee_name")
            
            # Test 5: Test get_by_employee class method
            print("\n5. Testing get_by_employee class method...")
            # Save the paychecks first
            paycheck1.save()
            paycheck2.save()
            
            self_paychecks = PaycheckModel.get_by_employee('test123', 'Self')
            spouse_paychecks = PaycheckModel.get_by_employee('test123', 'Spouse')
            
            assert len(self_paychecks) == 1, f"Expected 1 'Self' paycheck, got {len(self_paychecks)}"
            assert len(spouse_paychecks) == 1, f"Expected 1 'Spouse' paycheck, got {len(spouse_paychecks)}"
            print("   get_by_employee method works correctly")
            
            print("\nAll employee_name functionality tests passed!")
            
            # Clean up
            paycheck1.delete()
            paycheck2.delete()
            print("   Test data cleaned up")
            
        except Exception as e:
            print(f"\nError testing employee_name functionality: {str(e)}")
            raise

if __name__ == '__main__':
    test_employee_name_functionality()