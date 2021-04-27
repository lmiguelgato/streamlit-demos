from collections import OrderedDict

import streamlit as st

from stock_prices.app import ticker_stock, sp500


def intro():
    import streamlit as st

    st.markdown(
        """
        **👈 Select a demo from the dropdown on the left** to see some
        data-driven apps I have developed using Streamlit.

        [Streamlit](https://streamlit.io) is an open-source app framework built specifically for
        Machine Learning and Data Science projects.

        ###  Take a look to [my GitHub repo](https://github.com/lmiguelgato/streamlit-demos) for more details.
    """
    )


DEMOS = OrderedDict(
    [
        ("—", (intro, None)),
        (
            "Closing stock price and volume",
            (
                ticker_stock,
                """
                History of closing stock prices and volumes for certain ticker symbol.
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
    ]
)


demo_name = st.sidebar.selectbox("Choose a demo:", list(DEMOS.keys()), 0)
demo = DEMOS[demo_name][0]

if demo_name == "—":
    st.write("# Welcome 👋")
    st.write("I am Luis M. Gato, *Data & Applied Scientist* at Microsoft.")
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
