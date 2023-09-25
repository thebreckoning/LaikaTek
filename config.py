import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
# from keymaster import db_special_password, db_root_password

load_dotenv()

DB_SPECIAL_USER = os.environ.get('DB_SPECIAL_USER')
DB_SPECIAL_PASSWORD = os.environ.get('DB_SPECIAL_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_HOST_PORT = os.environ.get('DB_HOST_PORT')
DB_CONTAINER_NAME = os.environ.get('DB_CONTAINER')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some_secret_key'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'some_default_value'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_SPECIAL_USER}:{DB_SPECIAL_PASSWORD}@{DB_HOST}:{DB_HOST_PORT}/{DB_CONTAINER_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
#  
class DevelopmentConfig(Config):
    DEBUG = True

config_mapping = {
    'development': DevelopmentConfig,
    #'production': ProductionConfig,
}

def create_connection():
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_mapping.get(env, DevelopmentConfig)
