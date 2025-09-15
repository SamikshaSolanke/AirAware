# import os
# import requests
# import psycopg2
# from dotenv import load_dotenv

# load_dotenv()

# API_KEY = os.getenv("WEATHER_API_KEY")
# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT"),
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
# }

# city = "Pune"
# BASE_URL = "http://api.weatherapi.com/v1/current.json"


# def fetch_weather(city):
#     params = {"key": API_KEY, "q": city}
#     response = requests.get(BASE_URL, params=params, timeout=30)
#     response.raise_for_status()
#     return response.json()


# def insert_into_db(city, weather):
#     conn = psycopg2.connect(**DB_CONFIG)
#     cur = conn.cursor()

#     cur.execute(
#         """
#         INSERT INTO weather (city, temperature, humidity, pressure, description)
#         VALUES (%s, %s, %s, %s, %s)
#         ON CONFLICT DO NOTHING;
#         """,
#         (
#             city,
#             weather["current"]["temp_c"],
#             weather["current"]["humidity"],
#             weather["current"]["pressure_in"],
#             weather["current"]["condition"]["text"]
#         ),
#     )

#     conn.commit()
#     cur.close()
#     conn.close()


# if __name__ == "__main__":
#     try:
#         print(f"Fetching weather data for {city}...")
#         data = fetch_weather(city)
#         insert_into_db(city, data)
#         print(f"✅ Inserted weather record for {city}")
#     except Exception as e:
#         print(f"❌ Failed for {city}: {e}")

# import os
# import requests
# import psycopg2
# from dotenv import load_dotenv
# from datetime import datetime, timedelta

# load_dotenv()

# API_KEY = os.getenv("WEATHER_API_KEY")
# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT"),
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
# }
# CITIES = ["Chennai", "Pune", "Mumbai", "Surat", "Delhi"]
# CITY = "Delhi"
# BASE_URL = "http://api.weatherapi.com/v1/history.json"


# def fetch_weather_last_48hrs(city):
#     now = datetime.now()
#     two_days_ago = now - timedelta(days=2)
#     one_day_ago = now - timedelta(days=1)
    
#     all_hours = []

#     # Fetch data for the day before yesterday
#     params_two_days_ago = {"key": API_KEY, "q": city, "dt": two_days_ago.strftime("%Y-%m-%d")}
#     response_two_days_ago = requests.get(BASE_URL, params=params_two_days_ago, timeout=120)
#     response_two_days_ago.raise_for_status()
#     data_two_days_ago = response_two_days_ago.json()
#     if "forecast" in data_two_days_ago:
#         all_hours.extend(data_two_days_ago["forecast"]["forecastday"][0]["hour"])

#     # Fetch data for yesterday
#     params_one_day_ago = {"key": API_KEY, "q": city, "dt": one_day_ago.strftime("%Y-%m-%d")}
#     response_one_day_ago = requests.get(BASE_URL, params=params_one_day_ago, timeout=120)
#     response_one_day_ago.raise_for_status()
#     data_one_day_ago = response_one_day_ago.json()
#     if "forecast" in data_one_day_ago:
#         all_hours.extend(data_one_day_ago["forecast"]["forecastday"][0]["hour"])

#     # Fetch data for today
#     params_today = {"key": API_KEY, "q": city, "dt": now.strftime("%Y-%m-%d")}
#     response_today = requests.get(BASE_URL, params=params_today, timeout=120)
#     response_today.raise_for_status()
#     data_today = response_today.json()
#     if "forecast" in data_today:
#         all_hours.extend(data_today["forecast"]["forecastday"][0]["hour"])
    
#     # Correct filtering logic
#     forty_eight_hours_ago = now - timedelta(hours=48)
    
#     last_48hrs_data = []
#     for h in all_hours:
#         time_str = h["time"]
#         # The API returns a date and time string, e.g., "2025-09-11 15:00"
#         # The format string needs to match this.
#         h_datetime = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        
#         if h_datetime >= forty_eight_hours_ago and h_datetime <= now:
#             last_48hrs_data.append({
#                 "city": city,
#                 "temperature": h["temp_c"],
#                 "humidity": h["humidity"],
#                 "pressure": h["pressure_mb"],
#                 "description": h["condition"]["text"],
#                 "time": time_str
#             })

#     return last_48hrs_data


# def insert_into_db(records):
#     if not records:
#         print("⚠️ No records to insert")
#         return

#     conn = psycopg2.connect(**DB_CONFIG)
#     cur = conn.cursor()

#     for rec in records:
#         cur.execute(
#             """
#             INSERT INTO weather (city, temperature, humidity, pressure, description, timestamp)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             ON CONFLICT DO NOTHING;
#             """,
#             (
#                 rec["city"],
#                 rec["temperature"],
#                 rec["humidity"],
#                 rec["pressure"],
#                 rec["description"],
#                 rec["time"],
#             ),
#         )

#     conn.commit()
#     cur.close()
#     conn.close()


# if __name__ == "__main__":
#     try:
#         print(f"Fetching weather data for the last 48 hours in {CITY}...")
#         data = fetch_weather_last_48hrs(CITY)
#         insert_into_db(data)
#         print(f"Inserted {len(data)} weather records for {CITY}")
#     except Exception as e:
#         print(f"Failed: {e}")

import os
import requests
import psycopg2
from datetime import datetime

# ✅ Use Lambda environment variables
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": os.environ["DB_PORT"],
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}

CITIES = ["Delhi", "Pune", "Mumbai", "Chennai", "Surat"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city):
    params = {
        "q": f"{city},IN",
        "appid": WEATHER_API_KEY,
        "units": "metric"  # temperature in Celsius
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def insert_into_db(city, weather_data):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        wind_speed = weather_data["wind"]["speed"]
        timestamp = datetime.utcfromtimestamp(weather_data["dt"])

        cur.execute(
            """
            INSERT INTO weather_data 
            (city, temperature, humidity, pressure, wind_speed, last_update)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (city, temp, humidity, pressure, wind_speed, timestamp)
        )

        conn.commit()
        return 1
    except Exception as e:
        print(f"❌ Error inserting weather data for {city}: {e}")
        return 0
    finally:
        cur.close()
        conn.close()


def lambda_handler(event, context):
    results = {}
    total_inserted = 0

    for city in CITIES:
        try:
            weather_data = fetch_weather(city)
            inserted = insert_into_db(city, weather_data)
            results[city] = f"Inserted {inserted} record(s)"
            total_inserted += inserted
        except Exception as e:
            results[city] = f"❌ Failed: {str(e)}"

    return {
        "statusCode": 200,
        "body": {
            "total_inserted": total_inserted,
            "details": results,
        },
    }
