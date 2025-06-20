from datetime import datetime
import requests

weather_code_map = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def get_datetime_with_day():
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    weekday = now.strftime("%A")  # e.g., Monday, Tuesday
    return f"{weekday}, {formatted}"

def get_weather():
    # Step 1: Get current location from IP
    ip_response = requests.get("https://ipinfo.io/json")
    ip_data = ip_response.json()
    loc = ip_data["loc"]  # "lat,lon"
    city = ip_data.get("city", "your area")
    lat, lon = map(float, loc.split(","))

    # Step 2: Call Open-Meteo
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,weathercode"
        "&daily=temperature_2m_max,temperature_2m_min,weathercode"
        "&timezone=Asia%2FTokyo"
    )
    response = requests.get(url)
    data = response.json()

    if "daily" in data:
        temp_min = data["daily"]["temperature_2m_min"][0]
        temp_max = data["daily"]["temperature_2m_max"][0]
        weather_code = data["daily"]["weathercode"][0]
        weather_desc = weather_code_map.get(weather_code, "Unknown")
        return f"Weather in {city}: {temp_min}°C to {temp_max}°C, {weather_desc}"
    else:
        return "Weather data not available."

# Example usage
if __name__ == "__main__":
    # Example usage
    date_time = get_datetime_with_day()
    weather = get_weather()
    print(f"Currently it is {date_time}, {weather}")


