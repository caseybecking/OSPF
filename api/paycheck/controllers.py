from datetime import datetime, date
from math import ceil
from flask import g, request, jsonify, make_response, session
from flask_restx import Resource, fields
from app import db
from api.paycheck.models import PaycheckModel

# Define the paycheck model for API documentation
paycheck_model = g.api.model('Paycheck', {
    'user_id': fields.String(required=True, description='User ID'),
    'employer': fields.String(required=True, description='Employer/Company Name'),
    'employee_name': fields.String(description='Employee Name (defaults to "Self")'),
    'pay_period_start': fields.Date(required=True, description='Pay Period Start Date'),
    'pay_period_end': fields.Date(required=True, description='Pay Period End Date'),
    'pay_date': fields.Date(required=True, description='Pay Date'),
    'gross_income': fields.Float(required=True, description='Gross Income'),
    'net_pay': fields.Float(required=True, description='Net Pay'),
    'federal_tax': fields.Float(description='Federal Tax Withheld'),
    'state_tax': fields.Float(description='State Tax Withheld'),
    'social_security_tax': fields.Float(description='Social Security Tax'),
    'medicare_tax': fields.Float(description='Medicare Tax'),
    'other_taxes': fields.Float(description='Other Taxes'),
    'health_insurance': fields.Float(description='Health Insurance Deduction'),
    'dental_insurance': fields.Float(description='Dental Insurance Deduction'),
    'vision_insurance': fields.Float(description='Vision Insurance Deduction'),
    'voluntary_life_insurance': fields.Float(description='Voluntary Life Insurance Deduction'),
    'retirement_401k': fields.Float(description='401k Contribution'),
    'retirement_403b': fields.Float(description='403b Contribution'),
    'retirement_ira': fields.Float(description='IRA Contribution'),
    'other_deductions': fields.Float(description='Other Deductions'),
    'hours_worked': fields.Float(description='Hours Worked'),
    'hourly_rate': fields.Float(description='Hourly Rate'),
    'overtime_hours': fields.Float(description='Overtime Hours'),
    'overtime_rate': fields.Float(description='Overtime Rate'),
    'bonus': fields.Float(description='Bonus Amount'),
    'commission': fields.Float(description='Commission Amount'),
    'notes': fields.String(description='Additional Notes')
})

