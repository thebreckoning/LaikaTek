#!/usr/bin/python3
#forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, ValidationError, SelectField, TimeField, FieldList, FormField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
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


class AddDeviceForm(FlaskForm):
    nickname = StringField('Nickname:', validators=[DataRequired(), Length(max=50)])
    device_type = SelectField('Device Type:', choices=["Pet Feeder", "Pet Cam", "E-Collar"])
    feedtimes = FieldList(TimeField('Feed Time:', format='%H:%M'), min_entries=1)
    submit = SubmitField('Add Device')
    
class AddFeedTimeForm(FlaskForm):
    hours = SelectField('Hours', choices=[(str(i), str(i)) for i in range(1, 13)])
    minutes = SelectField('Minutes', choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(60)])
    ampm = SelectField('AM/PM', choices=[('AM', 'AM'), ('PM', 'PM')])
    

class NewDeviceForm(FlaskForm):
    nickname = StringField('Nickname:', validators=[DataRequired(), Length(max=50)])
    device_type = SelectField('Device Type:', choices=["Pet Feeder", "Pet Cam", "E-Collar"])
    feedtimes = FieldList(TimeField('Feed Time:', format='%H:%M'), min_entries=1)
    portions = FieldList(FloatField('Portions:', validators=[DataRequired(), NumberRange(min=0.5, max=6)]), min_entries=1)
    submit = SubmitField('Add Device')
    
class EditDeviceForm(FlaskForm):
    nickname = StringField('Nickname:', validators=[DataRequired(), Length(max=50)])
    device_type = SelectField('Device Type:', choices=["Pet Feeder", "Pet Cam", "E-Collar"])
    feedtimes = FieldList(FormField(AddFeedTimeForm), min_entries=1)
    submit = SubmitField('Update')

    def add_feed_time(self):
        feed_time_form = AddFeedTimeForm()
        self.feedtimes.append_entry(feed_time_form)

class EditFeedTimeForm(FlaskForm):
    time = TimeField('Feed Time:')
    #am_pm = SelectField('AM/PM:', choices=[('AM', 'AM'), ('PM', 'PM')])
    submit = SubmitField('Update Feed Time')



