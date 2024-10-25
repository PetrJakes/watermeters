# write reading to the database using django ORM
# only ALLOWED_HOSTS in settings.py only includes trusted domains and IPs.
# example ALLOWED_HOSTS = ['127.0.0.1', '192.168.0.145', 'yourdomain.com']

import requests

#url = 'http://127.0.0.1:8000/water/update-reading/'
url = 'http://192.168.0.145:8000/water/update-reading/'  # Change to the correct IP
data = {
    'sn': '1234555dddd',  # Watermeter serial number
    'recent_reading': 0,    
}
response = requests.post(url, json=data)

if response.status_code == 200:
    print("Reading updated successfully!")
else:
    print(f"Error: {response.json()}")