@g.api.route('/paycheck')
class Paycheck(Resource):
    @g.api.expect(paycheck_model)
    def post(self):
        """Create a new paycheck entry"""
        data = request.json
        
        # Extract required fields
        user_id = data.get('user_id')
        employer = data.get('employer')
        employee_name = data.get('employee_name', 'Self')
        pay_period_start = data.get('pay_period_start')
        pay_period_end = data.get('pay_period_end')
        pay_date = data.get('pay_date')
        gross_income = data.get('gross_income')
        net_pay = data.get('net_pay')

        # Validate required fields
        if not all([user_id, employer, pay_period_start, pay_period_end, pay_date, gross_income, net_pay]):
            return make_response(jsonify({
                'message': 'All required fields must be provided: user_id, employer, pay_period_start, pay_period_end, pay_date, gross_income, net_pay'
            }), 400)

        # Validate numeric fields
        try:
            gross_income = float(gross_income)
            net_pay = float(net_pay)
        except (ValueError, TypeError):
            return make_response(jsonify({
                'message': 'Gross income and net pay must be valid numbers'
            }), 400)

        # Parse date fields
        try:
            if isinstance(pay_period_start, str):
                pay_period_start = datetime.strptime(pay_period_start, '%Y-%m-%d').date()
            if isinstance(pay_period_end, str):
                pay_period_end = datetime.strptime(pay_period_end, '%Y-%m-%d').date()
            if isinstance(pay_date, str):
                pay_date = datetime.strptime(pay_date, '%Y-%m-%d').date()
        except ValueError:
            return make_response(jsonify({
                'message': 'Date fields must be in YYYY-MM-DD format'
            }), 400)

        # Validate logical date order
        if pay_period_start > pay_period_end:
            return make_response(jsonify({
                'message': 'Pay period start date must be before end date'
            }), 400)

        # Extract optional fields with defaults
        federal_tax = float(data.get('federal_tax', 0.0))
        state_tax = float(data.get('state_tax', 0.0))
        social_security_tax = float(data.get('social_security_tax', 0.0))
        medicare_tax = float(data.get('medicare_tax', 0.0))
        other_taxes = float(data.get('other_taxes', 0.0))
        health_insurance = float(data.get('health_insurance', 0.0))
        dental_insurance = float(data.get('dental_insurance', 0.0))
        vision_insurance = float(data.get('vision_insurance', 0.0))
        voluntary_life_insurance = float(data.get('voluntary_life_insurance', 0.0))
        retirement_401k = float(data.get('retirement_401k', 0.0))
        retirement_403b = float(data.get('retirement_403b', 0.0))
        retirement_ira = float(data.get('retirement_ira', 0.0))
        other_deductions = float(data.get('other_deductions', 0.0))
        hours_worked = data.get('hours_worked')
        hourly_rate = data.get('hourly_rate')
        overtime_hours = float(data.get('overtime_hours', 0.0))
        overtime_rate = data.get('overtime_rate')
        bonus = float(data.get('bonus', 0.0))
        commission = float(data.get('commission', 0.0))
        notes = data.get('notes')

        # Convert numeric string fields to float if provided
        if hours_worked is not None:
            hours_worked = float(hours_worked)
        if hourly_rate is not None:
            hourly_rate = float(hourly_rate)
        if overtime_rate is not None:
            overtime_rate = float(overtime_rate)

        # Create new paycheck
        new_paycheck = PaycheckModel(
            user_id=user_id,
            employer=employer,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=pay_date,
            gross_income=gross_income,
            net_pay=net_pay,
            employee_name=employee_name,
            federal_tax=federal_tax,
            state_tax=state_tax,
            social_security_tax=social_security_tax,
            medicare_tax=medicare_tax,
            other_taxes=other_taxes,
            health_insurance=health_insurance,
            dental_insurance=dental_insurance,
            vision_insurance=vision_insurance,
            voluntary_life_insurance=voluntary_life_insurance,
            retirement_401k=retirement_401k,
            retirement_403b=retirement_403b,
            retirement_ira=retirement_ira,
            other_deductions=other_deductions,
            hours_worked=hours_worked,
            hourly_rate=hourly_rate,
            overtime_hours=overtime_hours,
            overtime_rate=overtime_rate,
            bonus=bonus,
            commission=commission,
            notes=notes
        )
        
        new_paycheck.save()

        return make_response(jsonify({
            'message': 'Paycheck created successfully',
            'paycheck': new_paycheck.to_dict()
        }), 201)

    def get(self):
        """Get list of paychecks with pagination"""
        # Extract pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=100, type=int)
        user_id = request.args.get('user_id')
        employer = request.args.get('employer')
        employee_name = request.args.get('employee_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Start with base query
        query = PaycheckModel.query

        # Apply filters
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if employer:
            query = query.filter_by(employer=employer)
        
        if employee_name:
            query = query.filter_by(employee_name=employee_name)
            
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(PaycheckModel.pay_date >= start_date)
            except ValueError:
                return make_response(jsonify({
                    'message': 'start_date must be in YYYY-MM-DD format'
                }), 400)
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(PaycheckModel.pay_date <= end_date)
            except ValueError:
                return make_response(jsonify({
                    'message': 'end_date must be in YYYY-MM-DD format'
                }), 400)

        # Order by pay date descending
        query = query.order_by(PaycheckModel.pay_date.desc())

        # Apply pagination
        paychecks_query = query.paginate(page=page, per_page=per_page, error_out=False)

        # Get the items for the current page
        paychecks = paychecks_query.items

        # Convert paychecks to dictionaries
        _paychecks = [paycheck.to_dict() for paycheck in paychecks]

        # Metadata for pagination
        pagination_info = {
            'total': paychecks_query.total,
            'pages': ceil(paychecks_query.total / per_page),
            'current_page': paychecks_query.page,
            'per_page': paychecks_query.per_page
        }

        return make_response(jsonify({
            'paychecks': _paychecks, 
            'pagination': pagination_info
        }), 200)


@g.api.route('/paycheck/<string:paycheck_id>')
class PaycheckDetail(Resource):
    def get(self, paycheck_id):
        """Get a specific paycheck by ID"""
        paycheck = PaycheckModel.query.get(paycheck_id)
        
        if not paycheck:
            return make_response(jsonify({
                'message': 'Paycheck not found'
            }), 404)
            
        return make_response(jsonify({
            'paycheck': paycheck.to_dict()
        }), 200)

    @g.api.expect(paycheck_model)
    def put(self, paycheck_id):
        """Update a specific paycheck"""
        paycheck = PaycheckModel.query.get(paycheck_id)
        
        if not paycheck:
            return make_response(jsonify({
                'message': 'Paycheck not found'
            }), 404)

        data = request.json

        # Update fields if provided
        if 'employer' in data:
            paycheck.employer = data['employer']
        if 'employee_name' in data:
            paycheck.employee_name = data['employee_name']
        if 'pay_period_start' in data:
            try:
                paycheck.pay_period_start = datetime.strptime(data['pay_period_start'], '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({
                    'message': 'pay_period_start must be in YYYY-MM-DD format'
                }), 400)
        if 'pay_period_end' in data:
            try:
                paycheck.pay_period_end = datetime.strptime(data['pay_period_end'], '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({
                    'message': 'pay_period_end must be in YYYY-MM-DD format'
                }), 400)
        if 'pay_date' in data:
            try:
                paycheck.pay_date = datetime.strptime(data['pay_date'], '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({
                    'message': 'pay_date must be in YYYY-MM-DD format'
                }), 400)

        # Update numeric fields
        numeric_fields = [
            'gross_income', 'net_pay', 'federal_tax', 'state_tax', 
            'social_security_tax', 'medicare_tax', 'other_taxes',
            'health_insurance', 'dental_insurance', 'vision_insurance',
            'voluntary_life_insurance', 'retirement_401k', 'retirement_403b', 'retirement_ira',
            'other_deductions', 'hours_worked', 'hourly_rate',
            'overtime_hours', 'overtime_rate', 'bonus', 'commission'
        ]
        
        for field in numeric_fields:
            if field in data:
                try:
                    setattr(paycheck, field, float(data[field]) if data[field] is not None else None)
                except (ValueError, TypeError):
                    return make_response(jsonify({
                        'message': f'{field} must be a valid number'
                    }), 400)

        if 'notes' in data:
            paycheck.notes = data['notes']

        # Validate logical date order if dates were updated
        if paycheck.pay_period_start > paycheck.pay_period_end:
            return make_response(jsonify({
                'message': 'Pay period start date must be before end date'
            }), 400)

        paycheck.save()

        return make_response(jsonify({
            'message': 'Paycheck updated successfully',
            'paycheck': paycheck.to_dict()
        }), 200)

    def delete(self, paycheck_id):
        """Delete a specific paycheck"""
        paycheck = PaycheckModel.query.get(paycheck_id)
        
        if not paycheck:
            return make_response(jsonify({
                'message': 'Paycheck not found'
            }), 404)

        paycheck.delete()

        return make_response(jsonify({
            'message': 'Paycheck deleted successfully'
        }), 200)


