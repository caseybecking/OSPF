from datetime import datetime
from app import db
from api.base.models import Base


class PaycheckModel(Base):
    """
    PaycheckModel represents the paycheck table in the database.
    
    This model tracks detailed paycheck information including gross income,
    net pay, taxes, deductions, and retirement contributions for analysis
    and reporting purposes.

    Attributes:
        user_id (str): The ID of the user associated with the paycheck.
        employee_name (str): Name of the employee (e.g., "Casey", "Spouse", "Self").
        employer (str): The name of the employer/company.
        pay_period_start (datetime): Start date of the pay period.
        pay_period_end (datetime): End date of the pay period.
        pay_date (datetime): Date the paycheck was received.
        gross_income (float): Total gross income before deductions.
        net_pay (float): Final take-home pay after all deductions.
        federal_tax (float): Federal income tax withheld.
        state_tax (float): State income tax withheld.
        social_security_tax (float): Social Security tax withheld.
        medicare_tax (float): Medicare tax withheld.
        other_taxes (float): Other taxes withheld.
        health_insurance (float): Health insurance deduction.
        dental_insurance (float): Dental insurance deduction.
        vision_insurance (float): Vision insurance deduction.
        voluntary_life_insurance (float): Voluntary life insurance deduction.
        retirement_401k (float): 401k contribution amount.
        retirement_403b (float): 403b contribution amount.
        retirement_ira (float): IRA contribution amount.
        other_deductions (float): Other miscellaneous deductions.
        hours_worked (float): Total hours worked in pay period.
        hourly_rate (float): Hourly rate if applicable.
        overtime_hours (float): Overtime hours worked.
        overtime_rate (float): Overtime hourly rate.
        bonus (float): Bonus amount if applicable.
        commission (float): Commission amount if applicable.
        notes (text): Additional notes about the paycheck.
        
    Calculated Properties:
        taxable_income (float): Gross income minus pre-tax deductions.
        effective_tax_rate (float): Total tax rate as percentage of taxable income.
        federal_tax_rate (float): Federal tax rate as percentage of taxable income.
        state_tax_rate (float): State tax rate as percentage of taxable income.
        total_taxes (float): Sum of all tax deductions.
        total_deductions (float): Sum of all deductions including taxes.
        total_retirement (float): Sum of all retirement contributions.
        retirement_contribution_rate (float): Retirement rate as percentage of gross income.
    """

    __tablename__ = 'paycheck'
    
    # User relationship
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='paychecks')
    
    # Basic paycheck information
    employee_name = db.Column(db.String(100), nullable=False, default='Self')
    employer = db.Column(db.String(255), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    
    # Income amounts
    gross_income = db.Column(db.Float, nullable=False)
    net_pay = db.Column(db.Float, nullable=False)
    
    # Tax deductions
    federal_tax = db.Column(db.Float, nullable=True, default=0.0)
    state_tax = db.Column(db.Float, nullable=True, default=0.0)
    social_security_tax = db.Column(db.Float, nullable=True, default=0.0)
    medicare_tax = db.Column(db.Float, nullable=True, default=0.0)
    other_taxes = db.Column(db.Float, nullable=True, default=0.0)
    
    # Insurance deductions
    health_insurance = db.Column(db.Float, nullable=True, default=0.0)
    dental_insurance = db.Column(db.Float, nullable=True, default=0.0)
    vision_insurance = db.Column(db.Float, nullable=True, default=0.0)
    voluntary_life_insurance = db.Column(db.Float, nullable=True, default=0.0)
    
    # Retirement contributions
    retirement_401k = db.Column(db.Float, nullable=True, default=0.0)
    retirement_403b = db.Column(db.Float, nullable=True, default=0.0)
    retirement_ira = db.Column(db.Float, nullable=True, default=0.0)
    
    # Other deductions
    other_deductions = db.Column(db.Float, nullable=True, default=0.0)
    
    # Work details
    hours_worked = db.Column(db.Float, nullable=True)
    hourly_rate = db.Column(db.Float, nullable=True)
    overtime_hours = db.Column(db.Float, nullable=True, default=0.0)
    overtime_rate = db.Column(db.Float, nullable=True)
    
    # Additional income
    bonus = db.Column(db.Float, nullable=True, default=0.0)
    commission = db.Column(db.Float, nullable=True, default=0.0)
    
    # Notes
    notes = db.Column(db.Text, nullable=True)

    def __init__(self, user_id, employer, pay_period_start, pay_period_end, pay_date, gross_income, net_pay,
                 employee_name='Self', federal_tax=0.0, state_tax=0.0, social_security_tax=0.0, medicare_tax=0.0, other_taxes=0.0,
                 health_insurance=0.0, dental_insurance=0.0, vision_insurance=0.0, voluntary_life_insurance=0.0,
                 retirement_401k=0.0, retirement_403b=0.0, retirement_ira=0.0, other_deductions=0.0,
                 hours_worked=None, hourly_rate=None, overtime_hours=0.0, overtime_rate=None,
                 bonus=0.0, commission=0.0, notes=None):
        """
        Initialize a new paycheck record.
        
        Args:
            user_id: ID of the user this paycheck belongs to
            employer: Name of the employer/company
            pay_period_start: Start date of the pay period
            pay_period_end: End date of the pay period
            pay_date: Date the paycheck was issued
            gross_income: Total income before deductions
            net_pay: Take-home pay after all deductions
            employee_name: Name of the employee (default: 'Self')
            federal_tax: Federal tax withheld (default: 0.0)
            state_tax: State tax withheld (default: 0.0)
            social_security_tax: Social Security tax withheld (default: 0.0)
            medicare_tax: Medicare tax withheld (default: 0.0)
            other_taxes: Other taxes withheld (default: 0.0)
            health_insurance: Health insurance deduction (default: 0.0)
            dental_insurance: Dental insurance deduction (default: 0.0)
            vision_insurance: Vision insurance deduction (default: 0.0)
            voluntary_life_insurance: Voluntary life insurance deduction (default: 0.0)
            retirement_401k: 401k contribution (default: 0.0)
            retirement_403b: 403b contribution (default: 0.0)
            retirement_ira: IRA contribution (default: 0.0)
            other_deductions: Other deductions (default: 0.0)
            hours_worked: Hours worked in pay period (optional)
            hourly_rate: Hourly pay rate (optional)
            overtime_hours: Overtime hours worked (default: 0.0)
            overtime_rate: Overtime pay rate (optional)
            bonus: Bonus amount (default: 0.0)
            commission: Commission amount (default: 0.0)
            notes: Additional notes (optional)
        """
        self.user_id = user_id
        self.employee_name = employee_name
        self.employer = employer
        self.pay_period_start = pay_period_start
        self.pay_period_end = pay_period_end
        self.pay_date = pay_date
        self.gross_income = gross_income
        self.net_pay = net_pay
        self.federal_tax = federal_tax
        self.state_tax = state_tax
        self.social_security_tax = social_security_tax
        self.medicare_tax = medicare_tax
        self.other_taxes = other_taxes
        self.health_insurance = health_insurance
        self.dental_insurance = dental_insurance
        self.vision_insurance = vision_insurance
        self.voluntary_life_insurance = voluntary_life_insurance
        self.retirement_401k = retirement_401k
        self.retirement_403b = retirement_403b
        self.retirement_ira = retirement_ira
        self.other_deductions = other_deductions
        self.hours_worked = hours_worked
        self.hourly_rate = hourly_rate
        self.overtime_hours = overtime_hours
        self.overtime_rate = overtime_rate
        self.bonus = bonus
        self.commission = commission
        self.notes = notes

    def __repr__(self):
        """
        Return a string representation of the PaycheckModel instance.

        Returns:
            str: String representation of the paycheck.
        """
        return f'<Paycheck {self.id!r} - {self.employee_name} - {self.employer} - {self.pay_date}>'

    def to_dict(self):
        """
        Convert the PaycheckModel instance to a dictionary.

        Returns:
            dict: Dictionary representation of the paycheck.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_name': self.employee_name,
            'employer': self.employer,
            'pay_period_start': self.pay_period_start.isoformat() if self.pay_period_start else None,
            'pay_period_end': self.pay_period_end.isoformat() if self.pay_period_end else None,
            'pay_date': self.pay_date.isoformat() if self.pay_date else None,
            'gross_income': self.gross_income,
            'net_pay': self.net_pay,
            'federal_tax': self.federal_tax,
            'state_tax': self.state_tax,
            'social_security_tax': self.social_security_tax,
            'medicare_tax': self.medicare_tax,
            'other_taxes': self.other_taxes,
            'health_insurance': self.health_insurance,
            'dental_insurance': self.dental_insurance,
            'vision_insurance': self.vision_insurance,
            'voluntary_life_insurance': self.voluntary_life_insurance,
            'retirement_401k': self.retirement_401k,
            'retirement_403b': self.retirement_403b,
            'retirement_ira': self.retirement_ira,
            'other_deductions': self.other_deductions,
            'hours_worked': self.hours_worked,
            'hourly_rate': self.hourly_rate,
            'overtime_hours': self.overtime_hours,
            'overtime_rate': self.overtime_rate,
            'bonus': self.bonus,
            'commission': self.commission,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_taxes': self.total_taxes,
            'total_deductions': self.total_deductions,
            'total_retirement': self.total_retirement,
            'taxable_income': self.taxable_income,
            'calculated_net_pay': self.calculated_net_pay,
            'net_pay_difference': self.net_pay_difference,
            'net_pay_matches': self.net_pay_matches,
            'effective_tax_rate': self.effective_tax_rate,
            'federal_tax_rate': self.federal_tax_rate,
            'state_tax_rate': self.state_tax_rate,
            'retirement_contribution_rate': self.retirement_contribution_rate
        }

    @property
    def total_taxes(self):
        """Calculate total taxes withheld."""
        return (self.federal_tax + self.state_tax + self.social_security_tax + 
                self.medicare_tax + self.other_taxes)

    @property
    def total_deductions(self):
        """Calculate total deductions (taxes + insurance + other)."""
        return (self.total_taxes + self.health_insurance + self.dental_insurance + 
                self.vision_insurance + self.voluntary_life_insurance + self.other_deductions)

    @property
    def total_retirement(self):
        """Calculate total retirement contributions."""
        return self.retirement_401k + self.retirement_403b + self.retirement_ira

    @property
    def taxable_income(self):
        """Calculate taxable income (gross income minus pre-tax deductions)."""
        pre_tax_deductions = (self.total_retirement + self.health_insurance + 
                            self.dental_insurance + self.vision_insurance + 
                            self.voluntary_life_insurance)
        return self.gross_income - pre_tax_deductions

    @property
    def effective_tax_rate(self):
        """Calculate effective tax rate as percentage of taxable income."""
        if self.taxable_income > 0:
            return round((self.total_taxes / self.taxable_income) * 100, 2)
        return 0.0

    @property
    def federal_tax_rate(self):
        """Calculate federal tax rate as percentage of taxable income."""
        if self.taxable_income > 0:
            return round((self.federal_tax / self.taxable_income) * 100, 2)
        return 0.0

    @property
    def state_tax_rate(self):
        """Calculate state tax rate as percentage of taxable income."""
        if self.taxable_income > 0:
            return round((self.state_tax / self.taxable_income) * 100, 2)
        return 0.0

    @property
    def calculated_net_pay(self):
        """Calculate net pay as gross income minus total deductions."""
        return round(self.gross_income - self.total_deductions, 2)

    @property
    def net_pay_difference(self):
        """Calculate difference between entered net pay and calculated net pay."""
        return round(self.net_pay - self.calculated_net_pay, 2)

    @property
    def net_pay_matches(self):
        """Check if entered net pay matches calculated net pay (within $0.01)."""
        return abs(self.net_pay_difference) <= 0.01

    @property
    def retirement_contribution_rate(self):
        """Calculate retirement contribution rate as percentage."""
        if self.gross_income > 0:
            return round((self.total_retirement / self.gross_income) * 100, 2)
        return 0.0

    def save(self):
        """
        Save the PaycheckModel instance to the database.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete the PaycheckModel instance from the database.
        """
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_user_id(cls, user_id):
        """Get all paychecks for a specific user."""
        return cls.query.filter_by(user_id=user_id).order_by(cls.pay_date.desc()).all()

    @classmethod
    def get_by_date_range(cls, user_id, start_date, end_date):
        """Get paychecks for a user within a date range."""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.pay_date >= start_date,
            cls.pay_date <= end_date
        ).order_by(cls.pay_date.desc()).all()

    @classmethod
    def get_by_employer(cls, user_id, employer):
        """Get paychecks for a specific employer."""
        return cls.query.filter_by(user_id=user_id, employer=employer)\
                       .order_by(cls.pay_date.desc()).all()

    @classmethod
    def get_by_employee(cls, user_id, employee_name):
        """Get paychecks for a specific employee."""
        return cls.query.filter_by(user_id=user_id, employee_name=employee_name)\
                       .order_by(cls.pay_date.desc()).all()