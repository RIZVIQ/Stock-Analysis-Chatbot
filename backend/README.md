# Stock Analysis Backend Service

FastAPI-powered backend service orchestrating an autonomous financial agent via LangChain, LangGraph, Yahoo Finance (`yfinance`), and Thesys Generative UI (GenUI).

---

## Architecture

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) with asynchronous request handling.
- **Agent Orchestrator**: LangChain `create_agent` with ReAct reasoning loop.
- **LLM / Inference Engine**: Thesys C1 Model (`c1/openai/gpt-5/v-20250930`) via `https://api.thesys.dev/v1/embed/`.
- **Session Checkpointing**: LangGraph `InMemorySaver` maintaining multi-turn conversation memory by `thread_id`.
- **Financial Data Integration**: `yfinance` retrieving quotes, multi-period historical series, balance sheets, and market news.
- **Transport Protocol**: Server-Sent Events (SSE) via `StreamingResponse(..., media_type="text/event-stream")`.

---

## Registered Agent Tools

1. `get_stock_price(ticker: str)`:
   - Fetches the latest closing price from a 5-day historical window.
   - Automatically handles 6-character forex pairs (e.g. `EURUSD` -> `EURUSD=X`).
2. `get_historical_stock_price(ticker: str, start_date: str, end_date: str)`:
   - Queries historical closing prices within the provided date range.
   - Returns a structured mapping of timestamps to prices.
3. `get_balance_sheet(ticker: str)`:
   - Retrieves fundamental balance sheet statements.
   - Validates that the asset is not a forex pair and sanitizes missing values (`fillna("")`).
4. `get_stock_news(ticker: str)`:
   - Fetches up to 5 top financial news articles associated with the ticker symbol.

---

## Setup & Running

### 1. Virtual Environment & Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependencies with uv:
uv sync

# Or with pip:
pip install -e .
```

### 2. Environment Variables

Create `.env` based on `.env.example`:

```bash
OPENAI_API_KEY="sk-th-your-thesys-api-key"
```

### 3. Run the Server

```bash
python main.py
# Or with hot-reload:
uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

---

## API Specification

### `POST /api/chat`
- **Request Body**:
  ```json
  {
    "prompt": {
      "content": "What is the balance sheet of TSLA?",
      "id": "uuid-v4",
      "role": "user"
    },
    "threadId": "session-123",
    "responseId": "resp-123"
  }
  ```
- **Response**: Server-Sent Event stream (`text/event-stream`).
