import os
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

model = ChatOpenAI(
    model='deepseek/deepseek-v4-flash',
    api_key=os.environ.get('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
    max_retries=5,
    request_timeout=120,
)

comparison_agent = create_deep_agent(
    model=model,
    tools=[],
    system_prompt=(
        'You are a contract comparison specialist. You will be given the full text '
        "of two or more contracts, each clearly labeled (e.g. 'Contract A', 'Contract B'). "
        'Your job:\n'
        '1. Plan your approach using your planning tool before starting.\n'
        '2. For each contract, delegate an in-depth analysis to a subagent -- extract '
        'key terms: payment terms, termination rights, liability, auto-renewal, '
        'confidentiality obligations, and any unusual or one-sided clauses. Have each '
        'subagent write its findings to a file (e.g. contract_a_analysis.md) instead of '
        'returning everything directly, so nothing gets lost.\n'
        '3. Once all subagents report back, read their files and synthesize a final '
        'comparison: a clear summary of the key differences, and a recommendation of '
        'which contract is more favorable, with reasons.\n'
        'Write your final comparison as clean, well-structured markdown.'
    ),
)


def compare_contracts(labeled_contracts: dict) -> str:
    '''labeled_contracts: e.g. {"Contract A": full_text_a, "Contract B": full_text_b}'''
    parts = [f'=== {label} ===\n{text}' for label, text in labeled_contracts.items()]
    combined_input = '\n\n'.join(parts)

    result = comparison_agent.invoke({
        'messages': [{'role': 'user', 'content': f'Compare these contracts:\n\n{combined_input}'}]
    })
    return result['messages'][-1].content
