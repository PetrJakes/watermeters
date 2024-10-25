import paho.mqtt.client as mqtt # type: ignore
import json

# MQTT broker details
broker = 'maxbox.maxbox.cz'
port = 1883
topic = "watermeter/readings"

# MQTT credentials
username = 'foerster'
password = 'uJakese449'

# Create MQTT client
client = mqtt.Client()

# Set username and password
client.username_pw_set(username, password)

# Connect to the broker
client.connect(broker, port, 60000)

# Data to send (water meter reading)
data = {
    'sn': '11111',  # Water meter serial number
    'recent_reading': 12345,  # Updated reading value
}

# Publish the data to the topic
client.publish(topic, json.dumps(data))

# Disconnect after sending
client.disconnect()

print("Published data to the broker")
