import os
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import MemorySaver

model = ChatOpenAI(
    model="deepseek/deepseek-v4-flash",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    max_retries=5,
    request_timeout=60,
)

search_tool = TavilySearch(
    max_results=5,
    api_key=os.environ.get("TAVILY_API_KEY"),
)

checkpointer = MemorySaver()

agent = create_agent(
    model=model,
    tools=[search_tool],
    system_prompt=(
        "You are a FIFA World Cup historian and statistics expert, covering every "
        "tournament from 1930 to 2026. Always use the search tool to verify facts, "
        "scores, records, and statistics before answering -- never rely on memory alone, "
        "since exact numbers matter and must be accurate. "
        "Keep answers SHORT and DIRECT -- answer only what was asked, in 1-3 sentences. "
        "Do not add extra trivia, follow-up suggestions, emojis, or bullet lists unless "
        "specifically asked for more detail. No bold text or markdown formatting. "
        "Write like a knowledgeable friend giving a quick, precise answer -- not a report."
    ),
    checkpointer=checkpointer,
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=("tokens", 3000),
            keep=("messages", 10),
        ),
    ],
)

def run_worldcup_chat(message: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config,
    )
    return result["messages"][-1].content
