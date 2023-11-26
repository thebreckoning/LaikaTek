import ujson
from umqtt.simple import MQTTClient
import uasyncio as asyncio

MQTT_SECRETS = "mqtt_secrets.json"

class MQTTHandler:
    def __init__(self, server, callback=None, secrets_file='mqtt_secrets.json', feed_file='feedtimes.json', wifi_file='wifi.json'):
        self.server = server
        self.callback = callback
        self.secrets_file = secrets_file
        self.feed_file = feed_file
        self.wifi_file = wifi_file
        self.client = None

    def connect(self):
        try:
            with open(self.secrets_file, 'r') as f:
                secrets = ujson.load(f)
        except Exception as e:
            print(f"Error loading secrets file: {e}")
            return

        self.client = MQTTClient(
            client_id=secrets.get('client_id'),
            server=secrets.get('server'),
            port=secrets.get('port'),
            user=secrets.get('user'),
            password=secrets.get('password'),
            keepalive=secrets.get('keepalive'),
            ssl=secrets.get('ssl'),
            ssl_params=ujson.loads(secrets.get('ssl_params', '{}'))
        )
        try:
            self.client.connect()
        except Exception as e:
            print(f"Error connecting to MQTT server: {e}")
            self.client = None

    async def listen_async(self):
        print("Starting mqtt listener")
        if self.client is None:
            self.connect()
            print("Connected to mqtt broker")
            if self.client is None:
                print("Failed to connect to MQTT server")
                return

        device_name = None
        try:
            with open(self.wifi_file, 'r') as f:
                wifi_config = ujson.load(f)
            device_name = wifi_config['device_name']
            print(f"Device name: {device_name}")
        except Exception as e:
            print(f"Error loading wifi file: {e}")
            return

        self.client.set_callback(self.on_message)
        topic = 'feedtimes/{}'.format(device_name)
        self.client.subscribe(topic.encode('utf-8'))
        print(f'Subscribed to topic "{topic}"')

        print('Listening for messages on topic "{}"...'.format(topic))
        while True:
            try:
                self.client.check_msg()
                await asyncio.sleep(1)  # Adjust sleep duration as needed
            except Exception as e:
                print(f"Error in listen_async: {e}")
                await asyncio.sleep(1)  # Adjust sleep duration as needed

    def on_message(self, topic, msg):
        print("on_message called with topic: {} and msg: {}".format(topic, msg))
        try:
            msg_str = msg.decode('utf-8')
        except UnicodeDecodeError:
            print("Could not decode message")
            return

        print("Received message on topic {}: {}".format(topic, msg_str))

        # Handle message processing asynchronously
        asyncio.create_task(self.handle_message(topic, msg_str))

    async def handle_message(self, topic, msg_str):
        try:
            with open(self.feed_file, 'w') as f:
                ujson.dump(msg_str, f)
            print("Feed file updated!")
        except Exception as e:
            print("Error writing to file: {}".format(e))

        await self.create_parsed_feedtimes()

        if self.callback is not None:
            print("Calling callback")
            self.callback(topic, msg_str)  # Pass both topic and msg_str to the callback
            print("Finished calling callback")

    async def create_parsed_feedtimes(self):
        print("Creating parsed_feedtimes.json file")
        try:
            parsed_feedtimes = await self.app_parse_feedtimes()
            with open('parsed_feedtimes.json', 'w') as f:
                ujson.dump(parsed_feedtimes, f)
            print("Finished creating parsed_feedtimes.json file")
        except Exception as e:
            print("Error in create_parsed_feedtimes: ", e)

    async def app_parse_feedtimes(self):
        try:
            with open('feedtimes.json', 'r') as f:
                data = f.read()
                print("Read data from feedtimes.json: ", data)
        except (OSError, Exception) as e:
            print(f"Error reading feedtimes.json: {e}")
            return []

        sets = data.split(',')
        parsed_feedtimes = []
        for i, s in enumerate(sets):
            time, portion = s.rsplit(':', 1)
            parsed_feedtimes.append({'time': time, 'portion': portion})

        #print("Parsed feedtimes: ", parsed_feedtimes)
        return parsed_feedtimes

