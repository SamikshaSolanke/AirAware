import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AQI_API_KEY")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

CITY = "Chennai"
BASE_URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"  # AQI dataset ID


def fetch_aqi():
    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[country]": "India",
        # "filters[state]": "Gujarat",
        "filters[city]": CITY,
        "limit": 1000,
    }
    response = requests.get(BASE_URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data.get("records", [])


def safe_float(value):
    """Convert API values to float or None if 'NA'."""
    if value in (None, "NA", "", "null"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def insert_into_db(records):
    if not records:
        print("⚠️ No records found.")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    rows = [
        (
            rec.get("city"),
            rec.get("station"),
            rec.get("pollutant_id"),
            safe_float(rec.get("min_value")),
            safe_float(rec.get("max_value")),
            safe_float(rec.get("avg_value")),
            rec.get("last_update"),
        )
        for rec in records
    ]

    cur.executemany(
        """
        INSERT INTO air_quality (city, station, pollutant_id, pollutant_min, pollutant_max, pollutant_avg, last_update)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """,
        rows,
    )

    conn.commit()
    cur.close()
    conn.close()



if __name__ == "__main__":
    try:
        print(f"Fetching AQI data for {CITY}...")
        data = fetch_aqi()
        insert_into_db(data)
        print(f"Inserted {len(data)} AQI records for {CITY}")
    except Exception as e:
        print(f"Failed for {CITY}: {e}")
