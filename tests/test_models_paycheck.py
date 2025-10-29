"""Tests for Paycheck model"""
import pytest
from datetime import datetime, date, timedelta
from api.paycheck.models import PaycheckModel


class TestPaycheckModel:
    """Test Paycheck model functionality"""

    def test_paycheck_creation(self, session, test_user):
        """Test creating a new paycheck"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Test Company Inc',
            pay_period_start=date(2024, 1, 1),
            pay_period_end=date(2024, 1, 15),
            pay_date=date(2024, 1, 20),
            gross_income=5000.00,
            net_pay=3800.00,
            federal_tax=800.00,
            state_tax=200.00,
            social_security_tax=310.00,
            medicare_tax=72.50,
            retirement_401k=500.00,
            health_insurance=150.00,
            voluntary_life_insurance=25.00
        )
        paycheck.save()

        assert paycheck.id is not None
        assert paycheck.user_id == test_user.id
        assert paycheck.employer == 'Test Company Inc'
        assert paycheck.pay_period_start == date(2024, 1, 1)
        assert paycheck.pay_period_end == date(2024, 1, 15)
        assert paycheck.pay_date == date(2024, 1, 20)
        assert paycheck.gross_income == 5000.00
        assert paycheck.net_pay == 3800.00
        assert paycheck.federal_tax == 800.00
        assert paycheck.state_tax == 200.00
        assert paycheck.social_security_tax == 310.00
        assert paycheck.medicare_tax == 72.50
        assert paycheck.retirement_401k == 500.00
        assert paycheck.health_insurance == 150.00
        assert paycheck.created_at is not None
        assert paycheck.updated_at is not None

    def test_paycheck_minimal_creation(self, session, test_user):
        """Test creating paycheck with only required fields"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Minimal Corp',
            pay_period_start=date(2024, 2, 1),
            pay_period_end=date(2024, 2, 15),
            pay_date=date(2024, 2, 20),
            gross_income=3000.00,
            net_pay=2400.00
        )
        paycheck.save()

        assert paycheck.id is not None
        assert paycheck.employer == 'Minimal Corp'
        assert paycheck.gross_income == 3000.00
        assert paycheck.net_pay == 2400.00
        # Test default values
        assert paycheck.federal_tax == 0.0
        assert paycheck.state_tax == 0.0
        assert paycheck.social_security_tax == 0.0
        assert paycheck.medicare_tax == 0.0
        assert paycheck.other_taxes == 0.0
        assert paycheck.health_insurance == 0.0
        assert paycheck.dental_insurance == 0.0
        assert paycheck.vision_insurance == 0.0
        assert paycheck.retirement_401k == 0.0
        assert paycheck.retirement_403b == 0.0
        assert paycheck.retirement_ira == 0.0
        assert paycheck.other_deductions == 0.0
        assert paycheck.overtime_hours == 0.0
        assert paycheck.bonus == 0.0
        assert paycheck.commission == 0.0

    def test_paycheck_to_dict(self, session, test_user):
        """Test paycheck serialization to dictionary"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Dict Test Corp',
            pay_period_start=date(2024, 3, 1),
            pay_period_end=date(2024, 3, 15),
            pay_date=date(2024, 3, 20),
            gross_income=4000.00,
            net_pay=3200.00,
            federal_tax=500.00,
            retirement_401k=300.00,
            notes='Test notes'
        )
        paycheck.save()

        paycheck_dict = paycheck.to_dict()

        assert paycheck_dict['id'] == paycheck.id
        assert paycheck_dict['user_id'] == test_user.id
        assert paycheck_dict['employer'] == 'Dict Test Corp'
        assert paycheck_dict['pay_period_start'] == '2024-03-01'
        assert paycheck_dict['pay_period_end'] == '2024-03-15'
        assert paycheck_dict['pay_date'] == '2024-03-20'
        assert paycheck_dict['gross_income'] == 4000.00
        assert paycheck_dict['net_pay'] == 3200.00
        assert paycheck_dict['federal_tax'] == 500.00
        assert paycheck_dict['retirement_401k'] == 300.00
        assert paycheck_dict['notes'] == 'Test notes'
        assert 'created_at' in paycheck_dict
        assert 'updated_at' in paycheck_dict
        assert 'total_taxes' in paycheck_dict
        assert 'total_deductions' in paycheck_dict
        assert 'total_retirement' in paycheck_dict
        assert 'effective_tax_rate' in paycheck_dict
        assert 'retirement_contribution_rate' in paycheck_dict

    def test_paycheck_repr(self, session, test_user):
        """Test paycheck string representation"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Repr Test LLC',
            pay_period_start=date(2024, 4, 1),
            pay_period_end=date(2024, 4, 15),
            pay_date=date(2024, 4, 20),
            gross_income=3500.00,
            net_pay=2800.00
        )
        paycheck.save()

        expected_repr = f'<Paycheck {paycheck.id!r} - Self - Repr Test LLC - 2024-04-20>'
        assert repr(paycheck) == expected_repr

    def test_paycheck_total_taxes_property(self, session, test_user):
        """Test total_taxes calculated property"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Tax Test Corp',
            pay_period_start=date(2024, 5, 1),
            pay_period_end=date(2024, 5, 15),
            pay_date=date(2024, 5, 20),
            gross_income=5000.00,
            net_pay=3500.00,
            federal_tax=800.00,
            state_tax=300.00,
            social_security_tax=310.00,
            medicare_tax=72.50,
            other_taxes=50.00
        )
        paycheck.save()

        expected_total = 800.00 + 300.00 + 310.00 + 72.50 + 50.00
        assert paycheck.total_taxes == expected_total

    def test_paycheck_total_deductions_property(self, session, test_user):
        """Test total_deductions calculated property"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Deduction Test Inc',
            pay_period_start=date(2024, 6, 1),
            pay_period_end=date(2024, 6, 15),
            pay_date=date(2024, 6, 20),
            gross_income=6000.00,
            net_pay=4000.00,
            federal_tax=800.00,
            state_tax=300.00,
            social_security_tax=372.00,
            medicare_tax=87.00,
            health_insurance=200.00,
            dental_insurance=25.00,
            vision_insurance=15.00,
            voluntary_life_insurance=30.00,
            other_deductions=100.00
        )
        paycheck.save()

        expected_taxes = 800.00 + 300.00 + 372.00 + 87.00
        expected_total = expected_taxes + 200.00 + 25.00 + 15.00 + 30.00 + 100.00
        assert paycheck.total_deductions == expected_total

    def test_paycheck_total_retirement_property(self, session, test_user):
        """Test total_retirement calculated property"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Retirement Test LLC',
            pay_period_start=date(2024, 7, 1),
            pay_period_end=date(2024, 7, 15),
            pay_date=date(2024, 7, 20),
            gross_income=5500.00,
            net_pay=4200.00,
            retirement_401k=400.00,
            retirement_403b=200.00,
            retirement_ira=100.00
        )
        paycheck.save()

        expected_total = 400.00 + 200.00 + 100.00
        assert paycheck.total_retirement == expected_total

    def test_paycheck_effective_tax_rate_property(self, session, test_user):
        """Test effective_tax_rate calculated property"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Tax Rate Test Corp',
            pay_period_start=date(2024, 8, 1),
            pay_period_end=date(2024, 8, 15),
            pay_date=date(2024, 8, 20),
            gross_income=5000.00,
            net_pay=3750.00,
            federal_tax=750.00,
            state_tax=250.00,
            social_security_tax=310.00,
            medicare_tax=72.50
        )
        paycheck.save()

        total_taxes = 750.00 + 250.00 + 310.00 + 72.50  # 1382.50
        expected_rate = round((total_taxes / 5000.00) * 100, 2)  # 27.65%
        assert paycheck.effective_tax_rate == expected_rate

    def test_paycheck_retirement_contribution_rate_property(self, session, test_user):
        """Test retirement_contribution_rate calculated property"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Retirement Rate Test Inc',
            pay_period_start=date(2024, 9, 1),
            pay_period_end=date(2024, 9, 15),
            pay_date=date(2024, 9, 20),
            gross_income=6000.00,
            net_pay=4500.00,
            retirement_401k=600.00,
            retirement_ira=300.00
        )
        paycheck.save()

        total_retirement = 600.00 + 300.00  # 900.00
        expected_rate = round((total_retirement / 6000.00) * 100, 2)  # 15.00%
        assert paycheck.retirement_contribution_rate == expected_rate

    def test_paycheck_zero_gross_income_rates(self, session, test_user):
        """Test rate calculations with zero gross income"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Zero Gross Test',
            pay_period_start=date(2024, 10, 1),
            pay_period_end=date(2024, 10, 15),
            pay_date=date(2024, 10, 20),
            gross_income=0.00,
            net_pay=0.00,
            federal_tax=0.00,
            retirement_401k=0.00
        )
        paycheck.save()

        assert paycheck.effective_tax_rate == 0.0
        assert paycheck.retirement_contribution_rate == 0.0

    def test_paycheck_delete(self, session, test_user):
        """Test deleting a paycheck"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Delete Test Corp',
            pay_period_start=date(2024, 11, 1),
            pay_period_end=date(2024, 11, 15),
            pay_date=date(2024, 11, 20),
            gross_income=4500.00,
            net_pay=3400.00
        )
        paycheck.save()
        paycheck_id = paycheck.id

        assert PaycheckModel.query.get(paycheck_id) is not None
        paycheck.delete()
        assert PaycheckModel.query.get(paycheck_id) is None

    def test_paycheck_query_by_user_id(self, session, test_user):
        """Test querying paychecks by user ID"""
        paycheck1 = PaycheckModel(
            user_id=test_user.id,
            employer='Query Test Corp 1',
            pay_period_start=date(2024, 12, 1),
            pay_period_end=date(2024, 12, 15),
            pay_date=date(2024, 12, 20),
            gross_income=4000.00,
            net_pay=3200.00
        )
        paycheck1.save()

        paycheck2 = PaycheckModel(
            user_id=test_user.id,
            employer='Query Test Corp 2',
            pay_period_start=date(2024, 12, 16),
            pay_period_end=date(2024, 12, 31),
            pay_date=date(2025, 1, 5),
            gross_income=4200.00,
            net_pay=3350.00
        )
        paycheck2.save()

        paychecks = PaycheckModel.get_by_user_id(test_user.id)
        assert len(paychecks) >= 2
        paycheck_ids = [p.id for p in paychecks]
        assert paycheck1.id in paycheck_ids
        assert paycheck2.id in paycheck_ids

    def test_paycheck_query_by_date_range(self, session, test_user):
        """Test querying paychecks by date range"""
        # Paycheck within range
        paycheck_in_range = PaycheckModel(
            user_id=test_user.id,
            employer='Date Range Test 1',
            pay_period_start=date(2024, 6, 1),
            pay_period_end=date(2024, 6, 15),
            pay_date=date(2024, 6, 20),
            gross_income=4000.00,
            net_pay=3200.00
        )
        paycheck_in_range.save()

        # Paycheck outside range
        paycheck_outside_range = PaycheckModel(
            user_id=test_user.id,
            employer='Date Range Test 2',
            pay_period_start=date(2024, 8, 1),
            pay_period_end=date(2024, 8, 15),
            pay_date=date(2024, 8, 20),
            gross_income=4200.00,
            net_pay=3350.00
        )
        paycheck_outside_range.save()

        # Query for paychecks in June 2024
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 30)
        paychecks = PaycheckModel.get_by_date_range(test_user.id, start_date, end_date)
        
        paycheck_ids = [p.id for p in paychecks]
        assert paycheck_in_range.id in paycheck_ids
        assert paycheck_outside_range.id not in paycheck_ids

    def test_paycheck_query_by_employer(self, session, test_user):
        """Test querying paychecks by employer"""
        employer_name = 'Specific Employer Inc'
        
        paycheck1 = PaycheckModel(
            user_id=test_user.id,
            employer=employer_name,
            pay_period_start=date(2024, 3, 1),
            pay_period_end=date(2024, 3, 15),
            pay_date=date(2024, 3, 20),
            gross_income=5000.00,
            net_pay=4000.00
        )
        paycheck1.save()

        paycheck2 = PaycheckModel(
            user_id=test_user.id,
            employer='Different Employer LLC',
            pay_period_start=date(2024, 3, 16),
            pay_period_end=date(2024, 3, 31),
            pay_date=date(2024, 4, 5),
            gross_income=5200.00,
            net_pay=4100.00
        )
        paycheck2.save()

        paychecks = PaycheckModel.get_by_employer(test_user.id, employer_name)
        
        assert len(paychecks) >= 1
        for paycheck in paychecks:
            assert paycheck.employer == employer_name
        
        paycheck_ids = [p.id for p in paychecks]
        assert paycheck1.id in paycheck_ids
        assert paycheck2.id not in paycheck_ids

    def test_paycheck_work_details(self, session, test_user):
        """Test paycheck with work details"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Work Details Test Corp',
            pay_period_start=date(2024, 5, 1),
            pay_period_end=date(2024, 5, 15),
            pay_date=date(2024, 5, 20),
            gross_income=4800.00,
            net_pay=3600.00,
            hours_worked=80.0,
            hourly_rate=25.00,
            overtime_hours=8.0,
            overtime_rate=37.50,
            bonus=500.00,
            commission=200.00
        )
        paycheck.save()

        assert paycheck.hours_worked == 80.0
        assert paycheck.hourly_rate == 25.00
        assert paycheck.overtime_hours == 8.0
        assert paycheck.overtime_rate == 37.50
        assert paycheck.bonus == 500.00
        assert paycheck.commission == 200.00

    def test_paycheck_with_notes(self, session, test_user):
        """Test paycheck with notes"""
        notes_text = "This paycheck includes a year-end bonus and additional overtime pay for project completion."
        
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Notes Test LLC',
            pay_period_start=date(2024, 12, 1),
            pay_period_end=date(2024, 12, 15),
            pay_date=date(2024, 12, 20),
            gross_income=6500.00,
            net_pay=4800.00,
            notes=notes_text
        )
        paycheck.save()

        assert paycheck.notes == notes_text

    def test_paycheck_comprehensive_example(self, session, test_user):
        """Test paycheck with all fields populated"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Comprehensive Test Corp',
            pay_period_start=date(2024, 12, 1),
            pay_period_end=date(2024, 12, 15),
            pay_date=date(2024, 12, 20),
            gross_income=7500.00,
            net_pay=5200.00,
            federal_tax=1200.00,
            state_tax=450.00,
            social_security_tax=465.00,
            medicare_tax=108.75,
            other_taxes=75.00,
            health_insurance=250.00,
            dental_insurance=30.00,
            vision_insurance=15.00,
            voluntary_life_insurance=40.00,
            retirement_401k=750.00,
            retirement_403b=0.00,
            retirement_ira=100.00,
            other_deductions=50.00,
            hours_worked=80.0,
            hourly_rate=30.00,
            overtime_hours=10.0,
            overtime_rate=45.00,
            bonus=1000.00,
            commission=500.00,
            notes='Comprehensive test paycheck with all possible fields populated'
        )
        paycheck.save()

        # Test all properties are calculated correctly
        assert paycheck.total_taxes == 2298.75  # Sum of all taxes
        assert paycheck.total_retirement == 850.00  # 401k + 403b + IRA
        assert paycheck.effective_tax_rate > 0
        assert paycheck.retirement_contribution_rate > 0
        
        # Test string representation
        assert str(paycheck).startswith('<Paycheck')
        assert 'Comprehensive Test Corp' in str(paycheck)

    def test_paycheck_tax_rate_calculations(self, session, test_user):
        """Test tax rate calculations using taxable income"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Tax Rate Test Corp',
            pay_period_start=date(2024, 1, 1),
            pay_period_end=date(2024, 1, 15),
            pay_date=date(2024, 1, 20),
            gross_income=5000.00,
            net_pay=3500.00,
            federal_tax=600.00,
            state_tax=200.00,
            social_security_tax=310.00,
            medicare_tax=72.50,
            retirement_401k=300.00,
            health_insurance=150.00,
            voluntary_life_insurance=25.00
        )
        paycheck.save()

        # Test taxable income calculation
        # Gross ($5000) - Pre-tax deductions ($300 + $150 + $25 = $475) = $4525
        expected_taxable = 5000.00 - 475.00
        assert paycheck.taxable_income == expected_taxable

        # Test tax rate calculations based on taxable income
        expected_total_taxes = 600.00 + 200.00 + 310.00 + 72.50  # $1182.50
        expected_effective_rate = round((expected_total_taxes / expected_taxable) * 100, 2)
        expected_federal_rate = round((600.00 / expected_taxable) * 100, 2)
        expected_state_rate = round((200.00 / expected_taxable) * 100, 2)

        assert paycheck.effective_tax_rate == expected_effective_rate
        assert paycheck.federal_tax_rate == expected_federal_rate
        assert paycheck.state_tax_rate == expected_state_rate

    def test_paycheck_zero_taxable_income(self, session, test_user):
        """Test edge case where taxable income is zero or negative"""
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Edge Case Corp',
            pay_period_start=date(2024, 1, 1),
            pay_period_end=date(2024, 1, 15),
            pay_date=date(2024, 1, 20),
            gross_income=1000.00,
            net_pay=0.00,
            federal_tax=0.00,
            retirement_401k=1000.00  # Equals gross income
        )
        paycheck.save()

        # When taxable income is zero or negative, tax rates should be 0
        assert paycheck.taxable_income == 0.0
        assert paycheck.effective_tax_rate == 0.0
        assert paycheck.federal_tax_rate == 0.0
        assert paycheck.state_tax_rate == 0.0