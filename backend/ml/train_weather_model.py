# train_weather_model.py
import os
import pickle
import boto3
import pandas as pd
import pg8000
from statsmodels.tsa.arima.model import ARIMA

from preprocess import preprocess_weather
from feature_engineering import add_weather_features

# --- config from env ---
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

CITIES = os.environ.get("CITIES", "Delhi,Pune,Mumbai,Chennai,Surat").split(",")
CITIES = [c.strip() for c in CITIES]

VARIABLES = os.environ.get("FEATURES", "temperature,humidity,pressure").split(",")
VARIABLES = [v.strip() for v in VARIABLES]

OUTPUT_DIR = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
S3_OUTPUT_PREFIX = os.environ.get("S3_OUTPUT_PREFIX", None)
AWS_REGION = os.environ.get("AWS_REGION", None)

def connect_db():
    return pg8000.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def load_weather_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT city, temperature, humidity, pressure, description, timestamp
        FROM weather
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    cur.close()
    conn.close()
    if not rows:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(rows, columns=cols)
    return df

def train_and_forecast(series, order=(2,1,2), steps=72):
    model = ARIMA(series, order=order)
    fitted = model.fit()
    forecast_res = fitted.get_forecast(steps=steps)
    predicted = forecast_res.predicted_mean
    conf = forecast_res.conf_int()
    last_ts = series.index.max()
    forecast_index = pd.date_range(start=last_ts + pd.Timedelta(hours=1), periods=steps, freq="H")
    df_fc = pd.DataFrame({
        "timestamp": forecast_index,
        "predicted_mean": predicted.values,
        "ci_lower": conf.iloc[:, 0].values,
        "ci_upper": conf.iloc[:, 1].values
    })
    return fitted, df_fc

def save_local(obj, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    print("Saved:", path)
    return path

def save_csv_local(df, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print("Saved CSV:", path)
    return path

def upload_to_s3(local_path, s3_uri):
    s3 = boto3.client("s3", region_name=AWS_REGION) if AWS_REGION else boto3.client("s3")
    assert s3_uri.startswith("s3://")
    _, rest = s3_uri.split("s3://", 1)
    bucket, key = rest.split("/", 1)
    s3.upload_file(local_path, bucket, key)
    print("Uploaded to", s3_uri)

def main():
    print("Starting Weather training job")
    df = load_weather_table()
    if df.empty:
        print("No weather data found in DB. Exiting.")
        return

    df = preprocess_weather(df)
    df = add_weather_features(df)
    df["city"] = df["city"].str.lower().str.strip()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    for city in CITIES:
        city_key = city.lower().strip()
        df_city = df[df["city"] == city_key]
        if df_city.empty:
            print(f"No weather data for {city_key}, skipping.")
            continue

        for var in VARIABLES:
            if var not in df_city.columns:
                print(f"Variable {var} not in table, skipping for {city_key}")
                continue

            ts = df_city[["timestamp", var]].dropna(subset=[var]).copy()
            ts["timestamp"] = pd.to_datetime(ts["timestamp"])
            ts = ts.set_index("timestamp").sort_index()
            ts = ts.resample("H").mean().interpolate(limit=6)

            if len(ts.dropna()) < 48:
                print(f"Insufficient data for {city_key}-{var} (n={len(ts)}). Skipping.")
                continue

            print(f"Training ARIMA for {city_key} - {var} (n={len(ts)})")
            try:
                fitted_model, fc_df = train_and_forecast(ts[var], order=(2,1,2), steps=72)
            except Exception as e:
                print("Model training/forecast failed:", e)
                continue

            model_fname = f"{city_key}_{var}_arima.pkl"
            fc_fname = f"{city_key}_{var}_forecast_72h.csv"
            model_path = save_local(fitted_model, model_fname)
            fc_path = save_csv_local(fc_df, fc_fname)

            if S3_OUTPUT_PREFIX:
                upload_to_s3(model_path, f"{S3_OUTPUT_PREFIX.rstrip('/')}/{model_fname}")
                upload_to_s3(fc_path, f"{S3_OUTPUT_PREFIX.rstrip('/')}/{fc_fname}")

    print("Weather training job finished.")

if __name__ == "__main__":
    main()
