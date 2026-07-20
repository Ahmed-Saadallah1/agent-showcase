import os
import uuid
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, session, jsonify
from agents.transliterator_agent import run_transliteration, detect_script, run_batch_transliteration
from agents.weather_agent import run_weather_check
from agents.worldcup_agent import run_worldcup_chat

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

AGENTS = [
    {
        "id": "transliterator",
        "name": "Transliterator",
        "description": "Converts names between Arabic and English by sound, not meaning -- auto-detects the script.",
        "url": "/transliterator"
    },
    {
        "id": "weather",
        "name": "Weather Agent",
        "description": "Get the current weather for any city, powered by WeatherAPI.",
        "url": "/weather"
    },
    {
        "id": "worldcup",
        "name": "World Cup Historian",
        "description": "Chat about FIFA World Cup stats and history from 1930 to 2026, backed by live search.",
        "url": "/worldcup"
    },
]

@app.route("/")
def index():
    return render_template("index.html", agents=AGENTS)

@app.route("/transliterator", methods=["GET", "POST"])
def transliterator():
    result = None
    error = None
    detected = None
    name_input = ""
    batch_results = None

    if request.method == "POST":
        name_input = request.form.get("name", "").strip()
        if not name_input:
            error = "Please enter at least one name."
        else:
            lines = [line for line in name_input.splitlines() if line.strip()]
            try:
                if len(lines) > 1:
                    batch_results = run_batch_transliteration(lines)
                else:
                    detected = detect_script(name_input)
                    result = run_transliteration(name_input)
            except Exception as e:
                error = f"Something went wrong: {e}"

    return render_template(
        "transliterator.html",
        result=result,
        error=error,
        detected=detected,
        name_input=name_input,
        batch_results=batch_results
    )

@app.route("/weather", methods=["GET", "POST"])
def weather():
    result = None
    error = None
    city_input = ""

    if request.method == "POST":
        city_input = request.form.get("city", "").strip()
        if not city_input:
            error = "Please enter a city name."
        else:
            try:
                result = run_weather_check(city_input)
            except Exception as e:
                error = f"Something went wrong: {e}"

    return render_template(
        "weather.html",
        result=result,
        error=error,
        city_input=city_input
    )

@app.route("/worldcup", methods=["GET"])
def worldcup():
    if "worldcup_thread_id" not in session:
        session["worldcup_thread_id"] = str(uuid.uuid4())
    if "worldcup_history" not in session:
        session["worldcup_history"] = []

    return render_template("worldcup.html", history=session["worldcup_history"])

@app.route("/worldcup/reset", methods=["POST"])
def worldcup_reset():
    session["worldcup_thread_id"] = str(uuid.uuid4())
    session["worldcup_history"] = []
    session.modified = True
    return jsonify({"status": "ok"})

@app.route("/worldcup/message", methods=["POST"])
def worldcup_message():
    if "worldcup_thread_id" not in session:
        session["worldcup_thread_id"] = str(uuid.uuid4())
    if "worldcup_history" not in session:
        session["worldcup_history"] = []

    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Please enter a message."}), 400

    try:
        reply = run_worldcup_chat(user_message, session["worldcup_thread_id"])
        session["worldcup_history"].append({"role": "user", "content": user_message})
        session["worldcup_history"].append({"role": "assistant", "content": reply})
        session.modified = True
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
