import json
import utime
import uasyncio as asyncio
from machine import Pin
import heapq

class MotorControl:
    def __init__(self, IN1_pin=0, IN2_pin=1, IN3_pin=2, IN4_pin=3):
        self.IN1 = Pin(IN1_pin, Pin.OUT)
        self.IN2 = Pin(IN2_pin, Pin.OUT)
        self.IN3 = Pin(IN3_pin, Pin.OUT)
        self.IN4 = Pin(IN4_pin, Pin.OUT)
        
        self.p_multiplier = 128  # Adjust as needed for your motor's step resolution
        print("MotorControl instance created")
        
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

    async def dispense_food(self, step_number):
        self.IN1.value(self.step_sequence[step_number][0])
        self.IN2.value(self.step_sequence[step_number][1])
        self.IN3.value(self.step_sequence[step_number][2])
        self.IN4.value(self.step_sequence[step_number][3])
        await asyncio.sleep_ms(1)

    async def run_motor(self, portions):
        print("Starting run_motor.")
        steps = int(portions * self.p_multiplier)  # Calculate the total steps based on portion
        for _ in range(steps):  # Loop for the calculated number of steps
            for step in range(8):
                await self.dispense_food(step)

    async def update_schedule(self):
        while True:
            try:
                with open('parsed_feedtimes.json', 'r') as file:
                    feed_times = json.load(file)
                    #print(f"Feed Times: {feed_times}")
                self.schedule = [(entry['time'].strip('"'), float(entry['portion'].strip('"'))) for entry in feed_times]
                self.schedule.sort()
                #print(f"Feed schedule: {self.schedule}")
            except Exception as e:
                print(f"Failed to update schedule: {e}")
            await asyncio.sleep(2)  

    async def schedule_feedings(self):
        self.schedule = []
        asyncio.create_task(self.update_schedule())

        while True:
            current_time = "{:02d}:{:02d}".format(*utime.localtime()[3:5])
            #print(f"Serving food at: {feed_time}")
            #print(f"Current time: {current_time}")
            next_feed_index = None
            for i, (feed_time, _) in enumerate(self.schedule):
                #print(f"Next feed time(s): {feed_time}")
                if feed_time == current_time:
                    next_feed_index = i
                    break

            if next_feed_index is None and self.schedule:
                next_feed_index = 0

            if next_feed_index is not None:
                feed_time, portion = self.schedule[next_feed_index]
                if current_time == feed_time:
                    print(f"It's time to feed: {feed_time}")
                    await self.run_motor(portion)
                    await asyncio.sleep(60)  # Wait for 60 seconds after feeding
                    self.schedule.pop(next_feed_index)
                    self.schedule.append((feed_time, portion))
                else:
                    #print("Not time to feed")
                    await asyncio.sleep(5)  # Check every 5 seconds
            else:
                # If there's no schedule, wait a bit before checking again
                await asyncio.sleep(5)
'''
# Usage
async def main():
    motor_control = MotorControl()
    await motor_control.schedule_feedings()

# Run the main function
asyncio.run(main())
'''
