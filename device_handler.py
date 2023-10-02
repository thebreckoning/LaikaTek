from datetime import datetime
from flask import request, flash, redirect, url_for, render_template, Blueprint, jsonify
from flask_login import current_user, login_required
from models import db, Device, FeedTime
from forms import AddDeviceForm,AddFeedTimeForm, EditDeviceForm, EditFeedTimeForm
from sqlalchemy.exc import SQLAlchemyError


# Blueprint for adding and editing user devices
device_handler_bp = Blueprint('device_handler', __name__)

####### Fetching existing devices #######

@device_handler_bp.route('/owned_devices')
def owned_devices():
    if current_user.is_authenticated:
        return Device.query.filter_by(owner=current_user.user_id).all()
    else:
        return []
    
####### Adding new devices #######
@device_handler_bp.route('/add_device', methods=['GET', 'POST'])
def add_device():
    d_form = AddDeviceForm()
    f_form = AddFeedTimeForm()

    try:
        if request.method == 'POST':
            if d_form.validate_on_submit() and f_form.validate_on_submit():
                # Create a new device
                new_device = Device(
                    nickname=d_form.nickname.data,
                    device_type=d_form.device_type.data,
                    owner=current_user.user_id,
                )

                db.session.add(new_device)
                db.session.commit()

                # Extract feed times from the feedtime form
                hours = request.form.get('hours')  # Get the selected hours as a string
                minutes = request.form.get('minutes')  # Get the selected minutes as a string
                ampm = request.form.get('ampm')  # Get AM or PM as a string

                # Convert the input to HH:MM:SS format
                time_input = f'{hours}:{minutes}:00 {ampm}'

                try:
                    # Convert to a time string in HH:MM:SS format (assuming a valid time format)
                    time_obj = datetime.strptime(time_input, '%I:%M:%S %p').strftime('%H:%M:%S')

                    # Add feed time to the device
                    new_feedtime = FeedTime(
                        device_id=new_device.device_id,
                        time=time_obj,
                    )
                    db.session.add(new_feedtime)
                except ValueError:
                    flash(f'Invalid time format: {time_input}', 'error')

                db.session.commit()

                flash('Device added successfully!', 'success')
                return redirect(url_for('dashboard'))
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback the transaction in case of a database error
        flash('Database error occurred. Please try again later.', 'error')
        # You can also log the error for debugging purposes
        print(f'Database error: {str(e)}')

    return render_template('add_device.html', d_form=d_form, f_form=f_form)

####### Editing existing devices ########

@device_handler_bp.route('/edit_device/<int:device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    device = Device.query.get(device_id)
    form = EditDeviceForm(obj=device)  # Populate the form with device data

    if request.method == 'POST' and form.validate_on_submit():
        update_device_details(device, form)
        update_feedtimes(device_id, request.form.getlist('feedtimes'))
        
        db.session.commit()
        flash('Device updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    # Load the existing feed times associated with the device
    existing_feedtimes = FeedTime.query.filter_by(device_id=device_id).all()

    return render_template('edit_device.html', device=device, form=form, existing_feedtimes=existing_feedtimes)

# Update the device details in the database
def update_device_details(device, form):  
    form.populate_obj(device)

# Update the associated feed times for the device.
def update_feedtimes(device_id, updated_feedtimes):   
    existing_feedtimes = FeedTime.query.filter_by(device_id=device_id).all()

    # Remove any existing feed times not present in the updated list
    for feedtime in existing_feedtimes:
        if feedtime.time not in updated_feedtimes:
            db.session.delete(feedtime)

    # Add new feed times and update existing ones
    for time in updated_feedtimes:
        existing_time = FeedTime.query.filter_by(device_id=device_id, time=time).first()
        if not existing_time:
            new_time = FeedTime(device_id=device_id, time=time)
            db.session.add(new_time)
            
            
###### Delete device ########
@device_handler_bp.route('/delete_device/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        flash('Device deleted successfully!', 'success')
    else:
        flash('Device not found!', 'error')
    return redirect(url_for('dashboard'))

### Deleting feed times ###

@device_handler_bp.route('/delete_feedtime/<int:feedtime_id>', methods=['POST'])
def delete_feedtime(feedtime_id):
    feedtime = FeedTime.query.get(feedtime_id)
    
    if not feedtime:
        flash('Feed time not found!', 'error')
        return redirect(url_for('dashboard'))  # Redirect to a default page if feedtime not found

    try:
        db.session.delete(feedtime)
        db.session.commit()
        flash('Feed time deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback the transaction in case of a database error
        flash('Database error occurred. Please try again later.', 'error')
        # You can also log the error for debugging purposes
        print(f'Database error: {str(e)}')

    return redirect(url_for('device_handler.edit_device', device_id=feedtime.device_id))


### Updating feed times ###
    
@device_handler_bp.route('/get_device_feedtimes/<int:device_id>')
def device_feedtimes(device_id):
    # Query to retrieve feed times for the device
    feedtimes = FeedTime.query.filter_by(device_id=device_id).all()
    return jsonify(feedtimes)

@device_handler_bp.route('/get_device_by_id/<int:device_id>')    
def get_device_by_id(device_id):
    return Device.query.get(device_id)

def update_device(device):
    try:
        db.session.commit()
    except Exception as e:
        print(f'Error updating device: {str(e)}')
        db.session.rollback()
        raise e
    


