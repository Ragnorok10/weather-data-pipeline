#Import our libraries

import requests
import json #this is added later as we will use it to handle json data

#store API url

url = "https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date=2026-10-01&end_date=2026-10-07&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=America%2FNew_York"

#send HTTP request

response = requests.get(url);

#Check HTTP status

print(response.status_code);

#Parse the JSON response

data = response.json()

#Explore the data

print(data.keys())

#Access the HOURLY dictionary

hourly = data["hourly"]

#extract timestamps and temperatures

timestamps = hourly["time"]
temperatures = hourly["temperature_2m"]

#print 1st 5 rows

for i in range(5):
    print(timestamps[i], temperatures[i])

#import our data to a raw file on our machine

with open("data/raw/weather.json", "w") as file:
    json.dump(data, file, indent=4)

# open file into read mode, now to retrieve stored data and hold it

with open("data/raw/weather.json", "r") as file:
    saved_data = json.load(file)

#verify the contents

print(saved_data["hourly"]["time"][:5])