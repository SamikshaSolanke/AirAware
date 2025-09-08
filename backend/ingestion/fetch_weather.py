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

import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

CITY = "Delhi"
BASE_URL = "http://api.weatherapi.com/v1/history.json"


def fetch_weather_last_6hrs(city):
    now = datetime.now()  # local time
    date_str = now.strftime("%Y-%m-%d")

    params = {"key": API_KEY, "q": city, "dt": date_str}
    response = requests.get(BASE_URL, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()

    if "forecast" not in data:
        return []

    hours_data = data["forecast"]["forecastday"][0]["hour"]

    # Take only the last 6 hours (relative to current hour)
    current_hour = now.hour
    last_6hrs = [h for h in hours_data if current_hour - 24 <= int(h["time"].split(" ")[1].split(":")[0]) <= current_hour]

    results = []
    for h in last_6hrs:
        results.append({
            "city": city,
            "temperature": h["temp_c"],
            "humidity": h["humidity"],
            "pressure": h["pressure_mb"],
            "description": h["condition"]["text"],
            "time": h["time"]
        })
    return results


def insert_into_db(records):
    if not records:
        print("⚠️ No records to insert")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for rec in records:
        cur.execute(
            """
            INSERT INTO weather (city, temperature, humidity, pressure, description, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (
                rec["city"],
                rec["temperature"],
                rec["humidity"],
                rec["pressure"],
                rec["description"],
                rec["time"],
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        print(f"Fetching weather data for last 6 hrs in {CITY}...")
        data = fetch_weather_last_6hrs(CITY)
        insert_into_db(data)
        print(f"Inserted {len(data)} weather records for {CITY}")
    except Exception as e:
        print(f"Failed: {e}")
