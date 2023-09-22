#!/usr/bin/python3

# db_connection.py
import mariadb
from mariadb import Error
#from azure.identity import DefaultAzureCredential
#from azure.keyvault.secrets import SecretClient

def create_connection():
    try:
        connection = mariadb.connect(
            host='lt_data', 
            port=3306,
            user='thebreckoning',
            password='changepassword',
            database='lt_data'
        )
        return connection
    except Error as e:
        print("Error while connecting to MariaDB:", e)
        return None
