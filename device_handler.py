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

    if request.method == 'POST':
        if d_form.validate_on_submit() and f_form.validate_on_submit():
            try:
                # Create a new device
                new_device = Device(
                    nickname=d_form.nickname.data,
                    device_type=d_form.device_type.data,
                    owner=current_user.user_id,
                )

                db.session.add(new_device)
                db.session.commit()

                # Directly get the time from the form
                time_obj = request.form.get('feedtimes')

                # Add feed time to the device
                new_feedtime = FeedTime(
                    device_id=new_device.device_id,
                    time=time_obj,
                )
                db.session.add(new_feedtime)
                db.session.commit()

                return jsonify({'success': True, 'message': 'Device added successfully!'})

            except SQLAlchemyError as e:
                db.session.rollback()  # Rollback the transaction in case of a database error
                print(f'Database error: {str(e)}')  # Log the error for debugging purposes
                return jsonify({'success': False, 'error': 'Database error occurred. Please try again later.'})
        
        else:
            errors = d_form.errors
            errors.update(f_form.errors)
            return jsonify({'success': False, 'error': 'Form validation failed.', 'details': errors})

    # If the request method is GET or if there's any other issue, return a message indicating the expected method or error.
    if request.method == 'GET':
        return render_template('add_device.html', d_form=d_form, f_form=f_form)
    # If the request method is GET or if there's any other issue, return a message indicating the expected method or error.
    if request.method == 'GET':
        return render_template('add_device.html', d_form=d_form, f_form=f_form)

    # return jsonify({'success': False, 'message': 'Expected POST request method.'})

####### Editing existing devices ########

from flask import jsonify

@device_handler_bp.route('/edit_device/<int:device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'success': False, 'error': 'Device not found'}), 404

    if request.method == 'POST':
        form = EditDeviceForm(request.form, obj=device)  # Populate the form with request data
        if form.validate():
            update_device_details(device, form)
            update_feedtimes(device_id, request.form.getlist('feedtimes'))
            
            try:
                db.session.commit()
                return jsonify({'success': True, 'message': 'Device updated successfully!'})
            except SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': 'Database error occurred. Please try again later.'}), 500
        else:
            return jsonify({'success': False, 'error': 'Form validation failed', 'form_errors': form.errors}), 400

    # For a GET request, return the device details and associated feed times
    existing_feedtimes = [feedtime.time for feedtime in device.feedtimes]
    return jsonify({
        'device_id': device.device_id,
        'nickname': device.nickname,
        'device_type': device.device_type,
        'feedtimes': existing_feedtimes
    })


# Update the device details in the database
def update_device_details(device, form):  
    try:
        form.populate_obj(device)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Device details updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating device details: {str(e)}'})

# Update the associated feed times for the device.
def update_feedtimes(device_id, updated_feedtimes):   
    try:
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

        db.session.commit()
        return jsonify({'success': True, 'message': 'Feed times updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating feed times: {str(e)}'})
            

            
###### Delete device ########
@device_handler_bp.route('/delete_device/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if device:
        try:
            db.session.delete(device)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Device deleted successfully!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error deleting device: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'Device not found!'})


###### Add feed times ######

@device_handler_bp.route('/add_feedtime<int:device_id>', methods=['POST'])
def add_feedtime(device_id: any):
    form = AddFeedTimeForm()
    if form.validate_on_submit():
        try:
            new_feedtime = FeedTime(
                device_id=device_id,
                time=form.time.data,
            )
            db.session.add(new_feedtime)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Feed time added successfully!'})
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'Database error: {str(e)}')
            return jsonify({'success': False, 'message': 'Database error occurred. Please try again later.'})
    else:
        return jsonify({'success': False, 'message': 'Form validation failed.', 'details': form.errors})

### Deleting feed times ###

@device_handler_bp.route('/delete_feedtime/<int:feedtime_id>', methods=['POST'])
def delete_feedtime(feedtime_id):
    feedtime = FeedTime.query.get(feedtime_id)
    
    if not feedtime:
        return jsonify({'success': False, 'message': 'Feed time not found!'})

    try:
        db.session.delete(feedtime)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Feed time deleted successfully!'})
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback the transaction in case of a database error
        # You can also log the error for debugging purposes
        print(f'Database error: {str(e)}')
        return jsonify({'success': False, 'message': 'Database error occurred. Please try again later.'})


### Updating feed times ###
    
@device_handler_bp.route('/get_device_feedtimes/<int:device_id>')
def device_feedtimes(device_id):
    # Query to retrieve feed times for the device
    feedtimes = FeedTime.query.filter_by(device_id=device_id).all()
    feedtimes_list = [{'time_id': ft.time_id, 'time': ft.time} for ft in feedtimes]
    return jsonify(feedtimes_list)

@device_handler_bp.route('/get_device_by_id/<int:device_id>')    
def get_device_by_id(device_id):
    device = Device.query.get(device_id)
    if device:
        device_data = {
            'device_id': device.device_id,
            'nickname': device.nickname,
            'device_type': device.device_type,
            'owner': device.owner
        }
        return jsonify(device_data)
    else:
        return jsonify({'message': 'Device not found'}), 404

def update_device(device):
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Device updated successfully!'})
    except Exception as e:
        print(f'Error updating device: {str(e)}')
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating device'}), 500