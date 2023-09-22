#!/usr/bin/python3
# models.py

from flask_sqlalchemy import SQLAlchemy
#from flask_mysqldb import MySQLdb
from werkzeug.security import check_password_hash
from flask_login import UserMixin


db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email_address = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(10))
    street_address = db.Column(db.String(255))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.Integer)
    pets = db.relationship('Pet', backref='pet', lazy=True)
    def get_id(self):
        return str(self.user_id)
    
class Pet(db.Model):
    __tablename__ = 'pets'
    pet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    owner = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    breed = db.Column(db.String(50))
    weight = db.Column(db.Integer) 
    pet_profile_image = db.Column(db.String(50))   

class Device(db.Model):
    __tablename__ = 'devices'
    device_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(50))
    owner = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    device_type = db.Column(db.String(50))
    feed_times = db.relationship('FeedTime', backref='device', lazy=True)

class FeedTime(db.Model):
    __tablename__ = 'feed_time'
    time_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id'))
    time = db.Column(db.Time)

                        
