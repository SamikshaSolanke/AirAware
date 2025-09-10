from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
from typing import Optional
import uvicorn
from dotenv import load_dotenv

app = FastAPI(title="Air Quality Visualizer", version="1.0.0")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")

# API configuration
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
AMBEE_API_KEY = os.getenv("AMBEE_API_KEY")
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"
AMBEE_API_BASE_URL = "https://api.ambeedata.com"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/weather/{location}")
async def get_weather(location: str):
    """
    Get current weather data for a specific location
    """
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

@app.get("/api/aqi/{location}")
async def get_aqi_by_city(location: str):
    """
    Get air quality index data for a specific city using Ambee API
    """
    if not AMBEE_API_KEY or AMBEE_API_KEY == "YOUR_AMBEE_API_KEY_HERE":
        # Return demo AQI data when API key is not configured
        return {
            "stations": [{
                "city": location.title(),
                "countryCode": "US",
                "division": "Demo State",
                "lat": 40.7128,
                "lng": -74.0060,
                "placeName": location.title(),
                "postalCode": "10001",
                "state": "Demo State",
                "updatedAt": "2024-01-01T12:00:00.000Z",
                "AQI": 85,
                "aqiInfo": {
                    "pollutant": "PM2.5",
                    "concentration": 25.3,
                    "category": "Moderate"
                },
                "CO": {
                    "concentration": 0.5,
                    "AQI": 5
                },
                "NO2": {
                    "concentration": 15.2,
                    "AQI": 12
                },
                "OZONE": {
                    "concentration": 45.8,
                    "AQI": 35
                },
                "PM10": {
                    "concentration": 35.7,
                    "AQI": 32
                },
                "PM25": {
                    "concentration": 25.3,
                    "AQI": 85
                },
                "SO2": {
                    "concentration": 8.9,
                    "AQI": 6
                }
            }],
            "is_demo": True
        }
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": AMBEE_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{AMBEE_API_BASE_URL}/latest/by-city",
                headers=headers,
                params={"city": location}
            )
            
            if response.status_code == 200:
                data = response.json()
                data["is_demo"] = False
                return data
            else:
                raise HTTPException(status_code=404, detail="Air quality data not found for this location")
                
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Air quality service unavailable")

@app.get("/api/aqi/coordinates")
async def get_aqi_by_coordinates(lat: float, lng: float):
    """
    Get air quality index data for specific coordinates using Ambee API
    """
    if not AMBEE_API_KEY or AMBEE_API_KEY == "YOUR_AMBEE_API_KEY_HERE":
        # Return demo AQI data when API key is not configured
        return {
            "stations": [{
                "city": "Demo City",
                "countryCode": "US",
                "division": "Demo State",
                "lat": lat,
                "lng": lng,
                "placeName": "Demo Location",
                "postalCode": "10001",
                "state": "Demo State",
                "updatedAt": "2024-01-01T12:00:00.000Z",
                "AQI": 75,
                "aqiInfo": {
                    "pollutant": "PM2.5",
                    "concentration": 22.1,
                    "category": "Moderate"
                },
                "CO": {
                    "concentration": 0.4,
                    "AQI": 4
                },
                "NO2": {
                    "concentration": 12.8,
                    "AQI": 10
                },
                "OZONE": {
                    "concentration": 42.3,
                    "AQI": 32
                },
                "PM10": {
                    "concentration": 32.5,
                    "AQI": 29
                },
                "PM25": {
                    "concentration": 22.1,
                    "AQI": 75
                },
                "SO2": {
                    "concentration": 7.2,
                    "AQI": 5
                }
            }],
            "is_demo": True
        }
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "x-api-key": AMBEE_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{AMBEE_API_BASE_URL}/latest/by-lat-lng",
                headers=headers,
                params={"lat": lat, "lng": lng}
            )
            
            if response.status_code == 200:
                data = response.json()
                data["is_demo"] = False
                return data
            else:
                raise HTTPException(status_code=404, detail="Air quality data not found for these coordinates")
                
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Air quality service unavailable")

@app.get("/api/forecast/{location}")
async def get_forecast(location: str, days: Optional[int] = 3):
    """
    Get weather forecast for a specific location (placeholder for future air quality forecasting)
    """
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        # Return demo forecast data
        return {
            "location": {
                "name": location.title(),
                "country": "Demo Country"
            },
            "forecast": {
                "forecastday": [
                    {
                        "date": "2024-01-01",
                        "day": {
                            "maxtemp_c": 25.0,
                            "mintemp_c": 18.0,
                            "condition": {"text": "Sunny"},
                            "avghumidity": 60,
                            "uv": 6.0
                        }
                    },
                    {
                        "date": "2024-01-02",
                        "day": {
                            "maxtemp_c": 23.0,
                            "mintemp_c": 16.0,
                            "condition": {"text": "Partly Cloudy"},
                            "avghumidity": 70,
                            "uv": 5.0
                        }
                    }
                ]
            },
            "is_demo": True
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{WEATHER_API_BASE_URL}/forecast.json",
                params={
                    "key": WEATHER_API_KEY,
                    "q": location,
                    "days": min(days, 10),  # API limits to 10 days
                    "aqi": "yes"  # Include air quality in future
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Air Quality Visualizer API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )