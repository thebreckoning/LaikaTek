#!/usr/bin/python3
# db_config.py


#from models import db, User, Pet, Device
import mariadb
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
#from keymaster import db_special_password, db_root_password

load_dotenv()

DB_SPECIAL_USER = os.environ.get('DB_SPECIAL_USER')
DB_SPECIAL_PASSWORD = os.environ.get('DB_SPECIAL_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_HOST_PORT = os.environ.get('DB_HOST_PORT')
DB_CONTAINER_NAME = os.environ.get('DB_CONTAINER')

################################################################
# Create database connection
################################################################

def create_connection():
    try:
        connection = mariadb.connector.connect(
            host='DB_HOST',
            port='DB_HOST_PORT',
            user='DB_SPECIAL_USER',
            password='DB_SPECIAL_PASSWORD',
            database='DB_NAME'
        )
        return connection
    except mariadb.connector.Error as e:
        print("Error while connecting to MySQL:", e)
        return None

    #######################################
    # Database things creation and syncing
    #######################################

    ########################################################################
    #Get a list of all table names defined in the models.py file.
    ########################################################################
def get_table_names():
    metadata = db.metadata
    result = {}
    for table_name, table in metadata.tables.items():
        column_names = [column.name for column in table.columns]
        result[table_name] = column_names
    return result
    ########################################################################
    # Create missing tables and columns in the database 
    # based on the models.py file.
    ########################################################################
    
def sync_database():
    with db.app_context():
        # Get a list of all table names defined in models.py
        model_table_names = get_table_names()

        # Get a list of all table names present in the database
        cursor = db.connection.cursor()
        cursor.execute("SHOW TABLES;")
        db_table_names = [table[0] for table in cursor.fetchall()]

        # Create missing tables in the database
        for table_name in model_table_names:
            if table_name not in db_table_names:
                cursor.execute(f"CREATE TABLE {table_name} (id INT PRIMARY KEY AUTO_INCREMENT);")
                print(f"Created table '{table_name}' in the database.")

    
    # Get a list of all table names present in the database
    result_proxy = db.session.execute("SHOW TABLES;")
    db_table_names = [row[0] for row in result_proxy.fetchall()]

    # Create missing tables in the database
    for table_name in model_table_names:
        if table_name not in db_table_names:
            db.session.execute(f"CREATE TABLE {table_name} (id INT PRIMARY KEY AUTO_INCREMENT);")
            print(f"Created table '{table_name}' in the database.")

    # Save changes
    db.session.commit()

    # Close the cursor and commit changes
    cursor.close()
    db.connection.commit()
