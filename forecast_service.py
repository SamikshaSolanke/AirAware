from fastapi import APIRouter, HTTPException
import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"

# Enhanced forecast data with more detailed information
HARDCODED_FORECASTS = {
    "pune": {
        "location": {"name": "Pune", "country": "India", "region": "Maharashtra"},
        "forecast": {
            "forecastday": [
                {
                    "date": "2025-09-18",
                    "day": {
                        "maxtemp_c": 28.5,
                        "mintemp_c": 22.0,
                        "condition": {"text": "Partly Cloudy", "icon": "🌤️"},
                        "avghumidity": 72,
                        "uv": 6.2,
                        "maxwind_kph": 15.5,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 8.5
                    },
                    "pollutants": {
                        "PM25": {"concentration": 45.2, "AQI": 95, "category": "Moderate"},
                        "PM10": {"concentration": 65.8, "AQI": 88, "category": "Moderate"},
                        "O3": {"concentration": 85.3, "AQI": 72, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 22.0, "condition": "Clear"},
                        {"time": "12:00", "temp": 27.5, "condition": "Partly Cloudy"},
                        {"time": "18:00", "temp": 25.2, "condition": "Cloudy"}
                    ]
                },
                {
                    "date": "2025-09-19",
                    "day": {
                        "maxtemp_c": 30.2,
                        "mintemp_c": 23.5,
                        "condition": {"text": "Sunny", "icon": "☀️"},
                        "avghumidity": 68,
                        "uv": 7.1,
                        "maxwind_kph": 12.8,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 10.0
                    },
                    "pollutants": {
                        "PM25": {"concentration": 42.8, "AQI": 89, "category": "Moderate"},
                        "PM10": {"concentration": 62.3, "AQI": 82, "category": "Moderate"},
                        "O3": {"concentration": 89.7, "AQI": 78, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 23.5, "condition": "Clear"},
                        {"time": "12:00", "temp": 29.8, "condition": "Sunny"},
                        {"time": "18:00", "temp": 27.1, "condition": "Clear"}
                    ]
                },
                {
                    "date": "2025-09-20",
                    "day": {
                        "maxtemp_c": 29.8,
                        "mintemp_c": 22.8,
                        "condition": {"text": "Light Rain", "icon": "🌦️"},
                        "avghumidity": 85,
                        "uv": 4.5,
                        "maxwind_kph": 18.2,
                        "totalprecip_mm": 5.2,
                        "avgvis_km": 6.8
                    },
                    "pollutants": {
                        "PM25": {"concentration": 35.6, "AQI": 75, "category": "Moderate"},
                        "PM10": {"concentration": 48.2, "AQI": 65, "category": "Moderate"},
                        "O3": {"concentration": 65.4, "AQI": 58, "category": "Good"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 22.8, "condition": "Cloudy"},
                        {"time": "12:00", "temp": 28.5, "condition": "Light Rain"},
                        {"time": "18:00", "temp": 26.3, "condition": "Rain"}
                    ]
                }
            ]
        }
    },
    "mumbai": {
        "location": {"name": "Mumbai", "country": "India", "region": "Maharashtra"},
        "forecast": {
            "forecastday": [
                {
                    "date": "2025-09-18",
                    "day": {
                        "maxtemp_c": 32.1,
                        "mintemp_c": 26.5,
                        "condition": {"text": "Humid", "icon": "🌫️"},
                        "avghumidity": 78,
                        "uv": 8.2,
                        "maxwind_kph": 14.3,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 7.2
                    },
                    "pollutants": {
                        "PM25": {"concentration": 52.3, "AQI": 105, "category": "Unhealthy for Sensitive"},
                        "PM10": {"concentration": 78.9, "AQI": 98, "category": "Moderate"},
                        "O3": {"concentration": 92.1, "AQI": 82, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 26.5, "condition": "Humid"},
                        {"time": "12:00", "temp": 31.2, "condition": "Hot & Humid"},
                        {"time": "18:00", "temp": 29.8, "condition": "Humid"}
                    ]
                },
                {
                    "date": "2025-09-19",
                    "day": {
                        "maxtemp_c": 33.5,
                        "mintemp_c": 27.2,
                        "condition": {"text": "Partly Cloudy", "icon": "⛅"},
                        "avghumidity": 75,
                        "uv": 8.8,
                        "maxwind_kph": 16.7,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 8.5
                    },
                    "pollutants": {
                        "PM25": {"concentration": 48.7, "AQI": 98, "category": "Moderate"},
                        "PM10": {"concentration": 72.4, "AQI": 89, "category": "Moderate"},
                        "O3": {"concentration": 88.5, "AQI": 78, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 27.2, "condition": "Partly Cloudy"},
                        {"time": "12:00", "temp": 32.8, "condition": "Hot"},
                        {"time": "18:00", "temp": 30.5, "condition": "Cloudy"}
                    ]
                },
                {
                    "date": "2025-09-20",
                    "day": {
                        "maxtemp_c": 31.8,
                        "mintemp_c": 26.8,
                        "condition": {"text": "Thunderstorms", "icon": "⛈️"},
                        "avghumidity": 88,
                        "uv": 5.2,
                        "maxwind_kph": 25.4,
                        "totalprecip_mm": 12.8,
                        "avgvis_km": 5.1
                    },
                    "pollutants": {
                        "PM25": {"concentration": 38.9, "AQI": 82, "category": "Moderate"},
                        "PM10": {"concentration": 55.6, "AQI": 75, "category": "Moderate"},
                        "O3": {"concentration": 68.3, "AQI": 62, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 26.8, "condition": "Cloudy"},
                        {"time": "12:00", "temp": 30.5, "condition": "Thunderstorms"},
                        {"time": "18:00", "temp": 28.9, "condition": "Heavy Rain"}
                    ]
                }
            ]
        }
    },
    "chennai": {
        "location": {"name": "Chennai", "country": "India", "region": "Tamil Nadu"},
        "forecast": {
            "forecastday": [
                {
                    "date": "2025-09-18",
                    "day": {
                        "maxtemp_c": 34.2,
                        "mintemp_c": 28.1,
                        "condition": {"text": "Hot and Humid", "icon": "🔥"},
                        "avghumidity": 82,
                        "uv": 9.1,
                        "maxwind_kph": 18.5,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 6.8
                    },
                    "pollutants": {
                        "PM25": {"concentration": 38.5, "AQI": 81, "category": "Moderate"},
                        "PM10": {"concentration": 58.7, "AQI": 76, "category": "Moderate"},
                        "O3": {"concentration": 95.2, "AQI": 85, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 28.1, "condition": "Humid"},
                        {"time": "12:00", "temp": 33.5, "condition": "Very Hot"},
                        {"time": "18:00", "temp": 31.8, "condition": "Hot & Humid"}
                    ]
                },
                {
                    "date": "2025-09-19",
                    "day": {
                        "maxtemp_c": 35.8,
                        "mintemp_c": 29.3,
                        "condition": {"text": "Sunny", "icon": "☀️"},
                        "avghumidity": 79,
                        "uv": 9.8,
                        "maxwind_kph": 16.2,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 8.2
                    },
                    "pollutants": {
                        "PM25": {"concentration": 41.2, "AQI": 88, "category": "Moderate"},
                        "PM10": {"concentration": 63.4, "AQI": 82, "category": "Moderate"},
                        "O3": {"concentration": 102.8, "AQI": 92, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 29.3, "condition": "Clear"},
                        {"time": "12:00", "temp": 35.2, "condition": "Very Hot"},
                        {"time": "18:00", "temp": 33.1, "condition": "Hot"}
                    ]
                },
                {
                    "date": "2025-09-20",
                    "day": {
                        "maxtemp_c": 33.5,
                        "mintemp_c": 27.9,
                        "condition": {"text": "Partly Cloudy", "icon": "⛅"},
                        "avghumidity": 85,
                        "uv": 7.6,
                        "maxwind_kph": 20.1,
                        "totalprecip_mm": 2.1,
                        "avgvis_km": 7.5
                    },
                    "pollutants": {
                        "PM25": {"concentration": 35.8, "AQI": 76, "category": "Moderate"},
                        "PM10": {"concentration": 52.1, "AQI": 68, "category": "Moderate"},
                        "O3": {"concentration": 78.9, "AQI": 72, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 27.9, "condition": "Cloudy"},
                        {"time": "12:00", "temp": 32.8, "condition": "Partly Cloudy"},
                        {"time": "18:00", "temp": 30.5, "condition": "Light Rain"}
                    ]
                }
            ]
        }
    },
    "surat": {
        "location": {"name": "Surat", "country": "India", "region": "Gujarat"},
        "forecast": {
            "forecastday": [
                {
                    "date": "2025-09-18",
                    "day": {
                        "maxtemp_c": 31.5,
                        "mintemp_c": 24.8,
                        "condition": {"text": "Clear Sky", "icon": "🌞"},
                        "avghumidity": 65,
                        "uv": 7.8,
                        "maxwind_kph": 13.2,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 9.2
                    },
                    "pollutants": {
                        "PM25": {"concentration": 58.9, "AQI": 118, "category": "Unhealthy for Sensitive"},
                        "PM10": {"concentration": 89.3, "AQI": 112, "category": "Unhealthy for Sensitive"},
                        "O3": {"concentration": 75.6, "AQI": 68, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 24.8, "condition": "Clear"},
                        {"time": "12:00", "temp": 30.8, "condition": "Sunny"},
                        {"time": "18:00", "temp": 28.5, "condition": "Clear"}
                    ]
                },
                {
                    "date": "2025-09-19",
                    "day": {
                        "maxtemp_c": 33.2,
                        "mintemp_c": 25.6,
                        "condition": {"text": "Hazy", "icon": "🌫️"},
                        "avghumidity": 62,
                        "uv": 8.5,
                        "maxwind_kph": 11.8,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 6.5
                    },
                    "pollutants": {
                        "PM25": {"concentration": 62.4, "AQI": 125, "category": "Unhealthy for Sensitive"},
                        "PM10": {"concentration": 95.7, "AQI": 118, "category": "Unhealthy for Sensitive"},
                        "O3": {"concentration": 82.3, "AQI": 75, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 25.6, "condition": "Hazy"},
                        {"time": "12:00", "temp": 32.5, "condition": "Very Hazy"},
                        {"time": "18:00", "temp": 30.1, "condition": "Hazy"}
                    ]
                },
                {
                    "date": "2025-09-20",
                    "day": {
                        "maxtemp_c": 30.8,
                        "mintemp_c": 24.2,
                        "condition": {"text": "Light Haze", "icon": "🌫️"},
                        "avghumidity": 68,
                        "uv": 6.9,
                        "maxwind_kph": 15.7,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 7.8
                    },
                    "pollutants": {
                        "PM25": {"concentration": 55.1, "AQI": 110, "category": "Unhealthy for Sensitive"},
                        "PM10": {"concentration": 82.6, "AQI": 105, "category": "Unhealthy for Sensitive"},
                        "O3": {"concentration": 71.8, "AQI": 65, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 24.2, "condition": "Light Haze"},
                        {"time": "12:00", "temp": 30.2, "condition": "Hazy"},
                        {"time": "18:00", "temp": 28.8, "condition": "Clear"}
                    ]
                }
            ]
        }
    },
    "delhi": {
        "location": {"name": "Delhi", "country": "India", "region": "National Capital Territory"},
        "forecast": {
            "forecastday": [
                {
                    "date": "2025-09-18",
                    "day": {
                        "maxtemp_c": 35.8,
                        "mintemp_c": 28.5,
                        "condition": {"text": "Hazy", "icon": "🌫️"},
                        "avghumidity": 58,
                        "uv": 8.9,
                        "maxwind_kph": 10.5,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 4.2
                    },
                    "pollutants": {
                        "PM25": {"concentration": 85.6, "AQI": 158, "category": "Unhealthy"},
                        "PM10": {"concentration": 125.8, "AQI": 148, "category": "Unhealthy"},
                        "O3": {"concentration": 98.2, "AQI": 88, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 28.5, "condition": "Hazy"},
                        {"time": "12:00", "temp": 35.2, "condition": "Very Hazy"},
                        {"time": "18:00", "temp": 33.1, "condition": "Polluted"}
                    ]
                },
                {
                    "date": "2025-09-19",
                    "day": {
                        "maxtemp_c": 37.2,
                        "mintemp_c": 29.8,
                        "condition": {"text": "Very Hazy", "icon": "🌫️"},
                        "avghumidity": 55,
                        "uv": 9.5,
                        "maxwind_kph": 8.3,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 3.1
                    },
                    "pollutants": {
                        "PM25": {"concentration": 92.3, "AQI": 168, "category": "Unhealthy"},
                        "PM10": {"concentration": 138.7, "AQI": 162, "category": "Unhealthy"},
                        "O3": {"concentration": 105.9, "AQI": 95, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 29.8, "condition": "Very Hazy"},
                        {"time": "12:00", "temp": 36.8, "condition": "Severely Polluted"},
                        {"time": "18:00", "temp": 34.5, "condition": "Heavy Pollution"}
                    ]
                },
                {
                    "date": "2025-09-20",
                    "day": {
                        "maxtemp_c": 34.5,
                        "mintemp_c": 27.9,
                        "condition": {"text": "Dusty", "icon": "🌪️"},
                        "avghumidity": 62,
                        "uv": 7.8,
                        "maxwind_kph": 12.7,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 5.8
                    },
                    "pollutants": {
                        "PM25": {"concentration": 78.9, "AQI": 145, "category": "Unhealthy for Sensitive"},
                        "PM10": {"concentration": 115.2, "AQI": 135, "category": "Unhealthy for Sensitive"},
                        "O3": {"concentration": 88.6, "AQI": 78, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 27.9, "condition": "Dusty"},
                        {"time": "12:00", "temp": 33.8, "condition": "Dust Storm"},
                        {"time": "18:00", "temp": 31.5, "condition": "Clearing"}
                    ]
                }
            ]
        }
    }
}

