

import os
from flask import request, flash, redirect, url_for, render_template, Blueprint, jsonify
from flask_login import current_user, login_required
from models import db, Device, FeedTime
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

import paho.mqtt.client as mqtt

from models import db, Device, FeedTime

# Blueprint for adding and editing user devices
mqtt_connect_bp = Blueprint('mqtt_connect', __name__)


client_id = os.environ.get('MQTT_CLIENT_ID')
clean_session = os.environ.get('MQTT_CLEAN_SESSION')
userdata = os.environ.get('MQTT_USERDATA')
protocol = os.environ.get('MQTT_PROTOCOL')
transport = os.environ.get('MQTT_TRANSPORT')



client_c = {1: client_id, 2: clean_session, 3: userdata, 4: protocol, 5: transport}

# Probably don't need these vars
server = os.environ.get('MQTT_SERVER')
port = os.environ.get('MQTT_PORT')
user = os.environ.get('MQTT_USER')
password = os.environ.get('MQTT_PASSWORD')
keepalive = os.environ.get('MQTT_KEEPALIVE')
ssl = os.environ.get('MQTT_SSL')
ssl_params = os.environ.get('MQTT_SSL_PARAMS')


MQTT_BROKER = 'mqtt_broker'
MQTT_PORT = 1883  
#client = mqtt.Client()
#client.connect(MQTT_BROKER, MQTT_PORT, 60)


@mqtt_connect_bp.route('/publish_feedtimes/<int:device_id>', methods=['POST'])
def publish_feedtimes(device_id):
    #client = mqtt.Client(client_id, clean_session, userdata, protocol, transport)
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Identify device and associated feedtimes
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Device not found!"}), 404

    feedtimes = FeedTime.query.filter_by(device_id=device_id).all()

    # Extracting the 'time' and 'portion' attributes from each FeedTime object
    #time_portion_pairs = [f"{feedtime.time}:{feedtime.portions}" for feedtime in feedtimes]
    time_portion_pairs = [f"{datetime.strptime(feedtime.time, '%H:%M:%S').strftime('%H:%M')}:{feedtime.portions}" for feedtime in feedtimes]



    # Use device's nickname for the topic instead of device_id
    topic = "feedtimes/" + device.nickname
    payload = ",".join(time_portion_pairs)
    
    client.publish(topic, payload, retain=True, qos=1)
    print("Message published")
    
    return jsonify({"message": "Feed times and portions published successfully!"}), 200

