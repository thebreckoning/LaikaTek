from mqtt_handler import MQTTHandler
from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import ujson
import machine
import os
import utime
import _thread
import gc

AP_NAME = "LaikaTek"
AP_DOMAIN = "laika.net"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"
WIFI_FILE = "wifi.json"
MQTT_SECRETS = "mqtt_secrets.json"

WIFI_MAX_ATTEMPTS = 3

def machine_reset():
    utime.sleep(1)
    print("Resetting...")
    machine.reset()

def setup_mode():
    print("Entering setup mode...")
    
    def ap_index(request):
        if request.headers.get("host").lower() != AP_DOMAIN.lower():
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN.lower())

        return render_template(f"{AP_TEMPLATE_PATH}/index.html")

    def ap_configure(request):
        print("Saving wifi credentials...")

        with open(WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()

        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
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

def application_mode():
    print("Entering application mode.")
    onboard_led = machine.Pin("LED", machine.Pin.OUT)
    
    # Create an instance of MQTTHandler and connect to the MQTT server
    mqtt_handler = MQTTHandler()
    mqtt_handler.connect()

    def run_mqtt_listener():
        mqtt_handler.listen()

    # Start listening for MQTT messages in a separate thread
    _thread.start_new_thread(run_mqtt_listener, ())
    print("MQTT listener started")

    def app_index(request):
        return render_template(f"{APP_TEMPLATE_PATH}/index.html")

    def app_toggle_led(request):
        onboard_led.toggle()
        return "OK"
    
    def app_extract_device_name():
        with open(WIFI_FILE, 'r') as f:
            data = ujson.load(f)
            device_name = data.get('device_name', None)
        return device_name
    
    def app_get_device_name(req):
        device_name = app_extract_device_name()
        resp = server.Response(device_name)
        return resp

    server.add_route("/app_get_device_name", handler=app_get_device_name, methods=["GET"])
    
    def app_parse_feedtimes():
        # Step 0: Read data from feedtimes.json file
        try:
            with open('feedtimes.json', 'r') as f:
                data = json.load(f)
        except (OSError, Exception) as e:
            print(f"Error reading feedtimes.json: {e}")
            return []

        # Split the string into individual sets
        sets = data.split(',')

        # Iterate through each set
        parsed_feedtimes = []
        for i, s in enumerate(sets):
            # Split the set into time and portion using rsplit
            time, portion = s.rsplit(':', 1)
            
            # Add the time and portion to the list
            parsed_feedtimes.append({'time': time, 'portion': portion})

        return parsed_feedtimes

    
    def app_get_feedtimes(request):
        # Call the app_parse_feedtimes function to get the parsed feed times
        parsed_feedtimes = app_parse_feedtimes()

        # Create the response
        resp = server.Response(json.dumps(parsed_feedtimes))
        resp.headers['Content-Type'] = 'application/json'
        return resp

    server.add_route("/app_get_feedtimes", handler=app_get_feedtimes, methods=["GET"])

    def app_reset(request):
        os.remove(WIFI_FILE)
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{APP_TEMPLATE_PATH}/reset.html", access_point_ssid=AP_NAME)

    def app_catch_all(request):
        return "Not found.", 404

    server.add_route("/", handler=app_index, methods=["GET"])
    server.add_route("/toggle", handler=app_toggle_led, methods=["GET"])
    server.add_route("/reset", handler=app_reset, methods=["GET"])
    server.set_callback(app_catch_all)

    # Start the web server in a separate thread
    _thread.start_new_thread(server.run, ())
    print("Web server started")


# Figure out which mode to start up in...
try:
    os.stat(WIFI_FILE)

    with open(WIFI_FILE) as f:
        gc.collect()
        wifi_current_attempt = 1
        wifi_credentials = json.load(f)
        
        while wifi_current_attempt < WIFI_MAX_ATTEMPTS:
            ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])
            if is_connected_to_wifi():             
                print(f"Connected to wifi, IP address {ip_address}")
                break
            else:
                wifi_current_attempt += 1
                
        if is_connected_to_wifi():
            gc.collect()
            application_mode()
        else:
            print("Bad wifi connection!")
            print(wifi_credentials)
            os.remove(WIFI_FILE)
            machine_reset()

except Exception:
    setup_mode()

# Start the web server in the main thread
server.run()


