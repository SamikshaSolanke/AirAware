from fastapi import APIRouter, HTTPException
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"

@router.get("/weather/{location}")
async def get_weather(location: str):
    """Get current weather data for a specific location"""
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        # Return demo data when API key is not configured
        return {
            "location": {
                "name": location.title(),
                "country": "Demo Country",
                "region": "Demo Region",
                "lat": 40.7128,
                "lon": -74.0060
            },
            "current": {
                "temp_c": 22.5,
                "heatindex_c": 25.3,
                "condition": {
                    "text": "Partly Cloudy"
                },
                "humidity": 65,
                "cloud": 40,
                "uv": 5.2,
                "last_updated": "2024-01-01 12:00"
            },
            "is_demo": True
        }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{WEATHER_API_BASE_URL}/current.json",
                params={
                    "key": WEATHER_API_KEY,
                    "q": location,
                    "aqi": "no"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                data["is_demo"] = False
                return data
            else:
                raise HTTPException(status_code=404, detail="Location not found")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Weather service unavailable")
