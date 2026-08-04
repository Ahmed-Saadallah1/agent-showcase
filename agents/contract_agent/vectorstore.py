import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

embeddings = OpenAIEmbeddings(
    model='openai/text-embedding-3-small',
    api_key=os.environ.get('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=['\n## ', '\n### ', '\n\n', '\n', ' ', ''],
)

_stores = {}
_raw_texts = {}


def build_vectorstore(doc_id: str, markdown_text: str) -> int:
    '''Chunk markdown_text, embed each chunk, store it under doc_id.
    Also keeps the full raw text for tools that need the whole document
    (like risk flagging). Returns the number of chunks created.'''
    chunks = splitter.split_text(markdown_text)
    store = InMemoryVectorStore(embeddings)
    store.add_texts(chunks)
    _stores[doc_id] = store
    _raw_texts[doc_id] = markdown_text
    return len(chunks)


def search_contract(doc_id: str, query: str, k: int = 4) -> list[str]:
    '''Return the k most relevant chunks for a query, or [] if doc_id unknown.'''
    store = _stores.get(doc_id)
    if store is None:
        return []
    results = store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]


def get_raw_text(doc_id: str) -> str | None:
    return _raw_texts.get(doc_id)


def has_contract(doc_id: str) -> bool:
    return doc_id in _stores
