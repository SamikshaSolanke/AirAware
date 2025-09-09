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

# WeatherAPI configuration
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_BASE_URL = "https://api.weatherapi.com/v1"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/weather/{location}")
async def get_weather(location: str):
    """
    Get current weather data for a specific location
    """
    if WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        # Return demo data when API key is not configured
        return {
            "location": {
                "name": location.title(),
                "country": "Demo Country",
                "region": "Demo Region"
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

@app.get("/api/forecast/{location}")
async def get_forecast(location: str, days: Optional[int] = 3):
    """
    Get weather forecast for a specific location (placeholder for future air quality forecasting)
    """
    if WEATHER_API_KEY == "YOUR_API_KEY_HERE":
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