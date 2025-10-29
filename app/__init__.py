# Datetime
from datetime import datetime
# Flask
import babel.dates
from flask import Flask
from flask import g
# Flask Restx
from flask_restx import Namespace
from flask_restx import Api
from flask_login import LoginManager
# babel
import babel
# Baseline
from app.config import Config
from app.database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database
    db.init_app(app)

    # Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'account.login'

    # Blueprints
    from app.account.controllers import account_blueprint
    app.register_blueprint(account_blueprint)
    from app.dashboard.controllers import dashboards
    app.register_blueprint(dashboards)
    from app.institution.controllers import institution_blueprint
    app.register_blueprint(institution_blueprint)
    from app.institution_account.controllers import institution_account_blueprint
    app.register_blueprint(institution_account_blueprint)
    from app.categories.controllers import categories_blueprint
    app.register_blueprint(categories_blueprint)
    from app.transactions.controllers import transactions_blueprint
    app.register_blueprint(transactions_blueprint)
    from app.paycheck.controllers import paychecks
    app.register_blueprint(paychecks)

    # Models
    from api.user.models import User

    with app.app_context():
        g.api = Api(
            app,
            version='0.1',
            title='Open Source Personal Finance API',
            description='Open Source Personal Finance API',
            doc='/api/doc/',
            prefix='/api'
        )
        # API Controllers
        from api.account.controllers import Signup
        from api.institution.controllers import Institution
        from api.user.controllers import User as UserAPI
        from api.institution_account.controllers import InstitutionAccount
        from api.categories_group.controllers import CategoriesGroup
        from api.categories_type.controllers import CategoriesType
        from api.categories.controllers import Categories
        from api.transaction.controllers import Transaction
        from api.paycheck.controllers import Paycheck, PaycheckDetail, PaycheckAnalytics, PaycheckTrends, PaycheckCompare

        #CLI
        from app.cli import insert_categories
        @app.cli.command('insert-categories')
        def insert_cat():
            insert_categories()

        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(str(user_id))

    app.running = True


    @app.template_filter()
    def format_datetime(value, _format='medium'):
        _value = datetime.strptime(value, '%a, %d %b %Y %H:%M:%S %Z')
        if _format == 'full':
            _format="EEEE, d. MMMM y 'at' HH:mm"
        elif _format == 'medium':
            _format="EE dd.MM.y HH:mm"
        elif _format == 'short':
            _format="MM/dd/YYYY"
        return babel.dates.format_datetime(_value, _format)

    return app
