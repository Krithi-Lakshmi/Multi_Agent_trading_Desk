import asyncio
import random
from pathlib import Path
from typing import TypedDict, List, Dict, Any

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from langgraph.graph import StateGraph, END

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI()
connections: List[WebSocket] = []


class TradingState(TypedDict):
    price: float
    news_score: float
    tech_score: float
    risk_score: float
    decision: str
    logs: List[str]


def news_agent(state: TradingState):
    sentiment = random.uniform(-1, 1) * 100
    log = f"📰 News Agent: sentiment={sentiment:.2f}"
    state["news_score"] = sentiment
    state["logs"].append(log)
    return state


def technical_agent(state: TradingState):
    price = state["price"]
    moving_avg = 150
    score = (price - moving_avg) / moving_avg * 100
    log = f"📊 Technical Agent: score={score:.2f}"
    state["tech_score"] = score
    state["logs"].append(log)
    return state


def risk_agent(state: TradingState):
    volatility = random.uniform(0, 100)
    log = f"⚠️ Risk Agent: risk={volatility:.2f}"
    state["risk_score"] = volatility
    state["logs"].append(log)
    return state


def portfolio_agent(state: TradingState):
    score = (
        state["news_score"] * 0.4
        + state["tech_score"] * 0.4
        - state["risk_score"] * 0.2
    )

    if score > 20:
        decision = "BUY 📈"
    elif score < -20:
        decision = "SELL 📉"
    else:
        decision = "HOLD ✋"

    log = f"💼 Portfolio Agent: decision={decision} | score={score:.2f}"
    state["decision"] = decision
    state["logs"].append(log)
    return state


graph = StateGraph(TradingState)
graph.add_node("news", news_agent)
graph.add_node("tech", technical_agent)
graph.add_node("risk", risk_agent)
graph.add_node("portfolio", portfolio_agent)
graph.set_entry_point("news")
graph.add_edge("news", "tech")
graph.add_edge("tech", "risk")
graph.add_edge("risk", "portfolio")
graph.add_edge("portfolio", END)
app_graph = graph.compile()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})   


@app.get("/health")
async def health():
    return {"status": "ok"}


async def generate_price():
    return round(random.uniform(140, 160), 2)


async def broadcast(message: Dict[str, Any]):
    dead = []
    for ws in connections:
        try:
            await ws.send_json(message)
        except:
            dead.append(ws)
    for ws in dead:
        if ws in connections:
            connections.remove(ws)


async def trading_engine(max_cycles: int = 5):
    for _ in range(max_cycles):
        price = await generate_price()

        state: TradingState = {
            "price": price,
            "news_score": 0,
            "tech_score": 0,
            "risk_score": 0,
            "decision": "",
            "logs": []
        }
        result = await app_graph.ainvoke(state)
        for log in result["logs"]:
            await broadcast({"type": "log", "data": log})
        await asyncio.sleep(2)

        state = news_agent(state)
        await broadcast({"type": "price", "data": f"Price: {price}"})
        await broadcast({"type": "news", "data": state["logs"][-1]})
        await asyncio.sleep(1)

        state = technical_agent(state)
        await broadcast({"type": "tech", "data": state["logs"][-1]})
        await asyncio.sleep(1)

        state = risk_agent(state)
        await broadcast({"type": "risk", "data": state["logs"][-1]})
        await asyncio.sleep(1)

        state = portfolio_agent(state)
        await broadcast({"type": "decision", "data": state["logs"][-1]})
        await asyncio.sleep(2)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        if websocket in connections:
            connections.remove(websocket)


@app.on_event("startup")
async def startup():
    app.state.trading_task = asyncio.create_task(trading_engine())


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
