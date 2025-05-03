import requests

def get_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
        location = data.get('loc')  # latitude and longitude
        
        return f"City: {city}, Region: {region}, Country: {country}, Location: {location}"
    
    except Exception as e:
        return f"Error: {e}"

# Call the function
print(get_location())
