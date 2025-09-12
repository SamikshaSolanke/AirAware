import numpy as np
import pandas as pd

def aqi_features(df):
    df["pollutant_range"] = df["pollutant_max"] - df["pollutant_min"]

    conditions = [
        (df["pollutant_avg"] <= 50),
        (df["pollutant_avg"] <= 100),
        (df["pollutant_avg"] <= 200),
        (df["pollutant_avg"] <= 300),
        (df["pollutant_avg"] <= 400),
        (df["pollutant_avg"] > 400),
    ]
    categories = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]