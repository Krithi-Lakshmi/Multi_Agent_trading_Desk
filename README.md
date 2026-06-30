# Multi-Agent Trading Desk

A real-time trading **simulation** where multiple AI agents collaborate to produce a BUY / HOLD / SELL decision, orchestrated with **LangGraph** and streamed live to a **FastAPI + WebSockets** dashboard.

> ⚠️ This is a simulation for learning purposes. Prices, sentiment, and risk are randomly generated — it is **not** financial advice and makes no real trades.

## Agents

| Agent | Role |
|-------|------|
| 📰 News Agent | Generates a market sentiment score |
| 📊 Technical Agent | Scores price trend via a moving-average strategy |
| ⚠️ Risk Agent | Estimates volatility / portfolio risk |
| 💼 Portfolio Agent | Combines the scores into a BUY / HOLD / SELL call |

The agents run as nodes in a LangGraph `StateGraph` (`news → tech → risk → portfolio`), making the workflow modular and easy to extend.

## Tech stack

LangGraph · FastAPI · WebSockets · Jinja2 · AsyncIO · Python

## Project structure

```
.
├── Multi_Agent_Trading_Desk.py
├── templates/
│   └── dashboard.html
├── requirements.txt
└── README.md
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn Multi_Agent_Trading_Desk:app --reload
```

Then open <http://127.0.0.1:8000/> to watch prices, agent reasoning logs, and decisions stream in real time. Health check: <http://127.0.0.1:8000/health>.

## Notes

- Tested on Python 3.12. Some dependencies still have rough edges on Python 3.14.
- `starlette` is pinned `<1.0.0` because 1.0.0 removed the older `TemplateResponse` calling convention.

## License

MIT
