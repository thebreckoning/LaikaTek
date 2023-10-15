import time
import machine
import urequests as requests

class TimeManager:
    def __init__(self):
        self.rtc = machine.RTC()

    def set_current_time(self):
        success = False
        while not success:
            try:
                response = requests.get('http://worldtimeapi.org/api/ip')
                if response.status_code == 200:
                    data = response.json()
                    datetime_str = data['datetime']  # Assuming the API returns a 'datetime' field in the format "YYYY-MM-DDTHH:MM:SSZ"
                    
                    # Manually parse the datetime_str
                    year = int(datetime_str[0:4])
                    month = int(datetime_str[5:7])
                    day = int(datetime_str[8:10])
                    hour = int(datetime_str[11:13])
                    minute = int(datetime_str[14:16])
                    second = int(datetime_str[17:19])
                    # For the weekday, you can use a simple function to calculate it if needed
                    # For now, we'll set it as 1 (Monday) as a placeholder
                    weekday = 1
                    subseconds = 0  # This is a placeholder; adjust as needed
                    
                    # Set the datetime to RTC
                    rtc = machine.RTC()
                    rtc.datetime((year, month, day, weekday, hour, minute, second, subseconds))
                    
                    # ... [rest of the code to print the formatted time]
                    
                    success = True
                else:
                    print("Failed to fetch current time:", response.status_code)
                    utime.sleep(10)  # Wait for 10 seconds before retrying
            except Exception as e:
                print("An error occurred while setting device time:", e)
                utime.sleep(10)  # Wait for 10 seconds before retrying

# Example usage:
#time_manager = TimeManager()
#time_manager.print_current_time()
