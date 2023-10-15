# wificonnect.py
import network
import time
import machine
from user_info import wifi_secrets  # Import wifi_secrets from user_info.py

class TimeoutError(Exception):
    pass

class WiFiManager:
    def __init__(self):
        self.ssid = wifi_secrets[1]
        self.password = wifi_secrets[2]

    def scan_wifi(self):
        try:
            # Initialize Wi-Fi interface
            wifi = network.WLAN(network.STA_IF)
            
            # Activate Wi-Fi interface
            wifi.active(True)
            
            # Scan for available networks
            networks = wifi.scan()
            
            # Print available networks
            print("Available Wi-Fi Networks:")
            for network_info in networks:
                print(network_info[0].decode("utf-8"))
        
        except OSError as e:
            print("An error occurred while scanning for Wi-Fi networks:", e)
        except Exception as e:
            print("An unexpected error occurred:", e)

    def join_wifi(self, timeout=10):
        try:
            # Initialize Wi-Fi interface
            wifi = network.WLAN(network.STA_IF)
            
            # Activate Wi-Fi interface
            wifi.active(True)
            
            # Connect to the specified Wi-Fi network using the imported ssid and password
            wifi.connect(self.ssid, self.password)
            
            # Wait for the connection to complete with a timeout
            start_time = time.time()
            while not wifi.isconnected():
                if time.time() - start_time > timeout:
                    raise TimeoutError("Failed to connect to Wi-Fi within the specified timeout.")
                time.sleep(1)
            
            # Print connection details
            print("Connected to Wi-Fi:")
            print("SSID:", self.ssid)
            print("IP Address:", wifi.ifconfig()[0])
        
        except OSError as e:
            print("An error occurred while connecting to the Wi-Fi network:", e)
        except TimeoutError as e:
            print(e)
        except Exception as e:
            print("An unexpected error occurred:", e)
