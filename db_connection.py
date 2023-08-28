#!/usr/bin/python3

# db_connection.py
import mariadb
from mariadb import Error

def create_connection():
    try:
        connection = mariadb.connect(
            host='localhost', 
            port=3306,
            user='thebreckoning',
            password='changepassword',
            database='lt_db'
        )
        return connection
    except Error as e:
        print("Error while connecting to MariaDB:", e)
        return None