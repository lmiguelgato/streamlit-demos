import base64
import json
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup


def filedownload(df):
    # Let the user download S&P500 data
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Crypto_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv">📥 Download data as CSV File</a>'
    return href


@st.cache
def load_data(currency_price_unit):
    cmc = requests.get("https://coinmarketcap.com")
    soup = BeautifulSoup(cmc.content, "html.parser")

    data = soup.find("script", id="__NEXT_DATA__", type="application/json")
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data["props"]["initialState"]["cryptocurrency"]["listingLatest"][
        "data"
    ]
    for i in listings:
        coins[str(i["id"])] = i["slug"]

    coin_name = []
    coin_symbol = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for i in listings:
        coin_name.append(i["slug"])
        coin_symbol.append(i["symbol"])
        price.append(i["quote"][currency_price_unit]["price"])
        percent_change_1h.append(i["quote"][currency_price_unit]["percentChange1h"])
        percent_change_24h.append(i["quote"][currency_price_unit]["percentChange24h"])
        percent_change_7d.append(i["quote"][currency_price_unit]["percentChange7d"])
        volume_24h.append(i["quote"][currency_price_unit]["volume24h"])

    df = pd.DataFrame(
        columns=[
            "Name",
            "Symbol",
            "1 hour change (%)",
            "24 hours change (%)",
            "7 days change (%)",
            "Price",
            "24-hour volume",
        ]
    )
    df["Name"] = coin_name
    df["Symbol"] = coin_symbol
    df["Price"] = price
    df["1 hour change (%)"] = percent_change_1h
    df["24 hours change (%)"] = percent_change_24h
    df["7 days change (%)"] = percent_change_7d
    df["24-hour volume"] = volume_24h
    return df


def crypto():
    currency_price_unit = st.sidebar.selectbox(
        "Currency in which price is displayed:", ("USD", "BTC", "ETH")
    )
    if currency_price_unit != "USD":
        currency_price_unit = currency_price_unit.lower()

    df = load_data(currency_price_unit)

    ## Sidebar - Cryptocurrency selections
    sorted_coin = sorted(df["Symbol"])
    selected_coin = st.sidebar.multiselect(
        "Cryptocurrencies:", sorted_coin, ("BTC", "ETH", "LTC", "BCH")
    )

    df_selected_coin = df[(df["Symbol"].isin(selected_coin))]  # Filtering data

    ## Sidebar - Percent change timeframe
    percent_timeframe = st.sidebar.selectbox("Time resolution:", ["7d", "24h", "1h"])

    if percent_timeframe == "7d":
        df_change = df_selected_coin.sort_values(by=["7 days change (%)"])
    elif percent_timeframe == "24h":
        df_change = df_selected_coin.sort_values(by=["24 hours change (%)"])
    else:
        df_change = df_selected_coin.sort_values(by=["1 hour change (%)"])

    st.dataframe(
        df_change[["Name", "Symbol", "Price"]], height=df_selected_coin.shape[0] * 100
    )

    df_change["positive_percent_change_1h"] = df_change["1 hour change (%)"] > 0
    df_change["positive_percent_change_24h"] = df_change["24 hours change (%)"] > 0
    df_change["positive_percent_change_7d"] = df_change["7 days change (%)"] > 0

    periods = {"1h": "hour", "24h": "24 hours", "7d": "7 days"}
    orders = {
        "1h": "positive_percent_change_1h",
        "24h": "positive_percent_change_24h",
        "7d": "positive_percent_change_7d",
    }
    st.subheader(f"📈 Price change in the last {periods[percent_timeframe]}")

    plot_settings = {
        "color": df_change[orders[percent_timeframe]].map({True: "g", False: "r"}),
        "xlabel": "",
        "legend": False,
    }

    plt.figure(figsize=(5, 1))
    if percent_timeframe == "7d":
        df_change.plot(y="7 days change (%)", x="Symbol", kind="bar", **plot_settings)
    elif percent_timeframe == "24h":
        df_change.plot(y="24 hours change (%)", x="Symbol", kind="bar", **plot_settings)
    else:
        df_change.plot(y="1 hour change (%)", x="Symbol", kind="bar", **plot_settings)
    plt.ylabel("Change (%)", fontweight="bold")
    st.pyplot(plt)

    st.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)
