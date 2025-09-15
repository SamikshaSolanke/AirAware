# train_weather_model.py
import os
import pg8000
import pandas as pd
import pickle
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

CITIES = os.environ.get("CITIES", "Delhi,Pune,Mumbai,Chennai,Surat").split(",")
FEATURES = os.environ.get("FEATURES", "temperature,humidity,pressure").split(",")
OUTPUT_DIR = "/opt/ml/model"

def connect_db():
    return pg8000.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def fetch_feature_series(conn, city, feature):
    cur = conn.cursor()
    # Adjust column name if your table uses different names (e.g., last_update vs timestamp)
    cur.execute(f"""
        SELECT timestamp, {feature}
        FROM weather
        WHERE city=%s
        ORDER BY timestamp;
    """, (city,))
    rows = cur.fetchall()
    cur.close()
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=["timestamp", "value"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.dropna(subset=["value"])
    df = df.set_index("timestamp").sort_index()
    # Resample hourly and interpolate small gaps
    df = df.resample("H").mean().interpolate(limit=6)
    return df["value"]

def train_and_save(series, save_path):
    try:
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

    for city in CITIES:
        city = city.strip()
        print(f"--- City: {city} ---")
        for feature in FEATURES:
            feature = feature.strip()
            print(f"Training for {city} - {feature}")
            series = fetch_feature_series(conn, city, feature)
            if series is None or len(series.dropna()) < 48:
                print(f"Insufficient data for {city}-{feature}, skipping.")
                continue

            filename = f"{city.replace(' ','_')}_{feature}_arima.pkl"
            save_path = os.path.join(OUTPUT_DIR, filename)
            success = train_and_save(series, save_path)
            if not success:
                print(f"Training failed for {city}-{feature}")
    conn.close()

if __name__ == "__main__":
    print("Start Weather ARIMA training:", datetime.utcnow())
    main()
    print("Finished Weather ARIMA training:", datetime.utcnow())
