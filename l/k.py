import requests
WEATHER_API_KEY = "0040233313863f3ac6c7c383f46c5837"
def get_weather():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        city = data.get('city')
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        print (f"Weather in {city}: {weather.capitalize()}. "
                f"Temperature: {temp}°C (Feels like: {feels_like}°C). "
                f"Humidity: {humidity}%. Wind speed: {wind_speed} m/s.")
    except Exception as e:
        print( f"Could not fetch weather: {str(e)}")
get_weather()