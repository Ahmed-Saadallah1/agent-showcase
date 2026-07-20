import os
import requests
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

model = ChatOpenAI(
    model="deepseek/deepseek-v4-flash",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    max_retries=5,
    request_timeout=60,
)

WEATHERAPI_KEY = os.environ.get("WEATHERAPI_KEY")

@tool
def get_current_weather(city: str) -> str:
    """Fetch the current weather conditions for a given city name."""
    url = "https://api.weatherapi.com/v1/current.json"
    params = {"key": WEATHERAPI_KEY, "q": city}
    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        return f"Could not find weather data for '{city}'. Please check the city name."

    data = response.json()
    location = data["location"]
    current = data["current"]

    return (
        f"City: {location['name']}, {location['country']}\n"
        f"Temperature: {current['temp_c']}C (feels like {current['feelslike_c']}C)\n"
        f"Condition: {current['condition']['text']}\n"
        f"Humidity: {current['humidity']}%\n"
        f"Wind: {current['wind_kph']} kph, direction {current['wind_dir']}"
    )

agent = create_agent(
    model=model,
    tools=[get_current_weather],
    system_prompt=(
        "You are a helpful weather assistant. When asked about the weather in a city, "
        "use the get_current_weather tool to fetch real data, then summarize it clearly "
        "and naturally in one short paragraph. Always include temperature, condition, "
        "and how it feels. Do not make up data -- only use what the tool returns."
    )
)

def run_weather_check(city: str) -> str:
    result = agent.invoke({
        "messages": [{"role": "user", "content": f"What is the current weather in {city}?"}]
    })
    return result["messages"][-1].content
