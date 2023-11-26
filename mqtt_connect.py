# mqtt_connect.py

import os
import paho.mqtt.client as mqtt
from flask import Blueprint, jsonify
from models import Device, FeedTime
from datetime import datetime

# Blueprint for adding and editing user devices
mqtt_connect_bp = Blueprint('mqtt_connect', __name__)

MQTT_BROKER = 'mqtt_broker'
MQTT_PORT = 1883

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.subscribe("sensor_data/food_level")
        self.client.loop_start()
        self.mqtt_data = {}

    def on_message(self, client, userdata, message):
        payload = message.payload.decode()
        try:
            nickname, sensor_data = payload.split(';')
            nickname = nickname.split(': ')[1].strip()
            food_level = sensor_data.split(': ')[1].strip()
            self.mqtt_data[nickname] = food_level
        except ValueError:
            print("Invalid MQTT message format")

    def publish_feedtimes(self, device_id):
        device = Device.query.get(device_id)
        if not device:
            return jsonify({"error": "Device not found!"}), 404

        feedtimes = FeedTime.query.filter_by(device_id=device_id).all()
        time_portion_pairs = [f"{datetime.strptime(feedtime.time, '%H:%M:%S').strftime('%H:%M')}:{feedtime.portions}" for feedtime in feedtimes]

        topic = "feedtimes/" + device.nickname
        payload = ",".join(time_portion_pairs)

        self.client.publish(topic, payload, retain=True, qos=1)
        print("Message published")

        return jsonify({"message": "Feed times and portions published successfully!"}), 200

mqtt_client = MQTTClient()

@mqtt_connect_bp.route('/publish_feedtimes/<int:device_id>', methods=['POST'])
def publish_feedtimes(device_id):
    return mqtt_client.publish_feedtimes(device_id)

@mqtt_connect_bp.route('/latest_mqtt_message')
def get_latest_mqtt_message():
    return jsonify({'message': mqtt_client.mqtt_data})
