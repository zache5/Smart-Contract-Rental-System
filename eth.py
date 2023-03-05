import yfinance as yf
from prophet import Prophet
import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

start = "2020-01-01"
today = date.today().strftime("%Y-%m-%d")
data = yf.download("ETH-USD",start,today)

# Displaying latest price
latest_price = data['Close'].iloc[-1]
st.sidebar.subheader(f"The most recent price of Ethereum is {latest_price:.2f} USD")

# Forecasting the components of ETH so that customer can check daily trends
df_train = data[['Close']].reset_index().rename(columns={'Date': 'ds', 'Close': 'y'})
m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=365)
forecast = m.predict(future)

# Extract weekly seasonality component from the forecast dataframe
weekly = forecast[['ds', 'weekly']]
weekly.set_index('ds', inplace=True)

# Plot weekly seasonality component
st.sidebar.subheader("Weekly seasonality")
fig, ax = plt.subplots()
weekly.plot(ax=ax)
ax.set_xlabel('Date')
ax.set_ylabel('Weekly seasonality')
st.sidebar.write(fig)
