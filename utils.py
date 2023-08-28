#!/usr/bin/python3

import random
import string

def generate_random_password(length=12):
    """
    Generate a random password of the given length.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def format_sensor_data(sensor_data_list):
    """
    Format the sensor data list into a more user-friendly format.
    """
    formatted_data = []
    for data in sensor_data_list:
        formatted_data.append({
            'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': data.temperature,
            'humidity': data.humidity
        })
    return formatted_data
