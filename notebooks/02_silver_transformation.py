# Databricks notebook source
#Read Bronze Delta table into a Spark Daraframe

bronze_df = spark.read.table("workspace.default.bronze_weather")

# COMMAND ----------

#Inspect the data     

bronze_df.printSchema()
display(bronze_df)

# COMMAND ----------

#import pyspark sql

from pyspark.sql import functions as F

# COMMAND ----------

#Flatten the array

weather_df = bronze_df.select(
    "latitude",
    "longitude",
    F.explode(
        F.arrays_zip(
            "hourly.time",
            "hourly.temperature_2m",
            "hourly.relative_humidity_2m",
            "hourly.precipitation",
            "hourly.wind_speed_10m"
        )
    ).alias("weather")
)

# COMMAND ----------

#Inspect the results
weather_df.printSchema()
display(weather_df.limit(5))
print("Total records:", weather_df.count())

# COMMAND ----------

#Create silver dataframe

silver_df = weather_df.select(
    "latitude",
    "longitude",
    F.col("weather.time").alias("timestamp"),
    F.col("weather.temperature_2m").alias("temperature"),
    F.col("weather.relative_humidity_2m").alias("humidity"),
    F.col("weather.precipitation").alias("precipitation"),
    F.col("weather.wind_speed_10m").alias("wind_speed")
)

# COMMAND ----------

#Inspect the results

silver_df.printSchema()
display(silver_df.limit(10))

# COMMAND ----------

#Convert the timestamp

silver_df = silver_df.withColumn(
    "timestamp",
    F.to_timestamp(F.col("timestamp"), "yyyy-MM-dd'T'HH:mm")
)

# COMMAND ----------

#  Inspect the data types

silver_df.printSchema()
display(silver_df.limit(10))

# COMMAND ----------

#verify timestamp conversion

silver_df.select("timestamp").show(5, truncate=False)

# COMMAND ----------

#validate column types
silver_df.printSchema()

# COMMAND ----------

#Check for nulls in each column

silver_df.select([
    F.count(F.when(F.col(c).isNull(), c)).alias(c)
    for c in silver_df.columns
]).show()

# COMMAND ----------

# Remove duplicates based on location and timestamp

silver_df = silver_df.dropDuplicates([
    "latitude", 
    "longitude", 
    "timestamp"
])

#we do this since each location should only hae one obs. per hr

# COMMAND ----------

#Remove records with missing timestamps

silver_df = silver_df.dropna(subset=["timestamp"])

# COMMAND ----------

#verify the cleaned datafram

#print final record count

print("Total cleaned records:", silver_df.count())

display(silver_df.limit(10))
    

# COMMAND ----------

#Create our Silver Delta Table

silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("workspace.default.silver_weather")

# COMMAND ----------

# MAGIC %sql
# MAGIC --this will verify the table
# MAGIC SELECT *
# MAGIC FROM workspace.default.silver_weather
# MAGIC ORDER BY timestamp
# MAGIC LIMIT 10
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select count(*) as total_records
# MAGIC from workspace.default.silver_weather;