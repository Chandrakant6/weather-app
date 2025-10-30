from fastapi import FastAPI, Query, HTTPException
from geopy.geocoders import Nominatim
import requests

app = FastAPI(title="Weather API", version="1.0")

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city_name)
    if not location:
        raise ValueError("City not found.")
    return location.latitude, location.longitude

def get_weather(city_name):
    lat, lon = get_coordinates(city_name)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    data = response.json()
    if "current_weather" not in data:
        raise ValueError("Weather data not found.")
    weather = data["current_weather"]
    return {
        "city": city_name,
        "latitude": lat,
        "longitude": lon,
        "temperature": weather["temperature"],
        "windspeed": weather["windspeed"],
        "weathercode": weather["weathercode"]
    }

@app.get("/weather")
def read_weather(city: str = Query(..., description="Enter city name")):
    """
    Fetch live weather data for a city using Open-Meteo API.
    """
    try:
        data = get_weather(city)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
