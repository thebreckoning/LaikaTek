import json
import ujson
from machine import Pin
import gc
import uasyncio as asyncio
import utime
import RGB1602
import os
from mqtt_handler import MQTTHandler
from motor_control import MotorControl
from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
from time_manager import TimeManager
from publish_sensor_data import SensorPublisher

AP_NAME = "LaikaTek"
AP_DOMAIN = "deviceinfo.laikatek.com"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"
WIFI_FILE = "wifi.json"
#MQTT_SECRETS = "mqtt_secrets.json"

WIFI_MAX_ATTEMPTS = 3


# Define the GPIO pin connected to your button
BUTTON_PIN = Pin(8, Pin.IN, Pin.PULL_UP)

# Define a debounce time to ignore button bounces
DEBOUNCE_TIME = 3000

# Instantiate TimeManager
time_manager = TimeManager()
lcd = RGB1602.RGB1602(16, 2)
rgb1 = (148,0,110)

# Function to attempt WiFi connection
async def attempt_wifi_connection_async():
    wifi_current_attempt = 1
    while wifi_current_attempt <= WIFI_MAX_ATTEMPTS:
        try:
            with open(WIFI_FILE) as f:
                wifi_credentials = json.load(f)
            ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
            if is_connected_to_wifi():
                print(f"Connected to wifi, IP address {ip_address}")
                time_manager.set_current_time()  # Set the current time using TimeManager
                return True
            else:
                print(f"Attempt {wifi_current_attempt} failed. Retrying...")
                wifi_current_attempt += 1
        except OSError as e:
            print(f"Error reading {WIFI_FILE}: {e}")
            break
        except KeyError as e:
            print(f"Missing WiFi credentials: {e}")
            break
    return False

async def set_current_time():
    # Implement your time-setting logic here
    pass

    
def print_current_time():
    # Get the current local time
    localtime = utime.localtime()
    # Format the time as a string
    current_time = "{:02d}:{:02d}".format(localtime[3], localtime[4])
    # Print the current time
    print(f"Current local time is: {current_time}")

async def machine_reset_async():
    await asyncio.sleep(1)
    print("Resetting...")
    machine.reset()


async def setup_mode_async():
    print("Entering setup mode...")
    
    def ap_index(request):
        if request.headers.get("host").lower() != AP_DOMAIN.lower():
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN.lower())

        return render_template(f"{AP_TEMPLATE_PATH}/index.html")

    async def ap_configure(request):
        print("Saving wifi credentials...")

        with open(WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()

        asyncio.create_task(machine_reset_async())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid=request.form["ssid"])
    
    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN)

        return "Not found.", 404

    server.add_route("/", handler=ap_index, methods=["GET"])
    server.add_route("/configure", handler=ap_configure, methods=["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)

async def mqtt_callback(topic, msg):
    pass

mqtt_handler = MQTTHandler(
    server,
    callback=lambda topic, msg: asyncio.create_task(mqtt_callback(topic, msg))
)

async def mqtt_handler_async():
    print("mqtt handler starting!")
    await mqtt_handler.listen_async()

async def device_get_name_async():
    
    def app_extract_device_name():
        with open(WIFI_FILE, 'r') as f:
            data = json.load(f)
            device_name = data.get('device_name', None)
        return device_name
    
    def app_get_device_name(req):
        device_name = app_extract_device_name()
        resp = server.Response(device_name)
        return resp

    server.add_route("/app_get_device_name", handler=app_get_device_name, methods=["GET"])

async def application_mode_async():
    print("Entering application mode.")
    sensor_publisher = SensorPublisher()  # Create an instance of SensorPublisher
    
    # Add the new routes here:
    server.add_route("/", handler=app_index, methods=["GET"])
    server.add_route("/reset", handler=app_reset, methods=["GET"])
    server.set_callback(app_catch_all)
    
    await asyncio.gather(
        mqtt_handler_async(),
        sensor_publisher.publish_sensor_data(),
        device_get_name_async(),
        motor_control_async(),       
    )

def app_index(request):
    return render_template(f"{APP_TEMPLATE_PATH}/index.html")

def app_reset(request):
    # Deleting the WIFI configuration file will cause the device to reboot as
    # the access point and request new configuration.
    os.remove(WIFI_FILE)
    # Reboot from a new thread after we have responded to the user.
    _thread.start_new_thread(machine_reset, ())
    return render_template(f"{APP_TEMPLATE_PATH}/reset.html", access_point_ssid=AP_NAME)

def app_catch_all(request):
    return "Not found.", 404

    
async def motor_control_async():
    print("Starting motor control")
    motor_control = MotorControl()
    await motor_control.schedule_feedings()

# Function to reset the code when the button is pushed

def reset_on_button_press():
    if BUTTON_PIN.value() == 0:  # Button is pressed (assuming it's active-low)
        print("Button pressed. Resetting...")
        machine.reset()  # Reset the device

# Function to enter setup mode when the button is pressed

async def enter_setup_mode_on_button_press():
    start_time = utime.ticks_ms()
    button_held = False

    while True:
        if BUTTON_PIN.value() == 0:  # Button is pressed (assuming it's active-low)
            elapsed_time = utime.ticks_diff(utime.ticks_ms(), start_time)
            if elapsed_time >= DEBOUNCE_TIME:  # Check for debounce time (adjust as needed)
                if not button_held:
                    print("Button held down for {} milliseconds.".format(elapsed_time))
                    button_held = True
                if elapsed_time >= 5000:  # Button held for 5 seconds
                    print("Resetting Device")
                    # Remove the WIFI_FILE
                    try:
                        os.remove(WIFI_FILE)
                        print("WIFI_FILE removed.")
                    except OSError as e:
                        print("Error removing WIFI_FILE:", e)
        else:
            start_time = utime.ticks_ms()  # Reset the start time when the button is released
            button_held = False

        await asyncio.sleep_ms(100)  # Adjust the sleep time as needed


async def display_current_time_on_lcd_async():
    lcd = RGB1602.RGB1602(16, 2)  # Assuming a 16x2 LCD

    while True:
        # Get the current local time
        localtime = utime.localtime()
        # Format the time as a string in HH:MM format
        hour = localtime[3]
        hour_12_format = hour % 12
        hour_12_format = 12 if hour_12_format == 0 else hour_12_format
        am_pm = "AM" if hour < 12 else "PM"
        current_time = "{:02d}:{:02d} {}".format(hour_12_format, localtime[4], am_pm)
        
        # Clear the LCD display
        lcd.clear()
        lcd.setRGB(rgb1[0],rgb1[1],rgb1[2])
        # Set the cursor to the beginning of the first line
        lcd.setCursor(4, 0)
        # Print the current time on the LCD
        lcd.printout("LaikaTek")
        lcd.setCursor(4, 1)
        lcd.printout(f"{current_time}")

        # Wait for a specified time before updating the time again
        await asyncio.sleep(10)


async def main():
    #sensor_publisher = SensorPublisher()
    if await attempt_wifi_connection_async():
        print("Starting application mode...")
        asyncio.create_task(display_current_time_on_lcd_async())  # Start updating the LCD time display
        asyncio.create_task(enter_setup_mode_on_button_press())
        await application_mode_async()  # Ensure this is an async function
    else:
        print(f"Failed to connect to wifi after {WIFI_MAX_ATTEMPTS} attempts.")
        await setup_mode_async()  # Ensure this is an async function

    print("Starting server...")
    server.run()

        
# Start the event loop
asyncio.run(main())

