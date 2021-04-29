import base64
from datetime import date, datetime, timedelta

import cufflinks as cf
import pandas as pd
import streamlit as st
import yfinance as yf


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
        "Select start time:", date.today() - timedelta(days=365)
    )
    date_end = st.sidebar.date_input("Select end time:", date.today())
    n_days = (date_end - date_start).days

    st.sidebar.text(f"Records from a {n_days}-days period.")

    tickerData = yf.Ticker(tickerSymbol)

    tickerDf = tickerData.history(start=date_start, end=date_end)

    qf = cf.QuantFig(
        tickerDf,
        title=f"Stock price for {tickerSymbol}",
        legend="top",
        name=tickerSymbol,
    )
    qf.add_volume()
    qf.add_sma(periods=20, color="red")
    qf.add_ema(periods=20, color="green")

    st.plotly_chart(qf.iplot(asFigure=True), use_container_width=True)

    st.markdown(filedownload(tickerDf), unsafe_allow_html=True)


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
