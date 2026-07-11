import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request
from agents.transliterator_agent import run_transliteration, detect_script, run_batch_transliteration

app = Flask(__name__)

AGENTS = [
    {
        "id": "transliterator",
        "name": "Transliterator",
        "description": "Converts names between Arabic and English by sound, not meaning -- auto-detects the script.",
        "url": "/transliterator"
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

if __name__ == "__main__":
    app.run(debug=True)
