# 🌦️ Weather API

A simple FastAPI-based Weather Application that provides real-time weather data, validates user input, and stores results in a local SQLite database.

It uses Open-Meteo for weather and geocoding, Geopy for city coordinate lookup, and provides CRUD operations with optional CSV export.

## 🚀 Features

🌍 Fetch live weather for any city (temperature, windspeed, weather code, coordinates).

🗺️ Auto-generates OpenStreetMap links for quick map access.

🧠 Validates city names and date ranges.

💾 Saves weather records in a local SQLite database.

📤 Exports all data as downloadable CSV.

🧩 Full CRUD API (Create, Read, Update, Delete).

## 🏗️ Tech Stack

Backend: FastAPI

Database: SQLite3

APIs: Open-Meteo & OpenStreetMap (via Geopy)

Language: Python 3.12.3

## 📦 Installation
~~~
# 1. Clone the repository
git clone https://github.com/Chandrakant6/weather-app.git
cd weather-app

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate    # Linux/macOS
# OR
.\.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt
~~~

⚙️ Usage
Run the FastAPI server
~~~
uvicorn main:app --reload
~~~

Access the app

Open your browser at:
👉 http://127.0.0.1:8000/docs
 (Interactive Swagger UI)

Or test endpoints using curl / Postman.

## 📚 API Endpoints
Method	Endpoint	Description
`POST	/weather`	Fetch and store weather data for a city (with optional start & end dates).
`GET	/weather`	Retrieve all stored weather records.
`PUT	/weather/{id}`	Update a city or temperature for a specific record.
`DELETE	/weather/{id}`	Delete a record by ID.
`GET	/export`	Export all weather data as a downloadable `CSV` file.

## 🧠 Input Validation

City Validation: Checks if the city exists using Open-Meteo Geocoding API.

Date Validation: Ensures valid `YYYY-MM-DD` format and logical start–end range.

Error Handling: Returns detailed HTTP errors (400, 404, 503).

## 💾 Database Schema

Table: weather
~~~
Column	Type	Description
id	INTEGER	Auto-increment primary key
city	TEXT	City name
start_date	TEXT	Optional start date
end_date	TEXT	Optional end date
temperature	REAL	Temperature in °C
windspeed	REAL	Windspeed in km/h
weathercode	INTEGER	Weather condition code
map_link	TEXT	OpenStreetMap link
~~~

## 📤 CSV Export Example

Endpoint:

`GET /export`


Response:
A downloadable file named weather_data.csv containing all stored records.

## 🌦️ Example Workflow
~~~
1️⃣ Create
POST /weather?city=Mumbai&start_date=2025-10-01&end_date=2025-10-30

2️⃣ Read
GET /weather

3️⃣ Update
PUT /weather/1?temperature=31.5

4️⃣ Delete
DELETE /weather/1

5️⃣ Export
GET /export
~~~

## 🧩 File Structure
~~~
weather-app/
├── main.py           # FastAPI application, routes, and logic
├── database.py       # SQLite initialization and query utilities
├── requirements.txt  # Python dependencies
├── .gitignore
└── weather.db        # Auto-created SQLite database (on first run)
~~~

## 🧪 Testing Locally

You can test endpoints easily using Swagger UI (/docs) or via curl:
~~~
curl -X 'POST' \
  'http://127.0.0.1:8000/weather?city=Delhi' \
  -H 'accept: application/json'
~~~

## 🛡️ Error Codes
~~~
Code	Meaning
400	Invalid input or processing error
404	City not found
503	External API unavailable
200	Success
~~~
