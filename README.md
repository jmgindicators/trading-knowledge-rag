# Trading Knowledge RAG

[![License: MIT](https://img.shields.io/github/license/jmgindicators/trading-knowledge-rag)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Built with Claude](https://img.shields.io/badge/Built_with-Claude_Haiku_4.5-orange.svg)](https://www.anthropic.com/claude)

> Conversational RAG assistant over the documented trading methodology of a professional futures trader.

A retrieval-augmented generation system that answers natural language questions about a structured trading methodology document. Built on local multilingual embeddings, a persistent vector store, and Claude Haiku 4.5, with a Streamlit chat interface that includes source attribution and live cost tracking.

---

## Overview

This project demonstrates a complete production-style RAG pipeline applied to a real-world domain: a documented Spanish-language methodology for trading micro Nasdaq futures (MNQ) on NinjaTrader 8.

The system ingests a structured markdown document, chunks it respecting its semantic hierarchy, encodes each chunk with a multilingual embedding model, persists everything in a local vector database, and serves answers to user questions through a conversational interface. Each response is grounded in the source document and lists the sections consulted.

The methodology used as the knowledge base belongs to **Jose Gonzalez** (`jmgindicators`), a professional futures trader who designed and documented his own trading approach as the foundation for this system.

---

## Screenshots

### Initial view

![Trading Knowledge RAG initial dashboard](docs/screenshots/dashboard.png)

*Welcome screen with system information, technical stack, and three example questions to get the conversation started.*

### Multi-turn conversation

![Conversation example with source attribution](docs/screenshots/chat-conversation.png)

*A two-turn exchange about risk management and the quality filters of the BigTradesDir indicator. The sidebar tracks queries, accumulated cost in USD, and token usage in real time.*

### Sidebar with retrieved sources

![Sidebar showing system info and retrieved chunks](docs/screenshots/sidebar-sources.png)

*The sidebar exposes the underlying retrieval: session metrics and expandable views of the chunks that fed the most recent answer. Every fragment shows its source section and its cosine similarity score.*

---

## Features

- **Markdown-aware chunking** that respects the document's heading hierarchy (`#`, `##`, `###`), with a recursive character-based fallback for sections that exceed the configured chunk size.
- **Local multilingual embeddings** using `paraphrase-multilingual-mpnet-base-v2` (768 dimensions). No external embedding API, no per-query embedding cost.
- **Persistent vector store** with ChromaDB and cosine similarity.
- **Top-K retrieval** with configurable K (default 5), preserving section metadata for source attribution.
- **Claude Haiku 4.5** as the generation model, chosen for the cost-quality trade-off appropriate for synthesis over already-retrieved context.
- **Carefully engineered system prompt** with explicit rules against hallucination, third-person voice, exhaustive use of technical details when available, and consistent source citation at the end of each answer.
- **Conversational memory** across turns: the last user message drives retrieval, but the full chat history is sent to the model so it can resolve references like "expand on point two".
- **Streamlit chat UI** with sidebar showing the technical stack, live session metrics (queries, cost, tokens), and expandable views of the retrieved chunks for full traceability.
- **Cost tracking** in real time per query and accumulated per session.
- **Test suite** of 18 pytest tests covering the ingestion pipeline, retrieval logic, prompt construction, cost calculation, input validation, and end-to-end integration. All external dependencies are mocked so tests are fast, free, and deterministic.

---

## Tech Stack

| Component | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| LLM | Claude Haiku 4.5 (Anthropic) | API |
| Embeddings | sentence-transformers (multilingual mpnet) | 5.5.1 |
| Vector store | ChromaDB | 1.5.9 |
| Chunking | langchain-text-splitters | 1.1.2 |
| Web UI | Streamlit | 1.57.0 |
| Configuration | python-dotenv | 1.2.2 |
| Testing | pytest | 8.3.4 |

---

## Architecture

```mermaid
flowchart TB
    subgraph ingestion["Ingestion (one-time)"]
        direction TB
        A[metodologia.md] --> B[Markdown-aware chunker<br/>plus recursive fallback]
        B --> C[Multilingual embeddings<br/>mpnet 768d]
        C --> D[(ChromaDB<br/>persistent, cosine)]
    end

    subgraph query["Query (per turn)"]
        direction TB
        E[User question] --> F[Embed query<br/>same mpnet model]
        F --> G[Top-K=5 search<br/>cosine similarity]
        G --> H[Prompt assembly<br/>context + history + system]
        H --> I[Claude Haiku 4.5]
        I --> J[Answer with<br/>source citations]
    end

    D -.->|retrieval at query time| G
```

The two phases are decoupled. Ingestion runs once (or whenever the source document changes); querying reuses the persisted vector store and the same embedding model so dimensions remain consistent.

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- An Anthropic API key with available credit ([console.anthropic.com](https://console.anthropic.com))
- Approximately 1.5 GB of free disk space (the multilingual model is cached locally on first run)

### Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/jmgindicators/trading-knowledge-rag.git
cd trading-knowledge-rag
```

Create and activate a virtual environment:

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-real-key-here
```

Use `.env.example` as a template if needed.

### Build the vector store

Run the ingestion pipeline once. The first run downloads the embedding model (around 1.1 GB) and persists the vector store into `chroma_db/`.

```bash
python ingest.py
```

Expected output: chunking summary, embedding generation progress bar, and the number of chunks indexed.

### Run the application

Launch the Streamlit chat UI:

```bash
streamlit run app.py
```

The browser opens automatically at `http://localhost:8501`.

Alternatively, run the chat directly in the terminal:

```bash
python rag.py
```

---

## Usage

### Example questions

The system is designed to answer questions grounded in the documented methodology. Some examples:

- *Cual es la gestion del riesgo de Jose?*
- *Que indicadores propios utiliza?*
- *Como gestiona las salidas de operaciones?*
- *Que filtros de calidad utiliza BigTradesDir?*

For questions outside the scope of the documented methodology, the assistant explicitly states that the topic is not covered, rather than fabricating an answer.

### Conversational follow-ups

The system maintains conversation history across turns. After receiving an answer, the user can ask follow-up questions like *"expand on the second filter"* and the assistant will resolve the reference using the previous turn.

### Cost transparency

Each query displays the input and output token counts and the estimated cost in USD. Typical query cost ranges from $0.001 to $0.004 depending on context size and response length.

---

## Project Structure

```
trading-knowledge-rag/
├── data/
│   └── metodologia.md          # Source document (the trading methodology)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures (mocks for Anthropic, Chroma, embeddings)
│   ├── test_ingest.py          # Chunking tests
│   ├── test_rag.py             # Retrieval and prompt assembly tests
│   └── test_integration.py     # End-to-end pipeline tests
├── docs/
│   └── screenshots/            # UI captures referenced from this README
├── ingest.py                   # Ingestion pipeline: load, chunk, embed, persist
├── rag.py                      # Retrieval and generation engine
├── app.py                      # Streamlit chat UI
├── requirements.txt            # Pinned runtime dependencies
├── pytest.ini                  # Test runner configuration
├── .env.example                # Template for the .env file (no real keys)
├── .gitignore                  # Excludes .env, .venv, chroma_db, caches, etc.
├── LICENSE                     # MIT
└── README.md
```

The `chroma_db/` directory is generated by `ingest.py` and excluded from version control. It can always be regenerated from the source document.

---

## Testing

The project includes 18 tests covering ingestion, retrieval, prompt construction, cost calculation, input validation, and integration. All external dependencies (Anthropic API, ChromaDB, the embedding model) are mocked, so the test suite is fast, free, and reproducible.

Run the full suite:

```bash
pytest
```

Expected output: 18 passed in approximately 10 seconds.

Run a specific module:

```bash
pytest tests/test_ingest.py
pytest tests/test_rag.py
pytest tests/test_integration.py
```

Run a single test:

```bash
pytest tests/test_rag.py::TestCosteAproximado::test_one_million_tokens_each_way
```

---

## Roadmap

Future plans include multi-agent orchestration, persistent conversation history across sessions, and additional knowledge sources such as trade journal entries and recorded session transcripts.

---

## License

MIT License. See [LICENSE](LICENSE) for the full text.

---

## Author

Developed by **Jose Gonzalez** ([jmgindicators](https://github.com/jmgindicators)), professional futures trader expanding into AI engineering. The documented methodology that powers this RAG system is the result of years of live discretionary trading on MNQ futures.

---

## Acknowledgements

- Anthropic for the Claude API.
- The sentence-transformers project for accessible multilingual embeddings.
- The ChromaDB team for a clean, embeddable vector database.