@router.get("/forecast/{location}")
async def get_forecast(location: str, days: Optional[int] = 3):
    """Get enhanced weather and pollutant forecast for specific cities"""
    location_lower = location.lower()
    
    if location_lower in HARDCODED_FORECASTS:
        data = HARDCODED_FORECASTS[location_lower].copy()
        data["is_demo"] = True
        data["is_hardcoded"] = True
        return data
    
    # Enhanced fallback for other locations
    return {
        "location": {
            "name": location.title(),
            "country": "Demo Country",
            "region": "Demo Region"
        },
        "forecast": {
            "forecastday": [
                {
                    "date": "2025-09-18",
                    "day": {
                        "maxtemp_c": 25.0,
                        "mintemp_c": 18.0,
                        "condition": {"text": "Sunny", "icon": "☀️"},
                        "avghumidity": 60,
                        "uv": 6.0,
                        "maxwind_kph": 12.5,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 10.0
                    },
                    "pollutants": {
                        "PM25": {"concentration": 35.0, "AQI": 75, "category": "Moderate"},
                        "PM10": {"concentration": 50.0, "AQI": 68, "category": "Moderate"},
                        "O3": {"concentration": 80.0, "AQI": 72, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 18.0, "condition": "Clear"},
                        {"time": "12:00", "temp": 24.5, "condition": "Sunny"},
                        {"time": "18:00", "temp": 22.8, "condition": "Clear"}
                    ]
                },
                {
                    "date": "2025-09-19",
                    "day": {
                        "maxtemp_c": 23.0,
                        "mintemp_c": 16.0,
                        "condition": {"text": "Partly Cloudy", "icon": "⛅"},
                        "avghumidity": 70,
                        "uv": 5.0,
                        "maxwind_kph": 15.2,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 8.5
                    },
                    "pollutants": {
                        "PM25": {"concentration": 32.0, "AQI": 68, "category": "Moderate"},
                        "PM10": {"concentration": 45.0, "AQI": 62, "category": "Moderate"},
                        "O3": {"concentration": 75.0, "AQI": 68, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 16.0, "condition": "Cloudy"},
                        {"time": "12:00", "temp": 22.5, "condition": "Partly Cloudy"},
                        {"time": "18:00", "temp": 20.8, "condition": "Cloudy"}
                    ]
                },
                {
                    "date": "2025-09-20",
                    "day": {
                        "maxtemp_c": 26.0,
                        "mintemp_c": 19.0,
                        "condition": {"text": "Clear", "icon": "🌞"},
                        "avghumidity": 55,
                        "uv": 7.0,
                        "maxwind_kph": 10.8,
                        "totalprecip_mm": 0.0,
                        "avgvis_km": 12.0
                    },
                    "pollutants": {
                        "PM25": {"concentration": 28.0, "AQI": 58, "category": "Moderate"},
                        "PM10": {"concentration": 40.0, "AQI": 55, "category": "Good"},
                        "O3": {"concentration": 72.0, "AQI": 65, "category": "Moderate"}
                    },
                    "hourly_highlights": [
                        {"time": "06:00", "temp": 19.0, "condition": "Clear"},
                        {"time": "12:00", "temp": 25.5, "condition": "Sunny"},
                        {"time": "18:00", "temp": 23.8, "condition": "Clear"}
                    ]
                }
            ]
        },
        "is_demo": True,
        "is_hardcoded": False
    }