# Baseline
from app.config import Config
from app.database import db
# Flask
from flask import Flask
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
    from app.user.models import User

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    app.running = True

    return app