def ticker_stock():
    import datetime

    import streamlit as st
    import yfinance as yf

    tickerSymbol = st.sidebar.text_input(
        "Ticker symbol (e.g. GOOGL, AAPL, MSFT, ...):", "MSFT"
    ).upper()

    date_start = st.sidebar.date_input(
        "Select start time:", datetime.date.today() - datetime.timedelta(days=365 * 10)
    )
    date_end = st.sidebar.date_input("Select end time:", datetime.date.today())
    n_days = (date_end - date_start).days

    st.sidebar.text(f"Records from a {n_days}-days period.")

    possible_intervals = ["1d", "1wk", "1mo"]

    interval = st.sidebar.select_slider("Time resolution:", options=possible_intervals)

    tickerData = yf.Ticker(tickerSymbol)

    tickerDf = tickerData.history(start=date_start, end=date_end, interval=interval)

    st.line_chart(tickerDf.Close)

    st.line_chart(tickerDf.Volume)
