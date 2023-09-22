import os
from sqlalchemy import create_engine

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'mysql+pymysql://thebreckoning:changepassword@db:3306/lt_data'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    # Additional production-specific settings can be added here
    pass

config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

def create_connection():
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_mapping.get(env, DevelopmentConfig)
