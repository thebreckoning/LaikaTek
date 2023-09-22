#!/usr/bin/python3
# app.py

import os
import random
import string
# Flasky things
from flask import Flask, cli, render_template, request, redirect, session, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
#from flask_mysqldb import MySQL
#from dotenv import load_dotenv

# Other Helpful Libraries
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta

# Local Modules
from config import Config
from db_connection import create_connection
from models import db, User, Pet, Device, FeedTime
from forms import AddPetForm, EditPetForm, AddDeviceForm, EditDeviceForm, AddFeedTimeForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

# Set the configuration from the config.py file
app.config.from_object('config.Config')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'lt_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://thebreckoning:changepassword@db:3306/lt_data'
#load_dotenv()

db.init_app(app)

with app.app_context():
    db.create_all()

##########################################
# This section is for generating basic
# page templates
##########################################

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



##########################################
# Login and session management functions
##########################################

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#login_manager.login_view = 'login'

# User account
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    pets = owned_pets()
    devices = owned_devices()
    if current_user.is_authenticated:
        return render_template('dashboard.html', user=current_user,devices=devices, pets=pets)
    else:
        return redirect('/login')
    

#################################
# Log in/out
################################

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.user_id == int(user_id)).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')  # For redirecting to the requested page before login
            return redirect(next_page or 'dashboard')
        else:
            return 'Invalid credentials', 401
     # On successful login:
  
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/get_active_user', methods=['GET'])
def get_active_user():
    # Extract user_id from the current session
    user_id = session.get('user_id')

    # Check if user_id exists in the session
    if user_id:
        active_user = user_id
        return f'Active User is: {active_user}', 200
    else:
        return 'No user_id found in the session', 404

################################
# Create account
################################

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        email_address = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Choose another.')
            return redirect(url_for('create_account'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='scrypt')

        # Create a new user
        new_user = User(
            username=username,
            password=hashed_password,
            email_address=email_address,
        )

        db.session.add(new_user)
        db.session.commit()

        
        # Start a new session for the user using Flask-Login's login_user function
        login_user(new_user)

        # Redirect user to their account page
        return redirect(url_for('dashboard'))
    # Render the create_account.html template for GET requests
    return render_template('create_account.html')


    #######################################
    # Pet Handler functions
    #######################################


# Add a new pet
@app.route('/add_pet', methods=['GET', 'POST'])

def add_pet():
    if request.method == 'POST':
        print("Form Submitted")
        print(request.form) 

    form = AddPetForm()
    if form.validate_on_submit():
            #owner = session['user_id']
            new_pet = Pet(
                name=request.form['name'],
                breed=request.form['breed'],
                weight=int(request.form['weight']),
                owner=current_user.user_id,
                #pet_profile_pic=choose_random_profile_pic() 
            )
            db.session.add(new_pet)
            db.session.commit()
            flash('Pet added successfully!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('add_pet.html', form=form)

# Fetch pets
def owned_pets():
    if current_user.is_authenticated:
        return Pet.query.filter_by(owner=current_user.user_id).all()
    else:
        return []
    
def get_pet_by_id(pet_id):
    return Pet.query.get(pet_id)

def update_pet(pet):
    try:
        db.session.commit()
    except Exception as e:
        # Handle exception (you might want to log this error and/or rollback the session)
        db.session.rollback()
        raise e
def choose_random_profile_pic():
    profile_pics = [
        "./templates/images/pet_profile_images/pet_prof_01.jpg",
        "./templates/images/pet_profile_images/pet_prof_02.jpg",
        "./templates/images/pet_profile_images/pet_prof_03.jpg",
        "./templates/images/pet_profile_images/pet_prof_04.jpg",
        "./templates/images/pet_profile_images/pet_prof_05.jpg",
        "./templates/images/pet_profile_images/pet_prof_06.jpg",
        "./templates/images/pet_profile_images/pet_prof_07.jpg",
        "./templates/images/pet_profile_images/pet_prof_08.jpg",
        "./templates/images/pet_profile_images/pet_prof_09.jpg"
    ]
    return random.choice(profile_pics)


@app.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    pet = Pet.query.get(pet_id)
    form = EditPetForm()

    if request.method == 'GET':
        form.name.data = pet.name
        form.breed.data = pet.breed
        form.weight.data = pet.weight

    if form.validate_on_submit():
        # Save the changes to the pet in the database.
        pet.name = form.name.data
        pet.breed = form.breed.data
        pet.weight = form.weight.data
        db.session.commit()
        
        update_pet(pet)  # update the pet in the database
        return redirect(url_for('dashboard'))  

    return render_template('edit_pet.html', pet=pet, form=form)

@app.route('/delete_pet/<int:pet_id>', methods=['POST'])
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet:
        db.session.delete(pet)
        db.session.commit()
        flash('pet deleted successfully!', 'success')
    else:
        flash('pet not found!', 'error')
    return redirect(url_for('dashboard'))

# Set the my_pet function

@app.route('/mypets')
def my_pets():
    pets = owned_pets()
    return render_template('mypets.html', user_pets=pets)



    #######################################
    # Device Handler functions
    #######################################

# Add a new device
@app.route('/add_device', methods=['GET', 'POST'])
def add_device():

    if request.method == 'POST':
        print("Form Submitted")
        print(request.form) 

    form = AddDeviceForm()
    if form.validate_on_submit():
            new_device = Device(
                nickname=request.form['nickname'],
                device_type=request.form['device_type'],
                owner=current_user.user_id 
            )
            db.session.add(new_device)
            db.session.commit()
            flash('Device added successfully!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('add_device.html', form=form)

# Fetch devices
def owned_devices():
    if current_user.is_authenticated:
        return Device.query.filter_by(owner=current_user.user_id).all()
    else:
        return []
    
def get_device_by_id(device_id):
    return Device.query.get(device_id)

def update_device(device):
    try:
        db.session.commit()
    except Exception as e:
        # Handle exception (you might want to log this error and/or rollback the session)
        db.session.rollback()
        raise e
    
@app.route('/edit_device/<int:device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    device = Device.query.get(device_id)
    form = EditDeviceForm()

    if request.method == 'GET':
        form.nickname.data = device.nickname
        form.device_type.data = device.device_type

    if form.validate_on_submit():
        # Save the changes to the device in the database.
        device.nickname = form.nickname.data
        device.device_type = form.device_type.data
        db.session.commit()
        
        update_device(device)  # update the device in the database
        return redirect(url_for('dashboard'))  

    return render_template('edit_device.html', device=device, form=form)


@app.route('/delete_device/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        flash('Device deleted successfully!', 'success')
    else:
        flash('Device not found!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/mydevices')
def my_devices():
    devices = owned_devices()
    return render_template('devices.html', user_devices=devices)

# The feed time values for each device are stored in a separate 
# database so we can add multiple feed times for each device 
# with scalability.

@app.route('/add_feed_time/<int:device_id>', methods=['GET', 'POST'])
def add_feed_time(device_id):
    form = AddFeedTimeForm()
    device = Device.query.get_or_404(device_id)
    if form.validate_on_submit():
        new_feed_time = FeedTime(time=form.feed_time.data, device_id=device_id)
        db.session.add(new_feed_time)
        db.session.commit()
        flash('Feed time added!')
        return redirect(url_for('devices_page'))
    return render_template('add_feed_time.html', form=form)



    #########################################
    # Database things. Creation and syncing
    #########################################



    ########################################################################
    # Create missing tables and columns in the database 
    # based on the models.py file.
    ########################################################################
    
def sync_database():
    with app.app_context():
        db.create_all()
   
if __name__ == '__main__':
    sync_database()
    app.run()
    
