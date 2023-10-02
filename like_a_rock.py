#!/usr/bin/python3
#likearock.py

import mariadb
import sys
from key_master import get_secret

# Function(s) to update/harden the database passwords

def update_passwords():
    try:
        # Connect to MariaDB
        conn = mariadb.connect(
            user=DB_SPECIAL_USER,
            password=get_secret("mariadb_root_password"),
            host="localhost",
            port=3306,
            database="mydb"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

    # Get the special user's current password
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username='special_user'")
    current_password = cur.fetchone()[0]

    # Update the special user's password to use the key vault value
    new_password = get_secret("special_user_password")
    cur.execute("UPDATE users SET password=? WHERE username='special_user'", (new_password,))

    # Update the root user's password to use the key vault value
    cur.execute(f"SET PASSWORD FOR 'root'@'localhost' = '{get_secret('mariadb_root_password')}'")

    conn.commit()
    conn.close()
    
    from dotenv import load_dotenv
    import os

    load_dotenv()

    DB_SPECIAL_USER = os.getenv("DB_SPECIAL_USER")

if __name__ == "__main__":
    update_passwords()
