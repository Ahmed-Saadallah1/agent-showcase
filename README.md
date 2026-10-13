# 🤖 Agent Showcase: LLM Agents Web App

A **Flask web app** that hosts **four AI agents** built with **LangChain** and **LangGraph**. They range from a simple tool-calling agent to a **RAG-powered contract analyzer** that delegates work to sub-agents.

Each agent has its own page with a chat or form interface, all running on one Python backend.

---

## 🧠 The Agents

| Agent | What it does | Key techniques |
|-------|--------------|----------------|
| 📄 **Contract Intelligence** | Upload contracts (PDF/DOCX) and ask questions, flag risky clauses, or compare several contracts. Also answers general legal questions. | RAG, OCR document parsing, structured output, multi-agent planning |
| ⚽ **World Cup Historian** | Chat about FIFA World Cup history and stats (1930–2026), with every fact verified through live web search | Web-search tool, conversation memory, automatic summarization |
| 🌦️ **Weather Agent** | Current weather for any city | Tool calling with an external REST API |
| 🔤 **Transliterator** | Converts names between Arabic and English **by sound, not meaning**, and auto-detects the script. Supports batch input. | Prompt design, script detection, output cleaning |

---

## 📄 Contract Intelligence Agent: How It Works

The most advanced agent in the app:

1. **Parsing**: **Docling** converts uploaded PDF/DOCX files into structured markdown, with **OCR** for scanned contracts and table-structure detection.
2. **Indexing (RAG)**: the text is split into overlapping chunks (1,000 characters, 150 overlap), embedded with `text-embedding-3-small`, and stored in a vector store.
3. **Smart routing**: the agent decides on its own whether a question is about an uploaded contract or about law in general.
4. **Tools the agent can call:**
   - `search_contract`: retrieves the most relevant chunks to give grounded answers
   - `flag_risks`: returns a **structured risk report** (Pydantic schema) with each clause, an excerpt, the concern, and its severity (low / medium / high)
   - `compare_contracts`: hands off to a **Deep Agent** that plans the work, sends each contract to a **sub-agent** for analysis, then combines the findings and recommends the more favorable contract
   - `web_search`: live search for general legal questions

---

## 🛠️ Tech Stack

- **Python**
- **Flask** (web framework) + **Gunicorn** (production server)
- **LangChain / LangGraph** (agents, tools, memory)
- **Deep Agents** (planning + sub-agents)
- **Docling** (document parsing with OCR)
- **Pydantic** (structured LLM output)
- **DeepSeek** LLM via **OpenRouter**
- **Tavily** (web search) · **WeatherAPI**
- **HTML / CSS** (Jinja templates)

---

## 📁 Project Structure

```
├── app.py                      # Flask routes for all agents
├── agents/
│   ├── transliterator_agent.py
│   ├── weather_agent.py
│   ├── worldcup_agent.py
│   └── contract_agent/
│       ├── parsing.py          # Docling PDF/DOCX → markdown (OCR)
│       ├── vectorstore.py      # Chunking, embeddings, retrieval
│       ├── tools.py            # search / risk-flagging / compare / web-search tools
│       ├── deep_agent.py       # Multi-contract comparison with sub-agents
│       └── agent.py            # Main contract agent
├── templates/                  # HTML pages
├── static/                     # CSS
├── requirements.txt
└── Procfile                    # Deployment config
```

---

## ▶️ How to Run

1. Clone the repository
   ```bash
   git clone https://github.com/Ahmed-Saadallah1/agent-showcase.git
   cd agent-showcase
   ```
2. Install the dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys
   ```
   OPENROUTER_API_KEY=your_key
   TAVILY_API_KEY=your_key
   WEATHERAPI_KEY=your_key
   FLASK_SECRET_KEY=any_random_string
   ```
4. Run the app
   ```bash
   flask run
   ```
5. Open `http://127.0.0.1:5000` in your browser

---

## 👤 Author

**Ahmed Saadallah**, Data Science student at GIU
