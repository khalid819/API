from flask import Flask,render_template,jsonify,request
from flask_cors import CORS
import pyjokes
import webbrowser
import pyttsx3
import requests
import datetime
import wikipedia
from openai import OpenAI
import hijri_converter


# from googletrans import Translator
# translator = Translator()

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Configuration
NEWS_API_KEY = "edae796f6a954f1f9100cb5e2d334c6"
WEATHER_API_KEY = "0040233313863f3ac6c7c383f46c583"
OPENAI_API_KEY = "sk-or-v1-22c9b2c1895a24cb91716c57b9c60a58a3f6a1500e1930cb8c869714e31a4c9"

# Helper functions

def wish():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good morning!"
    elif 12 <= hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

def check_eid():
    today = datetime.date.today()
    hijri_date = hijri_converter.Gregorian(today.year, today.month, today.day).to_hijri()
    if hijri_date.month == 10 and hijri_date.day == 1:
        return "Eid Mubarak! May this Eid bring happiness to you and your family."
    return None

# Command processing functions
def process_web_command(d):
    webbrowser.open(f"https://www.{d}.com")
    return f"Opening {d}"

def process_youtube_search(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Search results for {query} on youtube"

def get_news():
    try:
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}")
        if r.status_code == 200:
            articles = r.json().get('articles', [])
            headlines = [article['title'] for article in articles[:5]]  # Get top 5 headlines
            return "Here are the latest news headlines: " + ". ".join(headlines)
        return "Could not fetch news at this time."
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def get_wikipedia_summary(query):
    wikipedia.set_user_agent("MyWikiApp/1.0 (contact@example.com)")
    if not query:
        return "What would you like me to search on Wikipedia?"
    try:
        # auto_suggest=False helps get more accurate matches
        summary = wikipedia.summary(query, sentences=3, auto_suggest=False)
        return f"According to Wikipedia: {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"There are multiple results for '{query}'. Did you mean: {', '.join(e.options[:3])}?"
    except wikipedia.exceptions.PageError:
        return f"I'm sorry, I couldn't find any Wikipedia page for '{query}'."
    except Exception as e:
        return f"I ran into an issue searching Wikipedia: {str(e)}"


def get_current_time():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return f"The current time is {current_time}"

def get_hijri_date():
    today = datetime.date.today()
    hijri_date = hijri_converter.Gregorian(today.year, today.month, today.day).to_hijri()
    return f"The Hijri date is {hijri_date}"

def get_joke():
    return pyjokes.get_joke()

def get_weather(city):
    try:
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
        return (f"Weather in {city}: {weather.capitalize()}. "
                f"Temperature: {temp}°C (Feels like: {feels_like}°C). "
                f"Humidity: {humidity}%. Wind speed: {wind_speed} m/s.")
    except Exception as e:
        return f"Could not fetch weather: {str(e)}"
conversation_history = []
def process_ai_query(query):
    global conversation_history

    # বর্তমান user message save
    conversation_history.append({
        "role": "user",
        "content": query
    })

    # শেষ 10 message রাখবে
    history = conversation_history[-10:]

    messages = [
        {
            "role": "system",
            "content": """you are in my web app jarvis,
use latex when giving math symbols,
please give every answer in short and plain text.do not use * in plain text. use * in math only please """
        }
    ]

    messages.extend(history)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=messages
    )

    answer = completion.choices[0].message.content

    # AI response save
    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    return answer

def get_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()

        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
        location = data.get('loc')  # latitude and longitude

        return f"your current location..City: {city}, Region: {region}, Country: {country}, Location: {location}"

    except Exception as e:
        return f"Error: {e}"

@app.route('/api/clear_memory', methods=['POST'])
def clear_memory():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "cleared"})
@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command', '').lower()
    response = {"text": "", "action": None}

    try:
        if command.startswith("open"):
            site = command.split(" ")[1]
            response["text"] = process_web_command(site)
            response["action"] = {"type": "open_website", "url": f"https://www.{site}.com"}

        elif "youtube" in command:
            query = command.replace("youtube", "").strip()
            response["text"] = process_youtube_search(query)
            response["action"] = {"type": "open_youtube", "query": query}

        elif "news" in command:
            response["text"] = get_news()

        elif "time" in command:
            response["text"] = get_current_time()

        elif "weather" in command:
            city = command.replace("weather", "").strip() or "New York"
            response["text"] = get_weather(city)

        elif "wiki" in command:
            query = command.replace("wiki", "").strip()
            response["text"] = get_wikipedia_summary(query)

        elif "hijri date" in command:
            response["text"] = get_hijri_date()

        elif "joke" in command:
            response["text"] = get_joke()

        elif "search" in command:
            query = command.replace("search", "").strip()
            response["text"] = f"Searching for {query}"
            response["action"] = {"type": "search_web", "query": query}
        elif "my location" in command:
            response["text"]=get_location()

        else:
            response["text"] = process_ai_query(command)

        # Speak the response

        return jsonify(response)

    except Exception as e:
        return jsonify({"text": f"Sorry, I encountered an error: {str(e)}", "error": True})

@app.route('/api/init', methods=['GET'])
def initialize():
    greeting = wish()
    eid_message = check_eid()
    if eid_message:
        greeting += " " + eid_message
    return jsonify({
        "text": greeting + " I'm Jarvis, your personal assistant. How can I help you today?",
        "greeting": True
    })


@app.route("/")
def home():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/doc")
def docs():
    return render_template("doc.html")
@app.route("/local")
def local():
    return render_template("local.html")
