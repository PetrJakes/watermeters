# yourapp/management/commands/mqtt_listener.py

import json
import paho.mqtt.client as mqtt # type: ignore
from django.core.management.base import BaseCommand # type: ignore
from water.models import Watermeter  # Import your Watermeter model

class Command(BaseCommand):
    help = 'Starts the MQTT listener'

    def handle(self, *args, **kwargs):
        # MQTT broker details
        broker = 'maxbox.maxbox.cz'
        port = 1883
        topic = "watermeter/readings"
        
        # MQTT credentials
        username = 'foerster'
        password = 'uJakese449'

        # This function will be called when the client connects to the broker
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                client.subscribe(topic)  # Subscribe to the topic
            else:
                print(f"Failed to connect, return code {rc}")

        # This function will be called when a message is received
        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
                print(f"Received message: {payload}")

                # Extract data from the payload
                sn = payload.get('sn')  # Serial number
                recent_reading = payload.get('recent_reading')

                if sn and recent_reading is not None:
                    # Try to find the Watermeter with the given serial number
                    try:
                        watermeter = Watermeter.objects.get(sn=sn)
                        # Update the recent reading and date
                        watermeter.recent_reading = recent_reading                        
                        watermeter.save()
                        print(f"Updated reading for {sn}: {recent_reading}")
                    except Watermeter.DoesNotExist:
                        print(f"No Watermeter found with serial number: {sn}")
            except json.JSONDecodeError:
                print("Error decoding JSON message")

        # Set up MQTT client and handlers
        client = mqtt.Client()

        # Set username and password
        client.username_pw_set(username, password)

        # Define connection and message handlers
        client.on_connect = on_connect
        client.on_message = on_message

        # Connect to the broker and start listening
        client.connect(broker, port, 60)
        client.loop_forever()  # Keep the script running to listen for messages
