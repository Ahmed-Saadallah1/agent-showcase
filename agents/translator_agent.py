import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

model = ChatOpenAI(
    model="openrouter/free",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

@tool
def translate_text(text: str, target_language: str) -> str:
    """Translate the given text into the target language. Reply with ONLY the translated text."""
    prompt = f"Translate this text into {target_language}. Reply with ONLY the translation, no explanation.\n\nText: {text}"
    result = model.invoke(prompt)
    return result.content.strip()

agent = create_agent(
    model=model,
    tools=[translate_text],
    system_prompt="You are a translation assistant. Translate the given text into the target language using the translate_text tool."
)

def run_translation(text: str, target_language: str) -> str:
    result = agent.invoke({
        "messages": [{"role": "user", "content": f"Translate '{text}' into {target_language}"}]
    })
    return result["messages"][-1].content
