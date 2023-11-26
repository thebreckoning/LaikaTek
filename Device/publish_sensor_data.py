import ujson
import uasyncio as asyncio
from umqtt.simple import MQTTClient
from machine import Pin, time_pulse_us

SOUND_SPEED = 340
TRIG_PULSE_DURATION_US = 10

class SensorPublisher:
    def __init__(self):
        self.trig_pin = Pin(15, Pin.OUT) # White
        self.echo_pin = Pin(14, Pin.IN) # Purple
        self.load_config()

    def load_config(self):
        with open('mqtt_publish.json', 'r') as f:
            self.mqtt_config = ujson.load(f)

        with open('wifi.json', 'r') as f:
            self.wifi_config = ujson.load(f)

    async def food_level_sensor(self):
        self.trig_pin.value(0)
        await asyncio.sleep(5)
        self.trig_pin.value(1)
        await asyncio.sleep(TRIG_PULSE_DURATION_US)
        self.trig_pin.value(0)

        ultrason_duration = time_pulse_us(self.echo_pin, 1, 30000)
        distance_cm = SOUND_SPEED * ultrason_duration / 20000

        print(f"Distance: {distance_cm} cm")
        return distance_cm

    def interpret_food_level(self, distance):
        if distance < 0:
            return "Error"
        elif distance <= 5:
            return "Full"
        elif distance < 18:
            return "Medium"
        else:
            return "Low"

    async def update_data(self, topic, message):
        client = MQTTClient(self.mqtt_config['client_id'], self.mqtt_config['server'], self.mqtt_config['port'])
        try:
            client.connect()
            client.publish(topic, message)
            print("Message published successfully")
        except Exception as e:
            print("Failed to publish message:", e)
            await asyncio.sleep(60)
        finally:
            try:
                client.disconnect()
            except Exception as e:
                print("Failed to disconnect client:", e)
            await asyncio.sleep(2)

    async def publish_sensor_data(self):
        while True:
            topic = "sensor_data/food_level"
            sensor_data = await self.food_level_sensor()
            food_level = self.interpret_food_level(sensor_data)
            message = f"Nickname: {self.wifi_config['device_name']}; Food Level: {food_level}"

            await self.update_data(topic, message)
'''
# Create an instance of SensorPublisher and start the event loop
sensor_publisher = SensorPublisher()
loop = asyncio.get_event_loop()
loop.create_task(sensor_publisher.publish_sensor_data())
loop.run_forever()
'''