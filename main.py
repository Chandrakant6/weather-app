from fastapi import FastAPI, Query, HTTPException
from geopy.geocoders import Nominatim
import requests

from datetime import datetime

from database import init_db, execute_query, fetch_all


app = FastAPI(title="Weather API", version="1.0")
init_db()

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


def validate_location(location: str):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}"
    try:
        res = requests.get(geo_url, timeout=5)
        res.raise_for_status()  # raise HTTPError for 4xx/5xx from API
        data = res.json()
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Location service unavailable. Try again later.")

    # Check if results exist
    if "results" not in data or not data["results"]:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found.")

def validate_date_range(start_date: str, end_date: str):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        # If the format is wrong, e.g. "2025-13-40"
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if start > end:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date.")

    return True


# CREATE
@app.post("/weather")
def create_weather(city: str = Query(...), start_date: str = Query(None), end_date: str = Query(None)):

    validate_location(city)
    if start_date and end_date:
        validate_date_range(start_date, end_date)

    try:
        weather = get_weather(city)
        execute_query(
            "INSERT INTO weather (city, start_date, end_date, temperature, windspeed, weathercode) VALUES (?, ?, ?, ?, ?, ?)",
            (weather["city"], start_date, end_date, weather["temperature"], weather["windspeed"], weather["weathercode"])
        )
        return {"status": "success", "data": weather}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# READ
@app.get("/weather")
def read_weather():
    rows = fetch_all("SELECT * FROM weather")
    data = [
        {
            "id": r[0],
            "city": r[1],
            "start_date": r[2],
            "end_date": r[3],
            "temperature": r[4],
            "windspeed": r[5],
            "weathercode": r[6],
        }
        for r in rows
    ]
    return {"count": len(data), "data": data}

# UPDATE
@app.put("/weather/{id}")
def update_weather(id: int, city: str = Query(None), temperature: float = Query(None)):
    try:
        if city:
            execute_query("UPDATE weather SET city=? WHERE id=?", (city, id))
        if temperature:
            execute_query("UPDATE weather SET temperature=? WHERE id=?", (temperature, id))
        return {"status": "success", "message": f"Record {id} updated."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# DELETE
@app.delete("/weather/{id}")
def delete_weather(id: int):
    try:
        execute_query("DELETE FROM weather WHERE id=?", (id,))
        return {"status": "success", "message": f"Record {id} deleted."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))