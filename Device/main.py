import gc
import time
import ntptime
import utime
import select
import urequests as requests

#from datetime import datetime
from machine import Pin
from umqtt.simple import MQTTClient
from wifi_connect import WiFiManager
from time_keeper import TimeManager
from user_info import mqtt_secrets, DEVICE_ID

def main():
    client_id = mqtt_secrets[1]
    server = mqtt_secrets[2]
    port = mqtt_secrets[3]
    user = mqtt_secrets[4]
    password = mqtt_secrets[5]
    keepalive = mqtt_secrets[6]
    ssl = mqtt_secrets[7]
    ssl_params = mqtt_secrets[8]

    device_id = DEVICE_ID
    topic = "feedtimes/" + str(device_id)

    class MyDevice:
        def __init__(self):
        
            print("Initializing MyDevice...")
            # Connect to WiFi
            self.wifi_manager = WiFiManager()  # Create an instance of WiFiManager
            self.wifi_manager.join_wifi()  # Use the join_wifi method of WiFiManager
            
            # Set device time
            self.time_keeper = TimeManager()
            self.time_keeper.set_current_time()
                
            # Garbage collection
            gc.collect()
            # Attributes from FeedTimes
            self.message_received = False
            self.client_id = mqtt_secrets[1]
            self.server = mqtt_secrets[2]
            self.port = mqtt_secrets[3]
            self.user = mqtt_secrets[4]
            self.password = mqtt_secrets[5]
            self.keepalive = mqtt_secrets[6]
            self.ssl = mqtt_secrets[7]
            self.ssl_params = mqtt_secrets[8]
            self.device_id = DEVICE_ID
            self.topic = "feedtimes/" + str(self.device_id)
            
            # Attributes from Dispenser
            self.dispense_times = []
            
            # Attributes from MyDevice
            self.mqtt_connected = False
            self.feedtimes = []
            self.IN1 = Pin(0, Pin.OUT)
            self.IN2 = Pin(1, Pin.OUT)
            self.IN3 = Pin(2, Pin.OUT)
            self.IN4 = Pin(3, Pin.OUT)
            self.step_sequence = [
                [1, 0, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 0, 0, 1],
                [1, 0, 0, 1]
            ]
            self.portioninput = 3
            self.portion = 128
            self.portions = self.portioninput * self.portion
            
            self.last_mqtt_update = 0

        ########## Functions for collecting data from the mqtt broker #######
        # Methods from FeedTimes
        def get_feedtimes_from_mqtt(self, topic, msg):
            gc.collect()
            print("MQTT message received!")
            try:
                # Decode the message and split by comma
                times_raw = msg.decode().split(',')
                
                # Convert each time to HH:MM format
                self.feedtimes = [time[:5] for time in times_raw]
                print(f"Decoded feed times from MQTT message: {self.feedtimes}")
                
                # Read the existing lines from the file
                with open('dispense_times.txt', 'r') as file:
                    lines = file.readlines()

                # Ensure there's at least one line
                while len(lines) < 1:
                    lines.append("\n")

                # Save to the second line of dispense_times.txt
                lines[1] = ",".join(self.feedtimes) + "\n"

                # Write the updated lines back to the file
                with open('dispense_times.txt', 'w') as file:
                    file.writelines(lines)
                
                self.message_received = True
                print("Feed times saved to dispense_times.txt")
            except Exception as e:
                print(f"Error processing MQTT message: {e}")


        def connect_to_mqtt(self):
            print("Attempting to connect to MQTT...")
            if not self.mqtt_connected:
                try:
                    client = MQTTClient(client_id, server, port, user, password, keepalive, ssl, ssl_params)
                    client.set_callback(self.on_mqtt_message)
                    client.connect()
                    client.subscribe(topic)
                    print('Connected to MQTT Broker and subscribed to:', topic)
                    
                    # Wait for a message for up to 3 seconds
                    rlist, _, _ = select.select([client.sock], [], [], 3)
                    if rlist:
                        client.wait_msg()
                    else:
                        print("No message received after 3 seconds.")

                    client.disconnect()
                    print("Disconnected from MQTT Broker.")
                    self.mqtt_connected = False

                except Exception as e:
                    print("Error connecting to MQTT:", e)
            else:
                print("Already connected to MQTT.")


        # Methods from MyDevice
        def on_mqtt_message(self, topic, msg):
            print("on_mqtt_message triggered...")
            self.message_received = True
            times_raw = msg.decode().split(',')
            self.feedtimes = [time[:5] for time in times_raw]  # Convert to HH:MM format
            self.last_mqtt_update = utime.time()  # Set the last update time
            print("Received feed times:", self.feedtimes)
            
            # Methods from Dispenser
        def get_feedtimes_from_file(self):
            with open('dispense_times.txt', 'r') as file:
                times_raw = file.readline().strip().split(",")
                return [time[:5] for time in times_raw]

        def check_dispense_time(self):
            print("Checking dispense time...")
            
            # Get feed times from the file only if the last MQTT update was more than 10 seconds ago
            if utime.time() - self.last_mqtt_update > 10:
                self.feedtimes = self.get_feedtimes_from_file()
            
            current_time = utime.localtime()
            current_hour_minute = "{:02d}:{:02d}".format(current_time[3], current_time[4])
            print(f"Current Time: {current_hour_minute}")
            print(f"Feed Times: {self.feedtimes}")
            
            if current_hour_minute in self.feedtimes:
                print("Time to dispense food!")
                self.run_motor()
                utime.sleep(60)
            else:
                print("Not time to dispense yet.")


        def dispense_food(self, step_number):
            #print(f"Dispensing food, step number: {step_number}...")
            self.IN1.value(self.step_sequence[step_number][0])
            self.IN2.value(self.step_sequence[step_number][1])
            self.IN3.value(self.step_sequence[step_number][2])
            self.IN4.value(self.step_sequence[step_number][3])
            utime.sleep_ms(1)

        def run_motor(self):
            print("Starting run_motor.")
            for _ in range(self.portions):
                for step in range(8):
                    self.dispense_food(step)
                    


        def run(self):
            print("Running MyDevice...")

            while True:
                self.connect_to_mqtt()
                self.check_dispense_time()
                utime.sleep(5)

    device = MyDevice()
    device.run()

if __name__ == '__main__':
    main()
