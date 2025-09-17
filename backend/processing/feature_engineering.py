# feature_engineering.py code
import pandas as pd

def add_aqi_features(df):
    """
    Feature engineering for AQI dataset.
    """
    # Pollutant range (spread between max and min)
    df['pollutant_range'] = df['pollutant_max'] - df['pollutant_min']

    # Categorize air quality based on pollutant_avg (example thresholds, can be adjusted)
    conditions = [
        (df['pollutant_avg'] <= 50),
        (df['pollutant_avg'] <= 100),
        (df['pollutant_avg'] <= 200),
        (df['pollutant_avg'] <= 300),
        (df['pollutant_avg'] <= 400),
        (df['pollutant_avg'] > 400),
    ]
    categories = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']
    df['aqi_category'] = pd.cut(df['pollutant_avg'], 
                                bins=[-1, 50, 100, 200, 300, 400, float("inf")], 
                                labels=categories)

    # Extract datetime features
    df['year'] = df['last_update'].dt.year
    df['month'] = df['last_update'].dt.month
    df['day'] = df['last_update'].dt.day
    df['hour'] = df['last_update'].dt.hour

    return df


def add_weather_features(df):
    """
    Feature engineering for weather dataset.
    """
    # Temperature feels hotter when humidity is high
    df['heat_index'] = df['temperature'] + 0.1 * df['humidity']

    # Pressure anomaly detection (how much it deviates from mean)
    df['pressure_anomaly'] = df['pressure'] - df['pressure'].mean()

    # Extract datetime features
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.day
    df['hour'] = df['timestamp'].dt.hour

    return df
