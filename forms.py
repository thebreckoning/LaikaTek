#!/usr/bin/python3
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, ValidationError, SelectField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from models import User


    #######################################
    # Cerate Account
    #######################################
class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    #######################################
    # Pet Forms
    #######################################

class AddPetForm(FlaskForm):
    name = StringField('Pet Name', validators=[DataRequired(), Length(max=50)])
    breed = StringField('Breed', validators=[DataRequired(), Length(max=50)])
    weight = IntegerField('Weight', validators=[DataRequired()])
    submit = SubmitField('Add Pet')

class EditPetForm(FlaskForm):
    name = StringField('Pet Name', validators=[DataRequired(), Length(max=50)])
    breed = StringField('Breed', validators=[DataRequired(), Length(max=50)])
    weight = IntegerField('Weight', validators=[DataRequired()])
    submit = SubmitField('Update')

    #######################################
    # Device Forms
    #######################################
class AddDeviceForm(FlaskForm):
    nickname = StringField('Nickname:', validators=[DataRequired(), Length(max=50)])
    device_type = SelectField('Device Type:', choices=["Pet Feeder", "Pet Cam", "E-Collar"])
    submit = SubmitField('add_device')

class EditDeviceForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired(), Length(max=50)])
    device_type = SelectField('device_options', choices=["Pet Feeder", "Pet Cam", "E-Collar"])
    submit = SubmitField('Update')


class AddFeedTimeForm(FlaskForm):
    feed_time = TimeField('Feed Time:', format='%H:%M')
    submit = SubmitField('Add Feed Time')