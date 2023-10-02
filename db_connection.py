#!/usr/bin/python3
# db_connection.py

# db_connection.py
import mariadb
from mariadb import Error
#from keymaster import db_password

def create_connection():
    try:
        connection = mariadb.connect(
            host='DB_HOST',
            port='DB_HOST_PORT',
            user='DB_SPECIAL_USER',
            password='DB_SPECIAL_PASSWORD',
            database='DB_NAME'
        )
        return connection
    except Error as e:
        print("Error while connecting to MariaDB:", e)
        return None