@g.api.route('/paycheck/analytics/<string:user_id>')
class PaycheckAnalytics(Resource):
    def get(self, user_id):
        """Get paycheck analytics for a user"""
        # Get query parameters for date filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = PaycheckModel.query.filter_by(user_id=user_id)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(PaycheckModel.pay_date >= start_date)
            except ValueError:
                return make_response(jsonify({
                    'message': 'start_date must be in YYYY-MM-DD format'
                }), 400)
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(PaycheckModel.pay_date <= end_date)
            except ValueError:
                return make_response(jsonify({
                    'message': 'end_date must be in YYYY-MM-DD format'
                }), 400)
        
        paychecks = query.order_by(PaycheckModel.pay_date.desc()).all()
        
        if not paychecks:
            return make_response(jsonify({
                'message': 'No paychecks found for the specified criteria'
            }), 404)
        
        # Calculate analytics
        total_paychecks = len(paychecks)
        total_gross = sum(p.gross_income for p in paychecks)
        total_net = sum(p.net_pay for p in paychecks)
        total_taxes = sum(p.total_taxes for p in paychecks)
        total_retirement = sum(p.total_retirement for p in paychecks)
        
        avg_gross = total_gross / total_paychecks if total_paychecks > 0 else 0
        avg_net = total_net / total_paychecks if total_paychecks > 0 else 0
        avg_tax_rate = (total_taxes / total_gross * 100) if total_gross > 0 else 0
        avg_retirement_rate = (total_retirement / total_gross * 100) if total_gross > 0 else 0
        
        # Group by employer
        employer_stats = {}
        for paycheck in paychecks:
            employer = paycheck.employer
            if employer not in employer_stats:
                employer_stats[employer] = {
                    'count': 0,
                    'total_gross': 0,
                    'total_net': 0,
                    'total_taxes': 0,
                    'total_retirement': 0
                }
            employer_stats[employer]['count'] += 1
            employer_stats[employer]['total_gross'] += paycheck.gross_income
            employer_stats[employer]['total_net'] += paycheck.net_pay
            employer_stats[employer]['total_taxes'] += paycheck.total_taxes
            employer_stats[employer]['total_retirement'] += paycheck.total_retirement
        
        # Calculate averages for each employer
        for employer, stats in employer_stats.items():
            count = stats['count']
            stats['avg_gross'] = stats['total_gross'] / count
            stats['avg_net'] = stats['total_net'] / count
            stats['avg_tax_rate'] = (stats['total_taxes'] / stats['total_gross'] * 100) if stats['total_gross'] > 0 else 0
            stats['avg_retirement_rate'] = (stats['total_retirement'] / stats['total_gross'] * 100) if stats['total_gross'] > 0 else 0
        
        return make_response(jsonify({
            'summary': {
                'total_paychecks': total_paychecks,
                'total_gross_income': round(total_gross, 2),
                'total_net_pay': round(total_net, 2),
                'total_taxes': round(total_taxes, 2),
                'total_retirement': round(total_retirement, 2),
                'average_gross_income': round(avg_gross, 2),
                'average_net_pay': round(avg_net, 2),
                'average_tax_rate': round(avg_tax_rate, 2),
                'average_retirement_rate': round(avg_retirement_rate, 2)
            },
            'by_employer': employer_stats,
            'date_range': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        }), 200)


