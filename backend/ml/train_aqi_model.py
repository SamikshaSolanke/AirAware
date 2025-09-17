# train_aqi_model.py
import os
import pickle
import io
from datetime import timedelta
import boto3
import pandas as pd
import pg8000
from statsmodels.tsa.arima.model import ARIMA

# Import preprocessing & feature engineering (these must be present in the same source_dir)
from preprocess import preprocess_aqi
from feature_engineering import add_aqi_features

# --- Config from environment (set these from SageMaker notebook) ---
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

CITIES = os.environ.get("CITIES", "Delhi,Pune,Mumbai,Chennai,Surat").split(",")
CITIES = [c.strip() for c in CITIES]

POLLUTANTS = os.environ.get("POLLUTANTS", "PM2.5,PM10,NO2,SO2,CO,OZONE").split(",")
POLLUTANTS = [p.strip() for p in POLLUTANTS]

OUTPUT_DIR = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")  # SageMaker default model dir
S3_OUTPUT_PREFIX = os.environ.get("S3_OUTPUT_PREFIX", None)   # optional s3 path to upload results
AWS_REGION = os.environ.get("AWS_REGION", None)

# --- DB connector ---
def connect_db():
    return pg8000.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

# --- fetch whole AQI table into Pandas df ---
def load_aqi_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT city, station, pollutant_id, pollutant_min, pollutant_max, pollutant_avg, last_update, created_at
        FROM air_quality
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    cur.close()
    conn.close()
    if not rows:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(rows, columns=cols)
    return df

# --- utility: train ARIMA and forecast next 72 hours (hourly) ---
def train_and_forecast(series, order=(2,1,2), steps=72):
    """
    series: pandas Series indexed by datetime (hourly)
    returns: fitted_model, forecast_df (timestamp, mean, conf_lower, conf_upper)
    """
    # Fit ARIMA
    model = ARIMA(series, order=order)
    fitted = model.fit()

    # Forecast steps ahead
    forecast_res = fitted.get_forecast(steps=steps)
    predicted = forecast_res.predicted_mean
    conf = forecast_res.conf_int()

    # build forecast dataframe (hourly forward from last index)
    last_ts = series.index.max()
    forecast_index = pd.date_range(start=last_ts + pd.Timedelta(hours=1), periods=steps, freq="H")
    df_fc = pd.DataFrame({
        "timestamp": forecast_index,
        "predicted_mean": predicted.values,
        "ci_lower": conf.iloc[:, 0].values,
        "ci_upper": conf.iloc[:, 1].values
    })
    return fitted, df_fc

# --- save artifacts locally & optionally to s3 ---
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
    # parse s3_uri: "s3://bucket/path..."
    assert s3_uri.startswith("s3://")
    _, rest = s3_uri.split("s3://", 1)
    bucket, key = rest.split("/", 1)
    s3.upload_file(local_path, bucket, key)
    print("Uploaded to", s3_uri)

# --- main flow ---
def main():
    print("Starting AQI training job")
    df = load_aqi_table()
    if df.empty:
        print("No AQI data found in DB. Exiting.")
        return

    # Preprocess and feature engineer
    df = preprocess_aqi(df)
    df = add_aqi_features(df)

    # Ensure datetime index and lowercase city strings
    df["city"] = df["city"].str.lower().str.strip()
    df["last_update"] = pd.to_datetime(df["last_update"])
    df = df.sort_values("last_update")

    # We'll train one model per (city, pollutant) for pollutant_avg.
    for city in CITIES:
        city_key = city.lower().strip()
        df_city = df[df["city"] == city_key]
        if df_city.empty:
            print(f"No data for {city_key}, skipping.")
            continue

        for pollutant in POLLUTANTS:
            # user may set pollutant ids exactly as in DB; try both uppercase and provided
            pollutant_key = pollutant.strip()
            df_poll = df_city[df_city["pollutant_id"].str.upper() == pollutant_key.upper()]
            if df_poll.empty:
                # fallback: some datasets store pollutant in pollutant_id or pollutant; skip if not found
                print(f"No rows for pollutant {pollutant_key} in {city_key}, skipping.")
                continue

            # build time series (hourly resample). Column pollutant_avg used as target
            ts = df_poll[["last_update", "pollutant_avg"]].dropna(subset=["pollutant_avg"]).copy()
            ts["last_update"] = pd.to_datetime(ts["last_update"])
            ts = ts.set_index("last_update").sort_index()
            # resample hourly and interpolate small gaps (limit 6 hours)
            ts = ts.resample("H").mean().interpolate(limit=6)

            if len(ts.dropna()) < 48:
                print(f"Insufficient data for {city_key}-{pollutant_key} (n={len(ts)}). Need >= 48 hourly points. Skipping.")
                continue

            print(f"Training ARIMA for {city_key} - {pollutant_key} (n={len(ts)})")
            try:
                fitted_model, fc_df = train_and_forecast(ts["pollutant_avg"], order=(2,1,2), steps=72)
            except Exception as e:
                print("Model training/forecast failed:", e)
                continue

            # Save model and forecast CSVs locally
            model_fname = f"{city_key}_{pollutant_key}_arima.pkl"
            fc_fname = f"{city_key}_{pollutant_key}_forecast_72h.csv"
            model_path = save_local(fitted_model, model_fname)
            fc_path = save_csv_local(fc_df, fc_fname)

            # optional upload to S3 if S3_OUTPUT_PREFIX is provided
            if S3_OUTPUT_PREFIX:
                # e.g. S3_OUTPUT_PREFIX = "s3://airaware-ml-bucket/models/aqi/"
                base_key = S3_OUTPUT_PREFIX.rstrip("/")
                # upload model and csv
                upload_to_s3(model_path, f"{base_key}/{model_fname}")
                upload_to_s3(fc_path, f"{base_key}/{fc_fname}")

    print("AQI training job finished.")

if __name__ == "__main__":
    main()
