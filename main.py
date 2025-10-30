import requests
from geopy.geocoders import Nominatim

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

if __name__ == "__main__":
    city = input("Enter city name: ")
    try:
        result = get_weather(city)
        print("\n✅ Weather data fetched successfully:")
        for key, value in result.items():
            print(f"{key.capitalize()}: {value}")
    except Exception as e:
        print(f"❌ Error: {e}")