@g.api.route('/paycheck/trends/<string:user_id>')
class PaycheckTrends(Resource):
    def get(self, user_id):
        """Get month-over-month and year-over-year paycheck trends"""
        from datetime import datetime, timedelta
        import calendar
        
        # Get all paychecks for the user
        paychecks = PaycheckModel.query.filter_by(user_id=user_id)\
                                      .order_by(PaycheckModel.pay_date.desc()).all()
        
        if not paychecks:
            return make_response(jsonify({
                'message': 'No paychecks found for this user'
            }), 404)
        
        # Group paychecks by month and year
        monthly_data = {}
        yearly_data = {}
        
        for paycheck in paychecks:
            # Monthly grouping
            month_key = f"{paycheck.pay_date.year}-{paycheck.pay_date.month:02d}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'count': 0,
                    'total_gross': 0,
                    'total_net': 0,
                    'total_taxes': 0,
                    'total_retirement': 0,
                    'paychecks': []
                }
            monthly_data[month_key]['count'] += 1
            monthly_data[month_key]['total_gross'] += paycheck.gross_income
            monthly_data[month_key]['total_net'] += paycheck.net_pay
            monthly_data[month_key]['total_taxes'] += paycheck.total_taxes
            monthly_data[month_key]['total_retirement'] += paycheck.total_retirement
            monthly_data[month_key]['paychecks'].append(paycheck.to_dict())
            
            # Yearly grouping
            year_key = str(paycheck.pay_date.year)
            if year_key not in yearly_data:
                yearly_data[year_key] = {
                    'count': 0,
                    'total_gross': 0,
                    'total_net': 0,
                    'total_taxes': 0,
                    'total_retirement': 0
                }
            yearly_data[year_key]['count'] += 1
            yearly_data[year_key]['total_gross'] += paycheck.gross_income
            yearly_data[year_key]['total_net'] += paycheck.net_pay
            yearly_data[year_key]['total_taxes'] += paycheck.total_taxes
            yearly_data[year_key]['total_retirement'] += paycheck.total_retirement
        
        # Calculate monthly trends with percentage changes
        monthly_trends = []
        sorted_months = sorted(monthly_data.keys())
        
        for i, month in enumerate(sorted_months):
            data = monthly_data[month]
            month_info = {
                'period': month,
                'year': int(month.split('-')[0]),
                'month': int(month.split('-')[1]),
                'month_name': calendar.month_name[int(month.split('-')[1])],
                'count': data['count'],
                'total_gross': round(data['total_gross'], 2),
                'total_net': round(data['total_net'], 2),
                'total_taxes': round(data['total_taxes'], 2),
                'total_retirement': round(data['total_retirement'], 2),
                'avg_gross': round(data['total_gross'] / data['count'], 2),
                'avg_net': round(data['total_net'] / data['count'], 2),
                'avg_tax_rate': round((data['total_taxes'] / data['total_gross'] * 100), 2) if data['total_gross'] > 0 else 0,
                'avg_retirement_rate': round((data['total_retirement'] / data['total_gross'] * 100), 2) if data['total_gross'] > 0 else 0
            }
            
            # Calculate month-over-month changes
            if i > 0:
                prev_month = sorted_months[i-1]
                prev_data = monthly_data[prev_month]
                
                month_info['mom_gross_change'] = round(
                    ((data['total_gross'] - prev_data['total_gross']) / prev_data['total_gross'] * 100), 2
                ) if prev_data['total_gross'] > 0 else 0
                
                month_info['mom_net_change'] = round(
                    ((data['total_net'] - prev_data['total_net']) / prev_data['total_net'] * 100), 2
                ) if prev_data['total_net'] > 0 else 0
                
                month_info['mom_tax_rate_change'] = round(
                    month_info['avg_tax_rate'] - round((prev_data['total_taxes'] / prev_data['total_gross'] * 100), 2), 2
                ) if prev_data['total_gross'] > 0 else 0
                
                month_info['mom_retirement_rate_change'] = round(
                    month_info['avg_retirement_rate'] - round((prev_data['total_retirement'] / prev_data['total_gross'] * 100), 2), 2
                ) if prev_data['total_gross'] > 0 else 0
            
            monthly_trends.append(month_info)
        
        # Calculate yearly trends with percentage changes
        yearly_trends = []
        sorted_years = sorted(yearly_data.keys())
        
        for i, year in enumerate(sorted_years):
            data = yearly_data[year]
            year_info = {
                'year': int(year),
                'count': data['count'],
                'total_gross': round(data['total_gross'], 2),
                'total_net': round(data['total_net'], 2),
                'total_taxes': round(data['total_taxes'], 2),
                'total_retirement': round(data['total_retirement'], 2),
                'avg_gross': round(data['total_gross'] / data['count'], 2),
                'avg_net': round(data['total_net'] / data['count'], 2),
                'avg_tax_rate': round((data['total_taxes'] / data['total_gross'] * 100), 2) if data['total_gross'] > 0 else 0,
                'avg_retirement_rate': round((data['total_retirement'] / data['total_gross'] * 100), 2) if data['total_gross'] > 0 else 0
            }
            
            # Calculate year-over-year changes
            if i > 0:
                prev_year = sorted_years[i-1]
                prev_data = yearly_data[prev_year]
                
                year_info['yoy_gross_change'] = round(
                    ((data['total_gross'] - prev_data['total_gross']) / prev_data['total_gross'] * 100), 2
                ) if prev_data['total_gross'] > 0 else 0
                
                year_info['yoy_net_change'] = round(
                    ((data['total_net'] - prev_data['total_net']) / prev_data['total_net'] * 100), 2
                ) if prev_data['total_net'] > 0 else 0
                
                year_info['yoy_tax_rate_change'] = round(
                    year_info['avg_tax_rate'] - round((prev_data['total_taxes'] / prev_data['total_gross'] * 100), 2), 2
                ) if prev_data['total_gross'] > 0 else 0
                
                year_info['yoy_retirement_rate_change'] = round(
                    year_info['avg_retirement_rate'] - round((prev_data['total_retirement'] / prev_data['total_gross'] * 100), 2), 2
                ) if prev_data['total_gross'] > 0 else 0
            
            yearly_trends.append(year_info)
        
        return make_response(jsonify({
            'monthly_trends': monthly_trends,
            'yearly_trends': yearly_trends,
            'summary': {
                'total_months': len(monthly_trends),
                'total_years': len(yearly_trends),
                'date_range': {
                    'earliest': paychecks[-1].pay_date.isoformat(),
                    'latest': paychecks[0].pay_date.isoformat()
                }
            }
        }), 200)


