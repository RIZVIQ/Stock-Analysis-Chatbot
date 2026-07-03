from dotenv import load_dotenv

load_dotenv()
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import uvicorn
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import SystemMessage,HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
import yfinance as yf


app=FastAPI()

model= ChatOpenAI(
    model = 'c1/openai/gpt-5/v-20250930',
    base_url = 'https://api.thesys.dev/v1/embed/'
)
    
checkpointer= InMemorySaver()

@tool('get_stock_price', description='A function that returns the current stock price based on a ticker symbol.')
def get_stock_price(ticker: str):
    print('get_stock_price tool is being used')

    try:
        ticker = ticker.upper().strip()

        # Convert forex pairs like EURUSD -> EURUSD=X
        if len(ticker) == 6 and ticker.isalpha():
            ticker = f"{ticker}=X"

        stock = yf.Ticker(ticker)
        df = stock.history(period="5d")

        if df.empty:
            return {"error": f"No price data found for symbol: {ticker}"}

        return float(df["Close"].iloc[-1])

    except Exception as e:
        return {"error": str(e)}


@tool('get_historical_stock_price', description='A function that returns the current stock price over time based on a ticker symbol and a start and end date.')
def get_historical_stock_price(ticker: str, start_date: str, end_date: str):
    print('get_historical_stock_price tool is being used')

    try:
        ticker = ticker.upper().strip()

        # Convert forex pairs like EURUSD -> EURUSD=X
        if len(ticker) == 6 and ticker.isalpha():
            ticker = f"{ticker}=X"

        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            return {"error": f"No historical data found for symbol: {ticker}"}

        return df["Close"].to_dict()

    except Exception as e:
        return {"error": str(e)}


@tool('get_balance_sheet', description='A function that returns the balance sheet based on a ticker symbol.')
def get_balance_sheet(ticker: str):
    print('get_balance_sheet tool is being used')

    try:
        ticker = ticker.upper().strip()

        # Forex pairs do not have balance sheets
        if len(ticker) == 6 and ticker.isalpha():
            return {"error": "Balance sheet not available for forex pairs."}

        stock = yf.Ticker(ticker)
        sheet = stock.balance_sheet

        if sheet is None or sheet.empty:
            return {"error": f"No balance sheet data found for {ticker}"}

        return sheet.fillna("").to_dict()

    except Exception as e:
        return {"error": str(e)}


@tool('get_stock_news', description='A function that returns news based on a ticker symbol.')
def get_stock_news(ticker: str):
    print('get_stock_news tool is being used')

    try:
        ticker = ticker.upper().strip()

        # Convert forex pairs like EURUSD -> EURUSD=X
        if len(ticker) == 6 and ticker.isalpha():
            ticker = f"{ticker}=X"

        stock = yf.Ticker(ticker)
        news = stock.news

        if not news:
            return {"error": f"No news found for {ticker}"}

        return news[:5]

    except Exception as e:
        return {"error": str(e)}

agent= create_agent(
    model=model,
    checkpointer=checkpointer,
    tools=[get_stock_price, get_historical_stock_price, get_balance_sheet, get_stock_news]
)

class PromptObject(BaseModel):
    content: str
    id: str
    role: str


class RequestObject(BaseModel):
    prompt: PromptObject
    threadId: str
    responseId: str

@app.post('/api/chat')
async def chat(request:RequestObject):
    config={'configurable' : {'thread_id' : request.threadId}}

    def generate():
        for token,_ in agent.stream(
            {
                'messages' : [
                    SystemMessage('You are a stock analysis assistant. you have the ability to get the real-time stock prices, historical stock prices (given a date range), news and balance sheet data for a given ticker symbol.'),
                    HumanMessage(request.prompt.content)
                
            ]},
            stream_mode='messages',
            config=config

        ):
            yield token.content

    return StreamingResponse(generate(),media_type='text/event-stream',
                             headers={
                                 'Cache-Control' :'no-cache, no-transform',
                                 'Connection' : 'keep-alive',
                             } 
                             )


if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0',port=8888)