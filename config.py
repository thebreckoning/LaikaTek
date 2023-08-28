#!/usr/bin/python3

import os
from sqlalchemy import create_engine

class Config:
    # Secret key for Flask sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-secret-key'
    #SECRET_KEY = 'tC9vnmKmNGZHZlToTpAZpdTUCFEwlhVE'

    # Database configuration (SQLite in this example)
    #DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lt_db')
    
    #SQLALCHEMY_DATABASE_URI = 'mysql://thebreckoning:changepassword@localhost/lt_db'
    #SQLALCHEMY_DATABASE_URI = 'mysql://thebreckoning:changepassword@db/lt_db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://thebreckoning:changepassword@localhost/lt_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other configuration settings (if needed)
    # ...

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    # Additional production configuration settings (if needed)
    # ...

# Create a dictionary to map environment names to their respective configurations
    config_mapping = {
        'development': DevelopmentConfig,
        #'production': ProductionConfig,
        # Add other configurations if needed
    }
def create_connection():
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)

def get_config():
    """
    Get the configuration object based on the 'FLASK_ENV' environment variable.
    Default to DevelopmentConfig if 'FLASK_ENV' is not set.
    """
    env = os.environ.get('FLASK_ENV', 'development')
    config_mapping = {
        'development': DevelopmentConfig,
    }
    return config_mapping.get(env, DevelopmentConfig)