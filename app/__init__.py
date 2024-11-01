# Baseline
from app.config import Config
from app.database import db
# Flask
from flask import Flask
from flask import g
from flask_restx import Api
from flask_login import LoginManager

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

        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(str(user_id))

    app.running = True

    return app
