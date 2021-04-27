import streamlit as st

from collections import OrderedDict
from stock_prices.app import ticker_stock


def intro():
    import streamlit as st

    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        Streamlit is an open-source app framework built specifically for
        Machine Learning and Data Science projects.

        **👈 Select a demo from the dropdown on the left** to see some examples
        of what Streamlit can do!

        ### Want to learn more?

        - Check out [streamlit.io](https://streamlit.io)
        - Jump into our [documentation](https://docs.streamlit.io)
        - Ask a question in our [community
          forums](https://discuss.streamlit.io)

        ### See more complex demos

        - Use a neural net to [analyze the Udacity Self-driving Car Image
          Dataset] (https://github.com/streamlit/demo-self-driving)
        - Explore a [New York City rideshare dataset]
          (https://github.com/streamlit/demo-uber-nyc-pickups)
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