@g.api.route('/paycheck/compare/<string:user_id>')
class PaycheckCompare(Resource):
    def get(self, user_id):
        """Compare paycheck data across different time periods"""
        period1_start = request.args.get('period1_start')
        period1_end = request.args.get('period1_end')
        period2_start = request.args.get('period2_start')
        period2_end = request.args.get('period2_end')
        
        if not all([period1_start, period1_end, period2_start, period2_end]):
            return make_response(jsonify({
                'message': 'All period dates are required: period1_start, period1_end, period2_start, period2_end'
            }), 400)
        
        try:
            period1_start = datetime.strptime(period1_start, '%Y-%m-%d').date()
            period1_end = datetime.strptime(period1_end, '%Y-%m-%d').date()
            period2_start = datetime.strptime(period2_start, '%Y-%m-%d').date()
            period2_end = datetime.strptime(period2_end, '%Y-%m-%d').date()
        except ValueError:
            return make_response(jsonify({
                'message': 'Date fields must be in YYYY-MM-DD format'
            }), 400)
        
        # Get paychecks for period 1
        period1_paychecks = PaycheckModel.query.filter(
            PaycheckModel.user_id == user_id,
            PaycheckModel.pay_date >= period1_start,
            PaycheckModel.pay_date <= period1_end
        ).all()
        
        # Get paychecks for period 2
        period2_paychecks = PaycheckModel.query.filter(
            PaycheckModel.user_id == user_id,
            PaycheckModel.pay_date >= period2_start,
            PaycheckModel.pay_date <= period2_end
        ).all()
        
        def calculate_period_stats(paychecks, period_name):
            if not paychecks:
                return {
                    'period': period_name,
                    'count': 0,
                    'total_gross': 0,
                    'total_net': 0,
                    'total_taxes': 0,
                    'total_retirement': 0,
                    'avg_gross': 0,
                    'avg_net': 0,
                    'avg_tax_rate': 0,
                    'avg_retirement_rate': 0
                }
            
            total_gross = sum(p.gross_income for p in paychecks)
            total_net = sum(p.net_pay for p in paychecks)
            total_taxes = sum(p.total_taxes for p in paychecks)
            total_retirement = sum(p.total_retirement for p in paychecks)
            count = len(paychecks)
            
            return {
                'period': period_name,
                'count': count,
                'total_gross': round(total_gross, 2),
                'total_net': round(total_net, 2),
                'total_taxes': round(total_taxes, 2),
                'total_retirement': round(total_retirement, 2),
                'avg_gross': round(total_gross / count, 2),
                'avg_net': round(total_net / count, 2),
                'avg_tax_rate': round((total_taxes / total_gross * 100), 2) if total_gross > 0 else 0,
                'avg_retirement_rate': round((total_retirement / total_gross * 100), 2) if total_gross > 0 else 0
            }
        
        period1_stats = calculate_period_stats(period1_paychecks, 'Period 1')
        period2_stats = calculate_period_stats(period2_paychecks, 'Period 2')
        
        # Calculate changes between periods
        changes = {}
        if period1_stats['total_gross'] > 0:
            changes['gross_change'] = round(
                ((period2_stats['total_gross'] - period1_stats['total_gross']) / period1_stats['total_gross'] * 100), 2
            )
        if period1_stats['total_net'] > 0:
            changes['net_change'] = round(
                ((period2_stats['total_net'] - period1_stats['total_net']) / period1_stats['total_net'] * 100), 2
            )
        changes['tax_rate_change'] = round(period2_stats['avg_tax_rate'] - period1_stats['avg_tax_rate'], 2)
        changes['retirement_rate_change'] = round(period2_stats['avg_retirement_rate'] - period1_stats['avg_retirement_rate'], 2)
        
        return make_response(jsonify({
            'period1': {
                **period1_stats,
                'date_range': {
                    'start': period1_start.isoformat(),
                    'end': period1_end.isoformat()
                }
            },
            'period2': {
                **period2_stats,
                'date_range': {
                    'start': period2_start.isoformat(),
                    'end': period2_end.isoformat()
                }
            },
            'changes': changes
        }), 200)