# train_aqi_model.py
import os
import pg8000
import pandas as pd
import pickle
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime

# DB config passed as env vars by SageMaker training job
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]


CITIES = os.environ.get("CITIES", "Delhi,Pune,Mumbai,Chennai,Surat").split(",")
# If you want to limit pollutants, you can set POLLUTANTS as env var; otherwise script will query distinct.
POLLUTANTS_ENV = os.environ.get("POLLUTANTS", None)
OUTPUT_DIR = "/opt/ml/model"


def connect_db():
    return pg8000.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def list_pollutants_for_city(conn, city):
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT pollutant_id FROM air_quality WHERE city=%s;", (city,))
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]


def fetch_series(conn, city, pollutant):
    cur = conn.cursor()
    cur.execute("""
        SELECT last_update, pollutant_avg
        FROM air_quality
        WHERE city=%s AND pollutant_id=%s
        ORDER BY last_update;
    """, (city, pollutant))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return None
    
    df = pd.DataFrame(rows, columns=["last_update", "value"])
    df["last_update"] = pd.to_datetime(df["last_update"])
    df = df.dropna(subset=["value"])
    df = df.set_index("last_update").sort_index()
    # Resample to hourly (adjust if your data is daily); interpolate short gaps
    df = df.resample("H").mean().interpolate(limit=6)
    return df["value"]


def train_and_save(series, save_path):
    try:
        # Basic ARIMA parameters -- you might want to tune these later
        model = ARIMA(series, order=(2,1,2))
        fitted = model.fit()
        with open(save_path, "wb") as f:
            pickle.dump(fitted, f)
        print(f"Saved model to {save_path}")
        return True
    except Exception as e:
        print(f"Failed to train ARIMA: {e}")
        return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = connect_db()
    pollutants_to_use = POLLUTANTS_ENV.split(",") if POLLUTANTS_ENV else None

    for city in CITIES:
        city = city.strip()
        print(f"--- City: {city} ---")
        pollutants = pollutants_to_use if pollutants_to_use else list_pollutants_for_city(conn, city)
        if not pollutants:
            print(f"No pollutants found for {city}")
            continue

        for pollutant in pollutants:
            pollutant = pollutant.strip()
            print(f"Training for {city} - {pollutant}")
            series = fetch_series(conn, city, pollutant)
            if series is None or len(series.dropna()) < 48:
                print(f"Insufficient data for {city}-{pollutant}, skipping.")
                continue

            filename = f"{city.replace(' ','_')}_{pollutant.replace('/','_')}_arima.pkl"
            save_path = os.path.join(OUTPUT_DIR, filename)
            success = train_and_save(series, save_path)
            if not success:
                print(f"Training failed for {city}-{pollutant}")
    conn.close()


if __name__ == "__main__":
    print("Start AQI ARIMA training:", datetime.utcnow())
    main()
    print("Finished AQI ARIMA training:", datetime.utcnow())
