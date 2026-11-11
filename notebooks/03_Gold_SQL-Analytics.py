# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC -- Read our silver table
# MAGIC
# MAGIC SELECT * FROM workspace.default.silver_weather
# MAGIC order by timestamp
# MAGIC limit 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --Calculate avg temp, humidity, previpitation & windspeed
# MAGIC
# MAGIC SELECT
# MAGIC     DATE(timestamp) as weather_date,
# MAGIC     round(avg(sw.temperature), 2) as avg_temp,
# MAGIC     round(avg(sw.humidity), 2) AS avg_humidity,
# MAGIC     round(sum(sw.precipitation), 2) as avg_precipitation,
# MAGIC     round(avg(sw.wind_speed), 2) as avg_wind_speed
# MAGIC from workspace.default.silver_weather as sw
# MAGIC GROUP BY DATE(timestamp)
# MAGIC ORDER BY weather_date;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --create gold delta table
# MAGIC
# MAGIC CREATE OR REPLACE TABLE workspace.default.gold_weather_daily
# MAGIC USING DELTA
# MAGIC AS 
# MAGIC SELECT
# MAGIC     DATE(timestamp) as weather_date,
# MAGIC     round(avg(sw.temperature), 2) as avg_temp,
# MAGIC     round(avg(sw.humidity), 2) AS avg_humidity,
# MAGIC     round(sum(sw.precipitation), 2) as total_precipitation,
# MAGIC     round(avg(sw.wind_speed), 2) as avg_wind_speed
# MAGIC from workspace.default.silver_weather as sw
# MAGIC GROUP BY DATE(timestamp);

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --verify delta table exists
# MAGIC
# MAGIC SELECT *
# MAGIC from workspace.default.gold_weather_daily
# MAGIC order by weather_date;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --verify record count (should be 7)
# MAGIC
# MAGIC select count(*) as total_days
# MAGIC from workspace.default.gold_weather_daily;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --identify hottest & coldest days
# MAGIC
# MAGIC SELECT
# MAGIC     weather_date,
# MAGIC     avg_temp,
# MAGIC     RANK() OVER (Order by avg_temp desc) as Hottest_rank,
# MAGIC     RANK() OVER (Order by avg_temp asc) as Coldest_rank
# MAGIC from workspace.default.gold_weather_daily
# MAGIC order by hottest_rank;
# MAGIC
# MAGIC /*
# MAGIC RANK()
# MAGIC
# MAGIC Assigns a numerical ranking to rows based on a specified order.
# MAGIC
# MAGIC ORDER BY temperature DESC ranks highest temperatures first.
# MAGIC ORDER BY temperature ASC ranks lowest temperatures first.
# MAGIC Rows with equal values receive the same rank, and the next rank is skipped.
# MAGIC */

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --Calculate temperature changes between days
# MAGIC
# MAGIC SELECT
# MAGIC     weather_date,
# MAGIC     avg_temp,
# MAGIC     LAG(avg_temp) OVER (
# MAGIC         ORDER BY weather_date
# MAGIC     ) as previous_day_temp,
# MAGIC
# MAGIC     ROUND(
# MAGIC         avg_temp - LAG(avg_temp) OVER (
# MAGIC             ORDER BY weather_date
# MAGIC         ), 2
# MAGIC     ) AS temp_change
# MAGIC from workspace.default.gold_weather_daily
# MAGIC ORDER BY weather_date;
# MAGIC
# MAGIC /*
# MAGIC LAG()
# MAGIC
# MAGIC Retrieves a value from a previous row within an ordered dataset.
# MAGIC
# MAGIC Useful for comparing current values against previous values.
# MAGIC Example: Comparing today's average temperature with yesterday's.
# MAGIC If no previous row exists, it returns NULL.
# MAGIC */

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --identify raniest days
# MAGIC
# MAGIC SELECT
# MAGIC     weather_date,
# MAGIC     total_precipitation,
# MAGIC     avg_humidity,
# MAGIC     avg_wind_speed
# MAGIC from workspace.default.gold_weather_daily
# MAGIC order by total_precipitation;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from workspace.default.gold_weather_daily limit 2

# COMMAND ----------

# MAGIC %sql 
# MAGIC
# MAGIC --verify record count
# MAGIC
# MAGIC SELECT count(*) as total_records
# MAGIC from workspace.default.gold_weather_daily;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --check for nulls
# MAGIC
# MAGIC SELECT *
# MAGIC from workspace.default.gold_weather_daily
# MAGIC WHERE
# MAGIC     weather_date is NULL
# MAGIC     or avg_temp is null
# MAGIC     or avg_humidity is NULL
# MAGIC     or total_precipitation is NULL
# MAGIC     or avg_wind_speed is null;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --check for duplicate dates
# MAGIC
# MAGIC select
# MAGIC     weather_date,
# MAGIC     count(*) as record_count
# MAGIC from workspace.default.gold_weather_daily
# MAGIC group by weather_date
# MAGIC having count(*) > 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC --Check temperature ranges
# MAGIC
# MAGIC select
# MAGIC     MIN(avg_temp) as lowest_temp,
# MAGIC     MAX(avg_temp) as highest_temp,
# MAGIC     AVG(avg_temp) as overall_avg_temp
# MAGIC from workspace.default.gold_weather_daily