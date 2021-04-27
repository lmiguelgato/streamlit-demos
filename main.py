from collections import OrderedDict

import streamlit as st

from stock_prices.app import ticker_stock


def intro():
    import streamlit as st

    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        [Streamlit](https://streamlit.io) is an open-source app framework built specifically for
        Machine Learning and Data Science projects.

        **👈 Select a demo from the dropdown on the left** to see some
        data-driven apps I have developed using Streamlit.
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
    ]
)


demo_name = st.sidebar.selectbox("Choose a demo", list(DEMOS.keys()), 0)
demo = DEMOS[demo_name][0]

if demo_name == "—":
    st.write("# Welcome to Streamlit! 👋")
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
