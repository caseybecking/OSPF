"""Tests for Paycheck API endpoints"""
import pytest
import json
from datetime import date, datetime
from api.paycheck.models import PaycheckModel


class TestPaycheckAPI:
    """Test paycheck API endpoints"""

    def test_create_paycheck(self, client, test_user):
        """Test creating a paycheck via API"""
        paycheck_data = {
            'user_id': test_user.id,
            'employer': 'API Test Corporation',
            'pay_period_start': '2024-01-01',
            'pay_period_end': '2024-01-15',
            'pay_date': '2024-01-20',
            'gross_income': 5000.00,
            'net_pay': 3800.00,
            'federal_tax': 800.00,
            'state_tax': 200.00,
            'social_security_tax': 310.00,
            'medicare_tax': 72.50,
            'retirement_401k': 500.00,
            'health_insurance': 150.00,
            'notes': 'API test paycheck'
        }

        response = client.post('/api/paycheck', 
                             data=json.dumps(paycheck_data),
                             content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Paycheck created successfully'
        assert 'paycheck' in data
        
        # Verify paycheck was created in database
        created_paycheck = PaycheckModel.query.filter_by(employer='API Test Corporation').first()
        assert created_paycheck is not None
        assert created_paycheck.gross_income == 5000.00
        assert created_paycheck.net_pay == 3800.00

    def test_create_paycheck_minimal(self, client, test_user):
        """Test creating paycheck with minimal required fields"""
        paycheck_data = {
            'user_id': test_user.id,
            'employer': 'Minimal API Test Corp',
            'pay_period_start': '2024-02-01',
            'pay_period_end': '2024-02-15',
            'pay_date': '2024-02-20',
            'gross_income': 3000.00,
            'net_pay': 2400.00
        }

        response = client.post('/api/paycheck', 
                             data=json.dumps(paycheck_data),
                             content_type='application/json')

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Paycheck created successfully'

    def test_create_paycheck_missing_required_fields(self, client, test_user):
        """Test creating paycheck with missing required fields"""
        paycheck_data = {
            'user_id': test_user.id,
            'employer': 'Incomplete Test Corp',
            # Missing required fields: pay_period_start, pay_period_end, pay_date, gross_income, net_pay
        }

        response = client.post('/api/paycheck', 
                             data=json.dumps(paycheck_data),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'All required fields must be provided' in data['message']

    def test_create_paycheck_invalid_numeric_values(self, client, test_user):
        """Test creating paycheck with invalid numeric values"""
        paycheck_data = {
            'user_id': test_user.id,
            'employer': 'Invalid Numeric Test Corp',
            'pay_period_start': '2024-03-01',
            'pay_period_end': '2024-03-15',
            'pay_date': '2024-03-20',
            'gross_income': 'not_a_number',
            'net_pay': '2400.00'
        }

        response = client.post('/api/paycheck', 
                             data=json.dumps(paycheck_data),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'must be valid numbers' in data['message']

    def test_create_paycheck_invalid_dates(self, client, test_user):
        """Test creating paycheck with invalid date format"""
        paycheck_data = {
            'user_id': test_user.id,
            'employer': 'Invalid Date Test Corp',
            'pay_period_start': 'invalid-date',
            'pay_period_end': '2024-03-15',
            'pay_date': '2024-03-20',
            'gross_income': 4000.00,
            'net_pay': 3200.00
        }

        response = client.post('/api/paycheck', 
                             data=json.dumps(paycheck_data),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'YYYY-MM-DD format' in data['message']

    def test_create_paycheck_invalid_date_logic(self, client, test_user):
        """Test creating paycheck with start date after end date"""
        paycheck_data = {
            'user_id': test_user.id,
            'employer': 'Invalid Date Logic Corp',
            'pay_period_start': '2024-03-20',  # After end date
            'pay_period_end': '2024-03-15',
            'pay_date': '2024-03-25',
            'gross_income': 4000.00,
            'net_pay': 3200.00
        }

        response = client.post('/api/paycheck', 
                             data=json.dumps(paycheck_data),
                             content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'start date must be before end date' in data['message']

    def test_list_paychecks(self, client, test_paycheck):
        """Test listing all paychecks"""
        response = client.get('/api/paycheck')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'paychecks' in data
        assert 'pagination' in data
        assert len(data['paychecks']) >= 1
        
        # Verify pagination info
        pagination = data['pagination']
        assert 'total' in pagination
        assert 'pages' in pagination
        assert 'current_page' in pagination
        assert 'per_page' in pagination

    def test_list_paychecks_pagination(self, client, session, test_user):
        """Test paycheck pagination"""
        # Create multiple paychecks
        for i in range(5):
            paycheck = PaycheckModel(
                user_id=test_user.id,
                employer=f'Pagination Test Corp {i+1}',
                pay_period_start=date(2024, i+1, 1),
                pay_period_end=date(2024, i+1, 15),
                pay_date=date(2024, i+1, 20),
                gross_income=4000.00 + (i * 100),
                net_pay=3200.00 + (i * 80)
            )
            paycheck.save()

        # Test first page with 3 items per page
        response = client.get('/api/paycheck?page=1&per_page=3')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['paychecks']) <= 3
        assert data['pagination']['current_page'] == 1
        assert data['pagination']['per_page'] == 3

    def test_list_paychecks_filters(self, client, test_user):
        """Test listing paychecks with filters"""
        # Create test paycheck
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Filter Test Corp',
            pay_period_start=date(2024, 6, 1),
            pay_period_end=date(2024, 6, 15),
            pay_date=date(2024, 6, 20),
            gross_income=5000.00,
            net_pay=4000.00
        )
        paycheck.save()

        # Test user_id filter
        response = client.get(f'/api/paycheck?user_id={test_user.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        for paycheck_data in data['paychecks']:
            assert paycheck_data['user_id'] == test_user.id

        # Test employer filter
        response = client.get('/api/paycheck?employer=Filter Test Corp')
        assert response.status_code == 200
        data = json.loads(response.data)
        for paycheck_data in data['paychecks']:
            assert paycheck_data['employer'] == 'Filter Test Corp'

        # Test date range filter
        response = client.get('/api/paycheck?start_date=2024-06-01&end_date=2024-06-30')
        assert response.status_code == 200
        data = json.loads(response.data)
        for paycheck_data in data['paychecks']:
            pay_date = datetime.strptime(paycheck_data['pay_date'], '%Y-%m-%d').date()
            assert date(2024, 6, 1) <= pay_date <= date(2024, 6, 30)

    def test_get_paycheck_detail(self, client, test_paycheck):
        """Test getting a specific paycheck by ID"""
        response = client.get(f'/api/paycheck/{test_paycheck.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'paycheck' in data
        paycheck_data = data['paycheck']
        assert paycheck_data['id'] == test_paycheck.id
        assert paycheck_data['employer'] == test_paycheck.employer
        assert paycheck_data['gross_income'] == test_paycheck.gross_income

    def test_get_paycheck_not_found(self, client):
        """Test getting a non-existent paycheck"""
        response = client.get('/api/paycheck/nonexistent-id')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Paycheck not found'

    def test_update_paycheck(self, client, test_paycheck):
        """Test updating a specific paycheck"""
        update_data = {
            'employer': 'Updated Test Corporation',
            'gross_income': 5500.00,
            'net_pay': 4200.00,
            'federal_tax': 900.00,
            'notes': 'Updated notes'
        }

        response = client.put(f'/api/paycheck/{test_paycheck.id}', 
                            data=json.dumps(update_data),
                            content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Paycheck updated successfully'
        
        # Verify updates in database
        updated_paycheck = PaycheckModel.query.get(test_paycheck.id)
        assert updated_paycheck.employer == 'Updated Test Corporation'
        assert updated_paycheck.gross_income == 5500.00
        assert updated_paycheck.net_pay == 4200.00
        assert updated_paycheck.federal_tax == 900.00
        assert updated_paycheck.notes == 'Updated notes'

    def test_update_paycheck_not_found(self, client):
        """Test updating a non-existent paycheck"""
        update_data = {
            'employer': 'Non-existent Corp',
            'gross_income': 5000.00
        }

        response = client.put('/api/paycheck/nonexistent-id', 
                            data=json.dumps(update_data),
                            content_type='application/json')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Paycheck not found'

    def test_update_paycheck_invalid_dates(self, client, test_paycheck):
        """Test updating paycheck with invalid date logic"""
        update_data = {
            'pay_period_start': '2024-03-20',  # After end date
            'pay_period_end': '2024-03-15'
        }

        response = client.put(f'/api/paycheck/{test_paycheck.id}', 
                            data=json.dumps(update_data),
                            content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'start date must be before end date' in data['message']

    def test_delete_paycheck(self, client, test_user):
        """Test deleting a specific paycheck"""
        # Create a paycheck to delete
        paycheck = PaycheckModel(
            user_id=test_user.id,
            employer='Delete Test Corp',
            pay_period_start=date(2024, 7, 1),
            pay_period_end=date(2024, 7, 15),
            pay_date=date(2024, 7, 20),
            gross_income=4000.00,
            net_pay=3200.00
        )
        paycheck.save()
        paycheck_id = paycheck.id

        response = client.delete(f'/api/paycheck/{paycheck_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Paycheck deleted successfully'
        
        # Verify deletion from database
        deleted_paycheck = PaycheckModel.query.get(paycheck_id)
        assert deleted_paycheck is None

    def test_delete_paycheck_not_found(self, client):
        """Test deleting a non-existent paycheck"""
        response = client.delete('/api/paycheck/nonexistent-id')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['message'] == 'Paycheck not found'

    def test_paycheck_analytics(self, client, test_user):
        """Test paycheck analytics endpoint"""
        # Create multiple paychecks for analytics
        paychecks_data = [
            {
                'employer': 'Analytics Test Corp 1',
                'gross_income': 5000.00,
                'net_pay': 3800.00,
                'federal_tax': 800.00,
                'retirement_401k': 500.00,
                'pay_date': date(2024, 1, 20)
            },
            {
                'employer': 'Analytics Test Corp 2',
                'gross_income': 5500.00,
                'net_pay': 4200.00,
                'federal_tax': 900.00,
                'retirement_401k': 600.00,
                'pay_date': date(2024, 2, 20)
            }
        ]
        
        for data in paychecks_data:
            paycheck = PaycheckModel(
                user_id=test_user.id,
                employer=data['employer'],
                pay_period_start=date(2024, 1, 1),
                pay_period_end=date(2024, 1, 15),
                pay_date=data['pay_date'],
                gross_income=data['gross_income'],
                net_pay=data['net_pay'],
                federal_tax=data['federal_tax'],
                retirement_401k=data['retirement_401k']
            )
            paycheck.save()

        response = client.get(f'/api/paycheck/analytics/{test_user.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify analytics structure
        assert 'summary' in data
        assert 'by_employer' in data
        assert 'date_range' in data
        
        summary = data['summary']
        assert 'total_paychecks' in summary
        assert 'total_gross_income' in summary
        assert 'total_net_pay' in summary
        assert 'average_gross_income' in summary
        assert 'average_tax_rate' in summary
        assert 'average_retirement_rate' in summary
        
        # Verify calculated values
        assert summary['total_paychecks'] >= 2
        assert summary['total_gross_income'] >= 10500.00  # 5000 + 5500
        assert summary['total_net_pay'] >= 8000.00  # 3800 + 4200

    def test_paycheck_analytics_not_found(self, client):
        """Test analytics for user with no paychecks"""
        response = client.get('/api/paycheck/analytics/nonexistent-user-id')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'No paychecks found' in data['message']

    def test_paycheck_trends(self, client, test_user):
        """Test paycheck trends endpoint"""
        # Create paychecks across different months
        months_data = [
            (date(2024, 1, 20), 5000.00, 3800.00),
            (date(2024, 2, 20), 5200.00, 3900.00),
            (date(2024, 3, 20), 5400.00, 4000.00)
        ]
        
        for pay_date, gross, net in months_data:
            paycheck = PaycheckModel(
                user_id=test_user.id,
                employer='Trends Test Corp',
                pay_period_start=date(pay_date.year, pay_date.month, 1),
                pay_period_end=date(pay_date.year, pay_date.month, 15),
                pay_date=pay_date,
                gross_income=gross,
                net_pay=net,
                federal_tax=gross * 0.15,
                retirement_401k=gross * 0.10
            )
            paycheck.save()

        response = client.get(f'/api/paycheck/trends/{test_user.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify trends structure
        assert 'monthly_trends' in data
        assert 'yearly_trends' in data
        assert 'summary' in data
        
        # Verify monthly trends contain expected data
        monthly_trends = data['monthly_trends']
        assert len(monthly_trends) >= 3
        
        # Check for month-over-month calculations
        for trend in monthly_trends:
            if 'mom_gross_change' in trend:
                assert isinstance(trend['mom_gross_change'], (int, float))

    def test_paycheck_compare(self, client, test_user):
        """Test paycheck comparison endpoint"""
        # Create paychecks for two different periods
        period1_paychecks = [
            PaycheckModel(
                user_id=test_user.id,
                employer='Compare Test Corp',
                pay_period_start=date(2024, 1, 1),
                pay_period_end=date(2024, 1, 15),
                pay_date=date(2024, 1, 20),
                gross_income=5000.00,
                net_pay=3800.00,
                federal_tax=800.00
            ),
            PaycheckModel(
                user_id=test_user.id,
                employer='Compare Test Corp',
                pay_period_start=date(2024, 1, 16),
                pay_period_end=date(2024, 1, 31),
                pay_date=date(2024, 1, 31),
                gross_income=5000.00,
                net_pay=3800.00,
                federal_tax=800.00
            )
        ]
        
        period2_paychecks = [
            PaycheckModel(
                user_id=test_user.id,
                employer='Compare Test Corp',
                pay_period_start=date(2024, 3, 1),
                pay_period_end=date(2024, 3, 15),
                pay_date=date(2024, 3, 20),
                gross_income=5500.00,
                net_pay=4200.00,
                federal_tax=900.00
            )
        ]
        
        for paycheck in period1_paychecks + period2_paychecks:
            paycheck.save()

        # Compare January vs March 2024
        params = {
            'period1_start': '2024-01-01',
            'period1_end': '2024-01-31',
            'period2_start': '2024-03-01',
            'period2_end': '2024-03-31'
        }
        
        response = client.get(f'/api/paycheck/compare/{test_user.id}', query_string=params)

        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify comparison structure
        assert 'period1' in data
        assert 'period2' in data
        assert 'changes' in data
        
        # Verify period data
        period1 = data['period1']
        period2 = data['period2']
        
        assert period1['count'] == 2
        assert period2['count'] == 1
        assert period1['total_gross'] == 10000.00  # 5000 + 5000
        assert period2['total_gross'] == 5500.00
        
        # Verify changes calculation
        changes = data['changes']
        assert 'gross_change' in changes
        expected_change = ((5500.00 - 10000.00) / 10000.00) * 100  # -45%
        assert abs(changes['gross_change'] - expected_change) < 0.01

    def test_paycheck_compare_missing_parameters(self, client, test_user):
        """Test paycheck comparison with missing parameters"""
        params = {
            'period1_start': '2024-01-01',
            # Missing other required parameters
        }
        
        response = client.get(f'/api/paycheck/compare/{test_user.id}', query_string=params)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'All period dates are required' in data['message']