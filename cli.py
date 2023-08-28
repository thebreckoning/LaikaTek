#!/usr/bin/python3
import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from models import db  # Import the SQLAlchemy instance from your models.py
from db_connection import create_connection  

mariadb_connection = create_connection()
db.init_app(mariadb_connection)


@click.command(name='init-db')
@with_appcontext
def init_db_command():
    """Create the database tables and seed initial data."""
    db.create_all()

    # Add your code here to seed initial data if needed
    # For example:
    # user = User(username='admin', password='password')
    # db.session.add(user)
    # db.session.commit()

    click.echo('Initialized the database.')