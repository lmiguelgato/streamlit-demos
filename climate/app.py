import base64
import math
import ssl
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ssl._create_default_https_context = ssl._create_unverified_context


def filedownload(df, data_type):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = '<a href="data:file/csv;base64,{b64}" '
    href += f'download="Climate_{data_type}_{datetime.now().strftime("%Y-%m-%d")}.csv">'
    href += "📥 Download data as CSV File</a>"
    return href


@st.cache
def load_co2_data():
    # Web scraping of climate data

    # Globally averaged atmospheric CO2 on marine surface - annual mean data:
    url_co2_annmean_gl = (
        "https://www.esrl.noaa.gov/gmd/webdata/ccgg/trends/co2/co2_annmean_gl.txt"
    )

    co2_annmean_gl = pd.read_csv(
        url_co2_annmean_gl,
        delim_whitespace=True,
        skiprows=57,
        usecols=[0, 1],
        names=["year", "co2"],
    )
    return co2_annmean_gl


@st.cache
def load_sea_level_data():
    # Global mean sea level:
    url_sea_levels = "https://sealevel.colorado.edu/files/2020_rel1:%20Global%20Mean%20Sea%20Level%20"
    url_sea_levels += (
        "(Seasonal%20Signals%20Retained)/gmsl_2020rel1_seasons_retained.txt"
    )

    sea_level_gl = pd.read_csv(
        url_sea_levels, delim_whitespace=True, skiprows=1, names=["year", "mm"]
    )

    sea_level_gl["year"] = sea_level_gl.apply(lambda x: math.floor(x["year"]), axis=1)

    mean_sea_level_gl = sea_level_gl.groupby("year", as_index=False).mean()

    return mean_sea_level_gl


@st.cache
def load_ocean_temp_data():
    # Global land-ocean temperature change in 0.01 degrees Celsius with respect to Jan 1950:
    url_ocean_temp_gl = (
        "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.txt"
    )

    ocean_temp_gl = pd.read_csv(
        url_ocean_temp_gl,
        delim_whitespace=True,
        skiprows=list(range(8))
        + [29, 30, 51, 52, 73, 74, 95, 96, 117, 118, 139, 140, 161, 162],
        skipfooter=8,
        usecols=[0, 13],
        engine="python",
        names=["year", "temp"],
    )

    ocean_temp_gl["temp"] = ocean_temp_gl.apply(lambda x: x["temp"] / 100, axis=1)

    return ocean_temp_gl


def climate_co2():
    df = load_co2_data()

    st.dataframe(
        df,
        height=df.shape[0] * 100,
    )

    plt.figure(figsize=(5, 1))
    df.plot.scatter(x="year", y="co2")
    plt.ylabel("CO2 concentration (ppm)")
    plt.xlabel("Year")
    plt.grid()
    st.pyplot(plt)

    st.markdown(filedownload(df, "CO2"), unsafe_allow_html=True)


def climate_sea_level():
    df = load_sea_level_data()

    st.dataframe(
        df,
        height=df.shape[0] * 100,
    )

    plt.figure(figsize=(5, 1))
    df.plot.scatter(x="year", y="mm")
    plt.ylabel("Relative sea level (mm)")
    plt.xlabel("Year")
    plt.grid()
    st.pyplot(plt)

    st.markdown(filedownload(df, "sea_level"), unsafe_allow_html=True)


def climate_ocean_temp():
    df = load_ocean_temp_data()

    st.dataframe(
        df,
        height=df.shape[0] * 100,
    )

    plt.figure(figsize=(5, 1))
    df.plot.scatter(x="year", y="temp")
    plt.ylabel("Relative temperature (°C)")
    plt.xlabel("Year")
    plt.grid()
    st.pyplot(plt)

    st.markdown(filedownload(df, "ocean_temp"), unsafe_allow_html=True)
