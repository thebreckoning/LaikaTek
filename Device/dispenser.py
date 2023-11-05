       refactor the following code to operate the run motor function at the specified feedtimes collected by the app_parse_feedtimes function
       
       
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