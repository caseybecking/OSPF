# Baseline
from app.config import Config

# Flask
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    return app