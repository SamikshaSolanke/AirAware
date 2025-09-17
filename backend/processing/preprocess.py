# preprocess.py code
import pandas as pd
import numpy as np

def preprocess_aqi(df):
    df = df.drop_duplicates()

    df["pollutant_min"] = df["pollutant_min"].fillna(df["pollutant_min"].mean())
    df["pollutant_max"] = df["pollutant_max"].fillna(df["pollutant_max"].mean())
    df["pollutant_avg"] = df["pollutant_avg"].fillna(df["pollutant_avg"].mean())

    df["city"] = df["city"].str.lower().str.strip()
    df["station"] = df["statio"].str.lower().str.strip()

    df["last_update"] = pd.to_datetime(df["last_update"])
    df["created_at"] = pd.to_datetime(df["created_at"])

    return df

def preprocess_weather(df):
    df = df.drop_duplicates()

    df["city"] = df["city"].str.lower().str.strip()

    for col in ["temperature", "humidity", "pressure"]:
        df[col] = df[col].fillna(df[col].mean())

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["description"] = df["description"].str.lower().str.strip()

    return df
