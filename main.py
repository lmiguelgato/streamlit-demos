from collections import OrderedDict

import streamlit as st

from climate.app import climate_co2, climate_ocean_temp, climate_sea_level
from crypto.app import crypto
from stocks.app import sp500, ticker_stock


def intro():
    st.markdown(
        """
        **👈 Select a demo from the dropdown on the left** to see some
        data-driven applications I have developed using Streamlit.

        [Streamlit](https://streamlit.io) is an open-source app framework built specifically for
        Machine Learning and Data Science projects.

        ###  Take a look to [my GitHub repo](https://github.com/lmiguelgato/streamlit-demos) for more details.
        """
    )


DEMOS = OrderedDict(
    [
        (
            "👇",
            (
                intro,
                None,
            ),
        ),
        (
            "Closing stock price and volume",
            (
                ticker_stock,
                """
                Historic closing stock prices and volumes for certain ticker symbol.
                """,
            ),
        ),
        (
            "S&P 500 stock market index",
            (
                sp500,
                """
                The [S&P 500](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) stock market index,
                maintained by S&P Dow Jones Indices, comprises 505 common stocks issued by 500 large-cap companies
                and traded on American stock exchanges (including the 30 companies that compose the Dow Jones
                Industrial Average), and covers about 80 percent of the American equity market by capitalization.
                """,
            ),
        ),
        (
            "Cryptocurrency prices",
            (
                crypto,
                """
                Today's cryptocurrency prices according to [CoinMarketCap](https://coinmarketcap.com/).
                """,
            ),
        ),
        (
            "Climate: CO2 concentration",
            (
                climate_co2,
                """
                Globally averaged atmospheric CO2 on marine surface according to the [NOAA](https://www.noaa.gov/).
                """,
            ),
        ),
        (
            "Climate: Sea level",
            (
                climate_sea_level,
                """
                Relative global sea level increase according to the [University of Colorado](https://www.cu.edu/).
                """,
            ),
        ),
        (
            "Climate: Ocean temperature",
            (
                climate_ocean_temp,
                """
                Global land-ocean temperature change in 0.01 degrees Celsius with respect to Jan 1950 according to the [NASA](https://www.nasa.gov/).
                """,
            ),
        ),
    ]
)


demo_name = st.sidebar.selectbox("Choose a demo:", list(DEMOS.keys()), 0)
demo = DEMOS[demo_name][0]

if demo_name == "👇":
    st.write("# Welcome 👋")
    st.write("I am Luis M Gato, *Data & Applied Scientist* at Microsoft.")
else:
    st.markdown("# %s" % demo_name)
    description = DEMOS[demo_name][1]
    if description:
        st.write(description)
    # Clear everything from the intro page.
    # We only have 4 elements in the page so this is intentional overkill.
    for i in range(10):
        st.empty()

demo()
