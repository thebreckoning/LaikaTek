#!/usr/bin/python3
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, ValidationError, SelectField, TimeField, FieldList, FormField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets import Input
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

class TimeInput(Input):
    def __init__(self):
        super().__init__()

    def __call__(self, field, **kwargs):
        format = '%I:%M %p'  # Set the format for 12-hour time with AM/PM
        if field.data:
            field.data = field.data.strftime(format)
        return super().__call__(field, **kwargs)

class AddDeviceForm(FlaskForm):
    nickname = StringField('Nickname:', validators=[DataRequired(), Length(max=50)])
    device_type = SelectField('Device Type:', choices=["Pet Feeder", "Pet Cam", "E-Collar"])
    feedtimes = FieldList(TimeField('Feed Time:', format='%H:%M'), min_entries=1)
    submit = SubmitField('Add Device')
    
class AddFeedTimeForm(FlaskForm):
    time = TimeField('Feed Time:', widget=TimeInput())
    am_pm = SelectField('AM/PM:', choices=[('AM', 'AM'), ('PM', 'PM')])
    submit = SubmitField('Add Feed Time')
    
class EditDeviceForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired(), Length(max=50)])
    device_type = SelectField('device_options', choices=["Pet Feeder", "Pet Cam", "E-Collar"])
    feedtimes = FieldList(FormField(AddFeedTimeForm))
    submit = SubmitField('Update')

class EditFeedTimeForm(FlaskForm):
    time = TimeField('Feed Time:', widget=TimeInput())
    #am_pm = SelectField('AM/PM:', choices=[('AM', 'AM'), ('PM', 'PM')])
    submit = SubmitField('Update Feed Time')



