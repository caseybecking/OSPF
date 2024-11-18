# Flask
from flask import Flask
from flask import g
# Flask Restx
from flask_restx import Namespace
from flask_restx import Api
from flask_login import LoginManager
# Baseline
from app.config import Config
from app.database import db
# CSV
import csv

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

    return app
