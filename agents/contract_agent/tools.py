import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from .vectorstore import search_contract as _search_contract, get_raw_text
from .deep_agent import compare_contracts as _compare_contracts

model = ChatOpenAI(
    model='deepseek/deepseek-v4-flash',
    api_key=os.environ.get('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
    max_retries=5,
    request_timeout=60,
)

web_search_tool = TavilySearch(
    max_results=5,
    api_key=os.environ.get('TAVILY_API_KEY'),
)


@tool
def search_contract(doc_id: str, query: str) -> str:
    '''Search a specific uploaded contract for text relevant to a question.
    Use this when the user asks about a SPECIFIC uploaded contract
    (e.g. what is the termination notice period). Requires the doc_id.'''
    chunks = _search_contract(doc_id, query)
    if not chunks:
        return 'No contract found with that ID, or no relevant text found.'
    return '\n\n---\n\n'.join(chunks)


class RiskyClause(BaseModel):
    clause: str = Field(description="Short name of the clause, e.g. 'Auto-renewal'")
    excerpt: str = Field(description='Relevant excerpt from the contract, 1-2 sentences')
    concern: str = Field(description='Why this clause could be risky, in plain language')
    severity: Literal['low', 'medium', 'high']


class RiskReport(BaseModel):
    risks: list[RiskyClause]


@tool
def flag_risks(doc_id: str) -> str:
    '''Scan an uploaded contract for risky or one-sided clauses (auto-renewal,
    unlimited liability, one-sided termination rights, missing clauses) and
    return a structured risk summary. Requires the doc_id.'''
    text = get_raw_text(doc_id)
    if not text:
        return 'No contract found with that ID.'
    structured_model = model.with_structured_output(RiskReport)
    prompt = (
        'Analyze this contract and identify risky or one-sided clauses. '
        'Look specifically for: auto-renewal terms, unlimited or one-sided liability, '
        'unfair termination rights, unusual penalty clauses, and any important clause '
        'that appears to be MISSING (e.g. no confidentiality clause). '
        f'Contract text:\n\n{text[:12000]}'
    )
    report = structured_model.invoke(prompt)
    if not report.risks:
        return 'No significant risks flagged in this contract.'
    lines = []
    for r in report.risks:
        lines.append(f'[{r.severity.upper()}] {r.clause}: {r.concern}\n  Excerpt: "{r.excerpt}"')
    return '\n\n'.join(lines)


@tool
def compare_contracts(doc_ids: list[str]) -> str:
    '''Compare two or more uploaded contracts and produce a synthesized comparison,
    highlighting differences and which is more favorable. Requires a list of at
    least 2 doc_ids.'''
    if len(doc_ids) < 2:
        return 'Need at least two uploaded contracts to compare.'
    labeled = {}
    for i, doc_id in enumerate(doc_ids):
        text = get_raw_text(doc_id)
        if not text:
            return f"Contract '{doc_id}' not found."
        labeled[f'Contract {chr(65 + i)}'] = text
    return _compare_contracts(labeled)
