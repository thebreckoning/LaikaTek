# userinfo.py
import time
import machine
import urequests as requests

### Wifi Connection Info ###

# Replace with your WiFi SSID and password
ssid = "YourWiFiSSID"
password = "YourWiFiPassword"

wifi_secrets = {1: ssid, 2: password}

### MQTT Broker Info ###

# Replace with your MQTT broker information
client_id = "YourClientID"
server = "YourMQTTBrokerServer"
port = 1883  # Replace with your MQTT broker port
user = "YourMQTTUsername"  # Replace with your MQTT username (if applicable)
password = "YourMQTTPassword"  # Replace with your MQTT password (if applicable)
keepalive = 0  # Replace with your desired MQTT keep-alive interval (in seconds)
ssl = False  # Set to True if you are using SSL/TLS for MQTT
ssl_params = "{}"  # Additional SSL parameters if needed

mqtt_secrets = {
    1: client_id,
    2: server,
    3: port,
    4: user,
    5: password,
    6: keepalive,
    7: ssl,
    8: ssl_params,
}

### Device Information ###

# Replace with your device ID or name
DEVICE_ID = "YourDeviceID"

device_secrets = {1: DEVICE_ID}
