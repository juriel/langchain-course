import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import base64
import pandas as pd
import mplfinance as mpf
import yfinance as yf
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator

import sys

# 1. Parámetros
today = datetime.now()
since = today - timedelta(days=1 * 365)
since_str = since.strftime("%Y-%m-%d")

# 2. Ticker
STOCK = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
print("Stock:", STOCK)

# 3. Descargar con auto_adjust=False para tener OHLCV
df = yf.download(STOCK, start=since_str, auto_adjust=False)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
    df.columns.name = None  # importante para que pandas no ponga nombre a las columnas

print(df.columns)  # para verificar

df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)


print(df.columns)
print(df.isna().sum())

df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

df.index.name = "Date"
df = df.reset_index()
df["Date"] = pd.to_datetime(df["Date"])
df = df.set_index("Date")

rsi_period = 14
rsi_indicator = RSIIndicator(close=df["Close"], window=rsi_period)
df["RSI"] = rsi_indicator.rsi()

# RSI en panel 2
rsi_plot = mpf.make_addplot(df["RSI"], panel=2, ylabel="RSI", color="purple")


filename = f"data/stock-{STOCK}.png"
savefig=dict(fname=filename, dpi=100, bbox_inches="tight", pad_inches=0.1)

# Graficar
mpf.plot(
    df,
    type="candle",
    title=f"Candlestick Chart for {STOCK}",
    ylabel="Price",
    style="yahoo",
    mav=(10, 20),
    volume=True,
    addplot=[rsi_plot],  # importante usar lista
    panel_ratios=(6, 2, 2) , # Velas, Volumen, RSI
    figsize=(10.24, 7.68),
    savefig=dict(fname=filename, dpi=100, bbox_inches="tight", pad_inches=0.1)
)


load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


prompt = f"Eres un analista financiero técnico. La imagen tiene un gráfico de velas de {STOCK}. Analiza el gráfico y dame un resumen de la tendencia del precio, el volumen y el RSI. ¿Qué recomendaciones harías para esta acción?  Suguiere compra, venta o mantener"
# Leer y codificar la imagen a base64
with open(filename, "rb") as f:
    image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

# Crear mensaje multimodal
human_message = HumanMessage(content=[
    {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/png;base64,{image_b64}"
        }
    },
    {
        "type": "text",
        "text": prompt
    }
])

# Invocar el modelo (nota: lista con un solo mensaje)
resp = llm.invoke([human_message])

print(type(resp))
print(resp.content)
