import os
import re
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

ARABIC_RE = re.compile(r'[\u0600-\u06FF]')
BOLD_RE = re.compile(r'\*\*(.+?)\*\*')

def detect_script(name: str) -> str:
    """Return 'arabic' if the name contains Arabic script characters, else 'english'."""
    return "arabic" if ARABIC_RE.search(name) else "english"

def clean_output(text: str) -> str:
    """Extract just the transliterated name, stripping markdown and explanatory wrapper text."""
    text = text.strip()
    bold_matches = BOLD_RE.findall(text)
    if bold_matches:
        return bold_matches[-1].strip()
    text = text.strip('*').strip()
    if ':' in text:
        text = text.split(':')[-1].strip()
    text = text.strip('"').strip("'").strip('.').strip()
    return text

@tool
def transliterate_name(name: str) -> str:
    """Transliterate a person's name between Arabic and English automatically, preserving
    pronunciation. NEVER translate the meaning of the name. Reply with ONLY the transliterated name."""
    source_script = detect_script(name)
    target_script = "English" if source_script == "arabic" else "Arabic"
    prompt = (
        f"Transliterate this name into {target_script} script/spelling. "
        f"Preserve how it SOUNDS -- do not translate its meaning, even if the name "
        f"contains a recognizable word. Use standard, common name-spelling conventions -- "
        f"do not add extra letters or vowels that are not pronounced. "
        f"For example, the name Warda should transliterate to وردة, not واردة. "
        f"Output ONLY the transliterated name itself -- no sentences, no explanation, "
        f"no markdown formatting, no bold text, no quotation marks, nothing else.\n\n"
        f"Name: {name}"
    )
    result = model.invoke(prompt)
    return clean_output(result.content)

agent = create_agent(
    model=model,
    tools=[transliterate_name],
    system_prompt=(
        "You are a name transliteration assistant. Your ONLY job is converting names "
        "between Arabic and English scripts phonetically, auto-detecting the input script. "
        "You must NEVER translate the meaning of a name, even if parts of it are recognizable words. "
        "Use the transliterate_name tool. Always return only the clean transliterated name as the "
        "final answer, with no extra sentences or formatting."
    )
)

def run_transliteration(name: str) -> str:
    result = agent.invoke({
        "messages": [{"role": "user", "content": f"Transliterate the name '{name}'"}]
    })
    return clean_output(result["messages"][-1].content)

def run_batch_transliteration(names: list[str]) -> list[dict]:
    """Transliterate a list of names, returning per-name results with any errors isolated."""
    results = []
    for raw_name in names:
        name = raw_name.strip()
        if not name:
            continue
        entry = {"input": name}
        try:
            entry["detected"] = detect_script(name)
            entry["result"] = run_transliteration(name)
            entry["error"] = None
        except Exception as e:
            entry["detected"] = None
            entry["result"] = None
            entry["error"] = str(e)
        results.append(entry)
    return results
