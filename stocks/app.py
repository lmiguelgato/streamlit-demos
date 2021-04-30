import base64
from datetime import date, datetime, timedelta

import backtrader as bt
import cufflinks as cf
import pandas as pd
import streamlit as st
import yfinance as yf


class MyBuySell(bt.observers.BuySell):
    plotlines = dict(
        buy=dict(marker="^", markersize=8.0, color="blue", fillstyle="full"),
        sell=dict(marker="v", markersize=8.0, color="red", fillstyle="full"),
    )


class SmaStrategy(bt.Strategy):
    params = (("ma_period", 20),)

    def __init__(self):
        self.strat_data = {
            "buy": list(),
            "sell": list(),
        }

        # keep track of close price in the series
        self.data_close = self.datas[0].close

        # keep track of pending orders/buy price/buy commission
        self.order = None
        self.price = None
        self.comm = None

        # add a simple moving average indicator
        self.sma = bt.ind.SMA(self.datas[0], period=self.params.ma_period)

    def log(self, txt):
        """Logging function"""
        dt = self.datas[0].datetime.date(0).isoformat()
        st.write(f"{dt} --> {txt}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order already submitted/accepted - no action required
            return

        # report executed order
        if order.status in [order.Completed]:
            if order.isbuy():
                self.strat_data["buy"].append(
                    {
                        "time": self.datas[0].datetime.date(0).isoformat(),
                        "price": order.executed.price,
                        "cost": order.executed.value,
                        "commission": order.executed.comm,
                    }
                )
                self.log(
                    f"BUY executed at Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}"
                )
                self.price = order.executed.price
                self.comm = order.executed.comm
            else:
                self.strat_data["sell"].append(
                    {
                        "time": self.datas[0].datetime.date(0).isoformat(),
                        "price": order.executed.price,
                        "cost": order.executed.value,
                        "commission": order.executed.comm,
                    }
                )
                self.log(
                    f"SELL executed at Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}"
                )

        # report failed order
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Failed")

        # set no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(
            f"OPERATION RESULT --- Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}"
        )

    def next(self):
        # do nothing if an order is pending
        if self.order:
            return

        # check if there is already a position
        if not self.position:
            # buy condition
            if self.data_close[0] > self.sma[0]:
                self.log(f"BUY created at Price: {self.data_close[0]:.2f}")
                self.order = self.buy()
        else:
            # sell condition
            if self.data_close[0] < self.sma[0]:
                self.log(f"SELL created at Price: {self.data_close[0]:.2f}")
                self.order = self.sell()


class SmaSignal(bt.Signal):
    params = (("period", 20),)

    def __init__(self):
        self.lines.signal = self.data - bt.ind.SMA(period=self.p.period)


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

    status = {"message": "", "auth": False}
    if st.sidebar.button("Login"):
        if pwd == st.secrets["PASSWORD"]:
            status["auth"] = True
            status["message"] = "Welcome back 👋"
        else:
            status["auth"] = False
            status["message"] = "Wrong password!"

        st.sidebar.write(status["message"])

    if status["auth"]:
        st.sidebar.write("You are logged in.")
        st.write("Launching trading bot with SMA strategy ...")

        data = bt.feeds.PandasData(dataname=tickerDf)

        # create a Cerebro entity
        cerebro = bt.Cerebro(stdstats=False)

        # set up the backtest
        cerebro.adddata(data)
        cerebro.broker.setcash(1000.0)
        cerebro.addstrategy(SmaStrategy)
        cerebro.addobserver(MyBuySell)
        cerebro.addobserver(bt.observers.Value)

        # run backtest
        st.markdown(
            f"### Starting Portfolio Value: {cerebro.broker.getvalue():.2f} USD"
        )
        cerebro.run()
        st.markdown(f"### Final Portfolio Value: {cerebro.broker.getvalue():.2f} USD")

    elif status["message"]:
        st.sidebar.write("Please, authenticate to start trading.")


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
