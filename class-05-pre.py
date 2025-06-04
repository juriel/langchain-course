import yfinance as yf
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import sys

import pandas as pd
import mplfinance as mpf
import yfinance as yf
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator


# 1. Parámetros
today = datetime.now()
since = today - timedelta(days=4 * 365)
since_str = since.strftime("%Y-%m-%d")

# 2. Ticker
STOCK = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
print("Stock:", STOCK)

# 3. Descargar con auto_adjust=False para tener OHLCV
df = yf.download(STOCK, start=since_str, auto_adjust=False)
print(df.head())
print(df.tail())

# 4. Verifica y convierte a float (puede venir con object o NaN)
ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
df = df[ohlcv_cols].copy()
df = df.astype(float).fillna(0)
df[ohlcv_cols] = df[ohlcv_cols].apply(pd.to_numeric, errors='coerce')
df = df.dropna()

# 5. Calcular RSI
rsi = RSIIndicator(close=df['Close'].astype(float).squeeze(), window=14)
df['RSI'] = rsi.rsi()

# 6. Prepara addplot para RSI
rsi_data = df[['RSI']].dropna()
apds = [
    mpf.make_addplot(rsi_data['RSI'], panel=1, color='orange', ylabel='RSI'),
    mpf.make_addplot([70]*len(rsi_data), panel=1, color='red', linestyle='dotted'),
    mpf.make_addplot([30]*len(rsi_data), panel=1, color='green', linestyle='dotted')
]

# 7. Graficar con mplfinance
mpf.plot(
    df,
    type='candle',
    volume=True,
    style='yahoo',
    addplot=apds,
    title=f"{STOCK} - Velas + Volumen + RSI",
    figratio=(18, 10),
    figscale=1.2,
    panel_ratios=(3, 1),
    mav=(20, 50),
    savefig=f"{STOCK}_mplfinance.png"
)
