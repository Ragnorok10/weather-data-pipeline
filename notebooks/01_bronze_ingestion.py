# Databricks notebook source
#step 32 - import data from Open-Meteo

#library imports
import requests
import json
from datetime import date, timedelta

#fetch the previous 7 complete days

end_date = date.today() - timedelta(days=1)
start_date = end_date - timedelta(days=6)

#api link
url = "https://archive-api.open-meteo.com/v1/archive"

#specifying what exact "columns"/parameters we are extracting from the link above
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "start_date": str(start_date),
    "end_date": str(end_date),
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m"
    ],
    "timezone": "America/New_York"
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

data = response.json() #here we are assigning the data we just ingested to a json formated variable

print("API request succesful")
print("Records fetched:",len(data["hourly"]["time"]))



# COMMAND ----------

#save API Response to your databricks volume

file_path = "/Volumes/workspace/default/weather_raw/weather.json" #this will write it to our weather json file

with open(file_path, "w") as file:
    json.dump(data, file, indent=4) #

print("Weather JSON saved successfully")

# COMMAND ----------

#identifies our uploaded json file
# file_path = "/Volumes/workspace/default/weather_raw/weather.json" - DEPRICATED

#assigns it to a variable named df (dataframe) and allows PySpark to read it and allows Spark to parse the formatted JSON
df = spark.read.option("multiline", "true").json(file_path)

# COMMAND ----------

df.printSchema()
display(df)

# COMMAND ----------

#Create 1st Bronze Table

df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.default.bronze_weather")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --This will count total records from the table
# MAGIC select count(*) as total_records
# MAGIC from workspace.default.bronze_weather;