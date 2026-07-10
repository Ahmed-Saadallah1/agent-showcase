import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request
from agents.translator_agent import run_translation

app = Flask(__name__)

AGENTS = [
    {
        "id": "translator",
        "name": "Translator Agent",
        "description": "Translates text into any language using an LLM-powered tool-calling agent.",
        "url": "/translator"
    },
]

@app.route("/")
def index():
    return render_template("index.html", agents=AGENTS)

@app.route("/translator", methods=["GET", "POST"])
def translator():
    result = None
    error = None
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        target_language = request.form.get("target_language", "").strip()
        if not text or not target_language:
            error = "Please provide both text and a target language."
        else:
            try:
                result = run_translation(text, target_language)
            except Exception as e:
                error = f"Something went wrong: {e}"
    return render_template("translator.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
