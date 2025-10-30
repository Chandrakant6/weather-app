from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from geopy.geocoders import Nominatim
import requests

from datetime import datetime
import sqlite3
import csv
import io

from database import DB_NAME, init_db, execute_query, fetch_all


app = FastAPI(title="Weather API", version="1.0")
init_db()

@app.get("/", summary="Welcome")
def root():
    return {
        "message": "Welcome to the Weather App 🌦️",
        "developer": "Chandrakant Turkar",
        "description": (
            "This app provides real-time weather information with full CRUD "
            "functionality, location validation, CSV export, and map integration."
        ),
        "info_endpoint": "/info",
        "docs": "/docs",
        "company": {
            "name": "Product Manager Accelerator",
            "linkedin": "https://www.linkedin.com/school/pmaccelerator/"
        }
    }

@app.get("/info", summary="App and Company Info")
def info():
    return {
        "app_name": "Weather App",
        "version": "1.0.0",
        "developer": {
            "name": "Chandrakant Turkar",
            "role": "Python Developer Intern",
            "github": "https://github.com/Chandrakant6",
            "linkedin": "https://www.linkedin.com/in/chandrakant-turkar-86b2112a1"
        },
        "company": {
            "name": "Product Manager Accelerator",
            "linkedin": "https://www.linkedin.com/school/pmaccelerator/",
            "description": (
                "Product Manager Accelerator (PMA) is a global learning platform "
                "for aspiring and professional product managers, helping them "
                "build, launch, and scale real-world products."
            )
        },
        "endpoints": {
            "root": "/",
            "weather": "/weather",
            "docs": "/docs"
        }
    }


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
        "weathercode": weather["weathercode"],
        "map_link" : f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=10/{lat}/{lon}"
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

def export_weather_data():
    """Exports all weather data from the database as a CSV stream."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM weather")
    rows = cursor.fetchall()

    # Get column names dynamically
    col_names = [description[0] for description in cursor.description]

    conn.close()

    # Convert to CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(col_names)
    writer.writerows(rows)
    output.seek(0)

    return output


# CREATE
@app.post("/weather")
def create_weather(city: str = Query(...), start_date: str = Query(None), end_date: str = Query(None)):

    validate_location(city)
    if start_date and end_date:
        validate_date_range(start_date, end_date)

    try:
        weather = get_weather(city)
        execute_query(
            "INSERT INTO weather (city, start_date, end_date, temperature, windspeed, weathercode, map_link) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (weather["city"], start_date, end_date, weather["temperature"], weather["windspeed"], weather["weathercode"], weather["map_link"])
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
            "map_link" : r[7]
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

# data export 
@app.get("/export", tags=["Utilities"])
def export_data():
    output = export_weather_data()
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_data.csv"}
    )