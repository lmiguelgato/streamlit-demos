import base64
import json
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

periods = {
    "1 hour": "hour",
    "24 hours": "24 hours",
    "7 days": "7 days",
}
orders = {
    "1 hour": "positive_percent_change_1h",
    "24 hours": "positive_percent_change_24h",
    "7 days": "positive_percent_change_7d",
}
y_axis_plot = {
    "1 hour": "1 hour change (%)",
    "24 hours": "24 hours change (%)",
    "7 days": "7 days change (%)",
}


def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Crypto_'
    href += f'{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv">📥 Download data as CSV File</a>'
    return href


@st.cache
def load_data(currency_price_unit):
    # Web scraping of cryptos data
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
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for i in listings:
        coin_name.append(i["slug"])
        coin_symbol.append(i["symbol"])
        market_cap.append(i["quote"][currency_price_unit]["marketCap"])
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
            "Market cap.",
        ]
    )
    df["Name"] = coin_name
    df["Symbol"] = coin_symbol
    df["Price"] = price
    df["1 hour change (%)"] = percent_change_1h
    df["24 hours change (%)"] = percent_change_24h
    df["7 days change (%)"] = percent_change_7d
    df["24-hour volume"] = volume_24h
    df["Market cap."] = market_cap

    return df


def crypto():
    currency_price_unit = st.sidebar.selectbox(
        "Currency in which price is displayed:", ("USD", "BTC", "ETH")
    )
    if currency_price_unit != "USD":
        currency_price_unit = currency_price_unit.lower()

    df = load_data(currency_price_unit)

    sorted_coin = sorted(df["Symbol"])
    selected_coin = st.sidebar.multiselect(
        "Choose which cryptos to analyze:",
        sorted_coin,
        df.sort_values(by="Market cap.", ascending=False)["Symbol"][:10],
    )

    df_selected_coin = df[(df["Symbol"].isin(selected_coin))]

    time_resolution = st.sidebar.selectbox(
        "Time resolution:", ["7 days", "24 hours", "1 hour"]
    )

    df_change = df_selected_coin.sort_values(by=y_axis_plot[time_resolution])

    st.dataframe(
        df_selected_coin[["Name", "Symbol", "Price"]],
        height=df_selected_coin.shape[0] * 100,
    )

    df_change["positive_percent_change_1h"] = df_change["1 hour change (%)"] > 0
    df_change["positive_percent_change_24h"] = df_change["24 hours change (%)"] > 0
    df_change["positive_percent_change_7d"] = df_change["7 days change (%)"] > 0

    st.subheader(f"📈 Price change in the past {periods[time_resolution]}")

    plot_settings = {
        "color": df_change[orders[time_resolution]].map({True: "g", False: "r"}),
        "xlabel": "",
        "legend": False,
    }

    plt.figure(figsize=(5, 1))
    df_change.plot(
        y=y_axis_plot[time_resolution], x="Symbol", kind="bar", **plot_settings
    )
    plt.ylabel("Change (%)", fontweight="bold")
    st.pyplot(plt)

    st.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)
