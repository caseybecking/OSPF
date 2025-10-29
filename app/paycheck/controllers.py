from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from api.paycheck.models import PaycheckModel

paychecks = Blueprint('paychecks', __name__)

@paychecks.route('/paychecks')
@login_required
def index():
    """Display list of user's paychecks"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 paychecks per page
    
    paychecks_query = PaycheckModel.query.filter_by(user_id=current_user.id)\
                                        .order_by(PaycheckModel.pay_date.desc())\
                                        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('paycheck/index.html', 
                         paychecks=paychecks_query.items,
                         pagination=paychecks_query)

@paychecks.route('/paychecks/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create a new paycheck"""
    if request.method == 'POST':
        try:
            # Extract form data
            employer = request.form.get('employer')
            employee_name = request.form.get('employee_name', 'Self')
            pay_period_start = datetime.strptime(request.form.get('pay_period_start'), '%Y-%m-%d').date()
            pay_period_end = datetime.strptime(request.form.get('pay_period_end'), '%Y-%m-%d').date()
            pay_date = datetime.strptime(request.form.get('pay_date'), '%Y-%m-%d').date()
            gross_income = float(request.form.get('gross_income'))
            net_pay = float(request.form.get('net_pay'))
            
            # Optional fields
            federal_tax = float(request.form.get('federal_tax') or 0.0)
            state_tax = float(request.form.get('state_tax') or 0.0)
            social_security_tax = float(request.form.get('social_security_tax') or 0.0)
            medicare_tax = float(request.form.get('medicare_tax') or 0.0)
            other_taxes = float(request.form.get('other_taxes') or 0.0)
            health_insurance = float(request.form.get('health_insurance') or 0.0)
            dental_insurance = float(request.form.get('dental_insurance') or 0.0)
            vision_insurance = float(request.form.get('vision_insurance') or 0.0)
            voluntary_life_insurance = float(request.form.get('voluntary_life_insurance') or 0.0)
            retirement_401k = float(request.form.get('retirement_401k') or 0.0)
            retirement_403b = float(request.form.get('retirement_403b') or 0.0)
            retirement_ira = float(request.form.get('retirement_ira') or 0.0)
            other_deductions = float(request.form.get('other_deductions') or 0.0)
            
            hours_worked = request.form.get('hours_worked')
            if hours_worked and hours_worked.strip():
                hours_worked = float(hours_worked)
            else:
                hours_worked = None
            
            hourly_rate = request.form.get('hourly_rate')
            if hourly_rate and hourly_rate.strip():
                hourly_rate = float(hourly_rate)
            else:
                hourly_rate = None
                
            overtime_hours = float(request.form.get('overtime_hours') or 0.0)
            
            overtime_rate = request.form.get('overtime_rate')
            if overtime_rate and overtime_rate.strip():
                overtime_rate = float(overtime_rate)
            else:
                overtime_rate = None
                
            bonus = float(request.form.get('bonus') or 0.0)
            commission = float(request.form.get('commission') or 0.0)
            notes = request.form.get('notes')
            
            # Validate required fields
            if not all([employer, pay_period_start, pay_period_end, pay_date, gross_income, net_pay]):
                flash('All required fields must be filled out.', 'error')
                return render_template('paycheck/new.html')
            
            # Validate date logic
            if pay_period_start > pay_period_end:
                flash('Pay period start date must be before end date.', 'error')
                return render_template('paycheck/new.html')
            
            # Create new paycheck
            paycheck = PaycheckModel(
                user_id=current_user.id,
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
            
            paycheck.save()
            flash('Paycheck created successfully!', 'success')
            return redirect(url_for('paychecks.index'))
            
        except ValueError as e:
            flash('Invalid numeric values provided. Please check your input.', 'error')
        except Exception as e:
            flash(f'Error creating paycheck: {str(e)}', 'error')
    
    return render_template('paycheck/new.html')

@paychecks.route('/paychecks/<paycheck_id>')
@login_required
def detail(paycheck_id):
    """Display paycheck details"""
    paycheck = PaycheckModel.query.get_or_404(paycheck_id)
    
    # Ensure the paycheck belongs to the current user
    if paycheck.user_id != current_user.id:
        flash('You do not have permission to view this paycheck.', 'error')
        return redirect(url_for('paychecks.index'))
    
    return render_template('paycheck/detail.html', paycheck=paycheck)

@paychecks.route('/paychecks/<paycheck_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(paycheck_id):
    """Edit a paycheck"""
    paycheck = PaycheckModel.query.get_or_404(paycheck_id)
    
    # Ensure the paycheck belongs to the current user
    if paycheck.user_id != current_user.id:
        flash('You do not have permission to edit this paycheck.', 'error')
        return redirect(url_for('paychecks.index'))
    
    if request.method == 'POST':
        try:
            # Update fields from form
            paycheck.employer = request.form.get('employer')
            paycheck.employee_name = request.form.get('employee_name', 'Self')
            paycheck.pay_period_start = datetime.strptime(request.form.get('pay_period_start'), '%Y-%m-%d').date()
            paycheck.pay_period_end = datetime.strptime(request.form.get('pay_period_end'), '%Y-%m-%d').date()
            paycheck.pay_date = datetime.strptime(request.form.get('pay_date'), '%Y-%m-%d').date()
            paycheck.gross_income = float(request.form.get('gross_income'))
            paycheck.net_pay = float(request.form.get('net_pay'))
            
            # Optional fields
            paycheck.federal_tax = float(request.form.get('federal_tax') or 0.0)
            paycheck.state_tax = float(request.form.get('state_tax') or 0.0)
            paycheck.social_security_tax = float(request.form.get('social_security_tax') or 0.0)
            paycheck.medicare_tax = float(request.form.get('medicare_tax') or 0.0)
            paycheck.other_taxes = float(request.form.get('other_taxes') or 0.0)
            paycheck.health_insurance = float(request.form.get('health_insurance') or 0.0)
            paycheck.dental_insurance = float(request.form.get('dental_insurance') or 0.0)
            paycheck.vision_insurance = float(request.form.get('vision_insurance') or 0.0)
            paycheck.voluntary_life_insurance = float(request.form.get('voluntary_life_insurance') or 0.0)
            paycheck.retirement_401k = float(request.form.get('retirement_401k') or 0.0)
            paycheck.retirement_403b = float(request.form.get('retirement_403b') or 0.0)
            paycheck.retirement_ira = float(request.form.get('retirement_ira') or 0.0)
            paycheck.other_deductions = float(request.form.get('other_deductions') or 0.0)
            
            hours_worked = request.form.get('hours_worked')
            paycheck.hours_worked = float(hours_worked) if hours_worked and hours_worked.strip() else None
            
            hourly_rate = request.form.get('hourly_rate')
            paycheck.hourly_rate = float(hourly_rate) if hourly_rate and hourly_rate.strip() else None
                
            paycheck.overtime_hours = float(request.form.get('overtime_hours') or 0.0)
            
            overtime_rate = request.form.get('overtime_rate')
            paycheck.overtime_rate = float(overtime_rate) if overtime_rate and overtime_rate.strip() else None
                
            paycheck.bonus = float(request.form.get('bonus') or 0.0)
            paycheck.commission = float(request.form.get('commission') or 0.0)
            paycheck.notes = request.form.get('notes')
            
            # Validate date logic
            if paycheck.pay_period_start > paycheck.pay_period_end:
                flash('Pay period start date must be before end date.', 'error')
                return render_template('paycheck/edit.html', paycheck=paycheck)
            
            paycheck.save()
            flash('Paycheck updated successfully!', 'success')
            return redirect(url_for('paychecks.detail', paycheck_id=paycheck.id))
            
        except ValueError as e:
            flash('Invalid numeric values provided. Please check your input.', 'error')
        except Exception as e:
            flash(f'Error updating paycheck: {str(e)}', 'error')
    
    return render_template('paycheck/edit.html', paycheck=paycheck)

@paychecks.route('/paychecks/<paycheck_id>/delete', methods=['POST'])
@login_required
def delete(paycheck_id):
    """Delete a paycheck"""
    paycheck = PaycheckModel.query.get_or_404(paycheck_id)
    
    # Ensure the paycheck belongs to the current user
    if paycheck.user_id != current_user.id:
        flash('You do not have permission to delete this paycheck.', 'error')
        return redirect(url_for('paychecks.index'))
    
    try:
        paycheck.delete()
        flash('Paycheck deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting paycheck: {str(e)}', 'error')
    
    return redirect(url_for('paychecks.index'))

@paychecks.route('/paychecks/analytics')
@login_required
def analytics():
    """Display paycheck analytics dashboard"""
    # Get basic analytics data
    paychecks = PaycheckModel.query.filter_by(user_id=current_user.id)\
                                  .order_by(PaycheckModel.pay_date.desc()).all()
    
    if not paychecks:
        flash('No paychecks found. Add some paychecks to view analytics.', 'info')
        return redirect(url_for('paychecks.index'))
    
    # Calculate summary statistics
    total_paychecks = len(paychecks)
    total_gross = sum(p.gross_income for p in paychecks)
    total_net = sum(p.net_pay for p in paychecks)
    total_taxes = sum(p.total_taxes for p in paychecks)
    total_retirement = sum(p.total_retirement for p in paychecks)
    
    avg_gross = total_gross / total_paychecks
    avg_net = total_net / total_paychecks
    avg_tax_rate = (total_taxes / total_gross * 100) if total_gross > 0 else 0
    avg_retirement_rate = (total_retirement / total_gross * 100) if total_gross > 0 else 0
    
    # Group by employer
    employers = {}
    for paycheck in paychecks:
        if paycheck.employer not in employers:
            employers[paycheck.employer] = []
        employers[paycheck.employer].append(paycheck)
    
    # Monthly trends (last 12 months)
    from datetime import datetime, timedelta
    import calendar
    
    monthly_data = {}
    for paycheck in paychecks:
        month_key = f"{paycheck.pay_date.year}-{paycheck.pay_date.month:02d}"
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'count': 0,
                'total_gross': 0,
                'total_net': 0,
                'total_taxes': 0,
                'total_retirement': 0
            }
        monthly_data[month_key]['count'] += 1
        monthly_data[month_key]['total_gross'] += paycheck.gross_income
        monthly_data[month_key]['total_net'] += paycheck.net_pay
        monthly_data[month_key]['total_taxes'] += paycheck.total_taxes
        monthly_data[month_key]['total_retirement'] += paycheck.total_retirement
    
    # Get last 12 months of data
    current_date = datetime.now().date()
    monthly_trends = []
    for i in range(11, -1, -1):
        # Calculate month/year going back i months
        current_year = current_date.year
        current_month = current_date.month
        
        target_month = current_month - i
        target_year = current_year
        
        # Handle year rollover
        while target_month <= 0:
            target_month += 12
            target_year -= 1
            
        month_key = f"{target_year}-{target_month:02d}"
        
        if month_key in monthly_data:
            data = monthly_data[month_key]
            monthly_trends.append({
                'month': calendar.month_name[target_month],
                'year': target_year,
                'count': data['count'],
                'gross': data['total_gross'],
                'net': data['total_net'],
                'tax_rate': (data['total_taxes'] / data['total_gross'] * 100) if data['total_gross'] > 0 else 0,
                'retirement_rate': (data['total_retirement'] / data['total_gross'] * 100) if data['total_gross'] > 0 else 0
            })
        else:
            monthly_trends.append({
                'month': calendar.month_name[target_month],
                'year': target_year,
                'count': 0,
                'gross': 0,
                'net': 0,
                'tax_rate': 0,
                'retirement_rate': 0
            })
    
    summary = {
        'total_paychecks': total_paychecks,
        'total_gross': total_gross,
        'total_net': total_net,
        'total_taxes': total_taxes,
        'total_retirement': total_retirement,
        'avg_gross': avg_gross,
        'avg_net': avg_net,
        'avg_tax_rate': avg_tax_rate,
        'avg_retirement_rate': avg_retirement_rate
    }
    
    return render_template('paycheck/analytics.html', 
                         summary=summary,
                         employers=employers,
                         monthly_trends=monthly_trends,
                         recent_paychecks=paychecks[:5])  # Show 5 most recent