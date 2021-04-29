import base64
import os
from datetime import date, datetime, timedelta

import cufflinks as cf
import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache
def get_password():
    return os.environ.get("LOGNAME", "?")


def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" '
    href += f'download="SP500_{datetime.now().strftime("%Y-%m-%d")}.csv">📥 Download data as CSV File</a>'
    return href


def ticker_stock():
    tickerSymbol = st.sidebar.text_input(
        "Ticker symbol (e.g. GOOGL, AAPL, MSFT, ...):", "MSFT"
    ).upper()

    date_start = st.sidebar.date_input(
        "Select start time:", date.today() - timedelta(days=30 * 3)
    )
    date_end = st.sidebar.date_input("Select end time:", date.today())
    n_days = (date_end - date_start).days

    st.sidebar.text(f"Records from a {n_days}-days period.")

    ema = st.sidebar.slider("Exponential moving-average (EMA):", 1, 30, 7)
    sma = st.sidebar.slider("Simple moving-average (SMA):", 1, 30, 15)

    tickerData = yf.Ticker(tickerSymbol)

    tickerDf = tickerData.history(start=date_start, end=date_end)

    qf = cf.QuantFig(
        tickerDf, name=tickerSymbol, up_color="#00BB00", down_color="#EE0000"
    )
    qf.add_volume()
    qf.add_sma(periods=sma, color="red")
    qf.add_ema(periods=ema, color="green")

    st.plotly_chart(qf.iplot(asFigure=True), use_container_width=True)

    st.markdown(filedownload(tickerDf), unsafe_allow_html=True)

    pwd = st.sidebar.text_input(
        "Authenticate to launch the trading bot:", max_chars=50, type="password"
    )
    status = ""
    if st.sidebar.button("Login"):
        if pwd == get_password():
            status = "Authenticated! Launch the trading bot when you're ready."
        else:
            status = f"Wrong password! Try again."
    st.sidebar.write(status)


@st.cache
def load_data():
    # Web scraping of S&P 500 data
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header=0)
    df = html[0]
    return df


def sp500():
    df = load_data()

    sorted_sector_unique = sorted(df["GICS Sector"].unique())
    selected_sector = st.sidebar.multiselect(
        "Industry sector:", sorted_sector_unique, []
    )

    df_selected_sector = df[(df["GICS Sector"].isin(selected_sector))]

    sorted_sub_sector_unique = sorted(df_selected_sector["GICS Sub-Industry"].unique())
    selected_sub_sector = st.sidebar.multiselect(
        "Sub-sector:", sorted_sub_sector_unique, sorted_sub_sector_unique
    )

    df_selected_sub_sector = df_selected_sector[
        (df_selected_sector["GICS Sub-Industry"].isin(selected_sub_sector))
    ]

    st.write(
        f"Found {df_selected_sub_sector.shape[0]} companies in the selected sectors."
    )
    df_selected_sub_sector.pop("SEC filings")
    df_selected_sub_sector.pop("CIK")
    df_selected_sub_sector.rename(
        columns={
            "Security": "Name",
            "Date first added": "Date added",
            "GICS Sector": "Sector",
            "GICS Sub-Industry": "Sub-Sector",
        },
        inplace=True,
    )
    st.dataframe(df_selected_sub_sector, height=df_selected_sub_sector.shape[0] * 50)
    st.markdown(filedownload(df_selected_sub_sector), unsafe_allow_html=True)
