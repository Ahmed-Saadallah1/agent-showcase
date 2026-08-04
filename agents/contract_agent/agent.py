import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from .tools import search_contract, flag_risks, compare_contracts, web_search_tool

model = ChatOpenAI(
    model='deepseek/deepseek-v4-flash',
    api_key=os.environ.get('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
    max_retries=5,
    request_timeout=60,
)

checkpointer = MemorySaver()

agent = create_agent(
    model=model,
    tools=[search_contract, flag_risks, compare_contracts, web_search_tool],
    system_prompt=(
        'You are a legal assistant with two modes:\n\n'
        '1. CONTRACT MODE -- if contracts are currently uploaded (you will be told '
        'their doc_ids and filenames) and the question is about a SPECIFIC uploaded '
        'contract, use search_contract (grounded Q&A), flag_risks (risk scanning), or '
        'compare_contracts (if 2+ contracts and a comparison is wanted).\n\n'
        '2. GENERAL LEGAL MODE -- if the question is about law in general and NOT tied '
        "to an uploaded contract (e.g. 'what are human rights in Egypt'), use the "
        'web_search tool and answer from current, accurate results. No contract needs '
        'to be uploaded for this mode.\n\n'
        'Decide the mode from the question itself and whether relevant documents are '
        'currently uploaded.\n\n'
        'STYLE RULES -- follow these strictly:\n'
        '- Be concise. Answer only what was asked, in 3-6 sentences unless the user '
        'explicitly asks for more detail.\n'
        '- Do not use markdown tables or headers for simple factual answers -- a short '
        'paragraph or a brief bullet list is enough.\n'
        '- Only use flag_risks output (which is naturally longer) when specifically '
        'asked for a risk report.\n'
        '- Keep any quoted contract text short.'
    ),
    checkpointer=checkpointer,
)


def run_contract_chat(message: str, thread_id: str, uploaded_docs: list) -> str:
    config = {'configurable': {'thread_id': thread_id}}
    context_note = ''
    if uploaded_docs:
        doc_list = '\n'.join(f"- {d['filename']} (doc_id: {d['doc_id']})" for d in uploaded_docs)
        context_note = f'[Currently uploaded contracts:\n{doc_list}]\n\n'
    result = agent.invoke(
        {'messages': [{'role': 'user', 'content': context_note + message}]},
        config,
    )
    return result['messages'][-1].content
