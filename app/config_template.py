import os

class Config(object):
    FLASK_DEBUG = True
    FLASK_ENV = 'DEVELOPMENT'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@192.168.1.1:5432/ospf?sslmode=disable'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DATABASE_CONNECT_OPTIONS = {}
    TEMPLATES_AUTO_RELOAD = True
    PASSWORD_SALT = ''
    SECRET_KEY = b'superstongsecret'
    SERVICES_LOGGING_CONFIG = 'app/logger.yml'