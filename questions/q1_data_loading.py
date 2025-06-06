import streamlit as st
import pandas as pd

def get_standard_column_map(df):
    col_map = {}
    for col in df.columns:
        col_lower = col.lower().replace("_", "").replace(" ", "")
        if "province" in col_lower or "state" in col_lower:
            col_map[col] = "Province/State"
        elif "country" in col_lower or "region" in col_lower:
            col_map[col] = "Country/Region"
        elif col_lower in ["lat", "latitude"]:
            col_map[col] = "Lat"
        elif col_lower in ["long", "longitude"]:
            col_map[col] = "Long"
    return col_map

def standardize_dataframe_columns(df):
    return df.rename(columns=get_standard_column_map(df))

#Filling missing or blank values in the Province/State column with "All Provinces"
def clean_province_column(df):
    if "Province/State" in df.columns:
        df["Province/State"] = df["Province/State"].fillna("All Provinces")
        df["Province/State"].replace("", "All Provinces", inplace=True)
    return df

@st.cache_data
def load_and_prepare_datasets():
    try:
        confirmed = pd.read_csv('covid_19_confirmed_v1.csv')
        deaths = pd.read_csv('covid_19_deaths_v1.csv')
        recovered = pd.read_csv('covid_19_recovered_v1.csv')
        confirmed = standardize_dataframe_columns(confirmed)
        deaths = standardize_dataframe_columns(deaths)
        recovered = standardize_dataframe_columns(recovered)
        confirmed = clean_province_column(confirmed)
        deaths = clean_province_column(deaths)
        recovered = clean_province_column(recovered)
        return confirmed, deaths, recovered
    except Exception as e:
        st.error(f"Dataset file not found or error: {e}")
        return None, None, None

# Q1: Data Loading Section
def show_data_loading_section():
    confirmed_df, deaths_df, recovered_df = load_and_prepare_datasets()
    
    if confirmed_df is None or deaths_df is None or recovered_df is None:
        st.stop()
    
    st.header("📥 Question 1: Data Loading")
    st.markdown("**Q1.1:** Load the COVID-19 datasets for confirmed cases, deaths, and recoveries into Python using Pandas.")
    
    with st.expander("📋 View Code"):
        st.code("""
import pandas as pd
confirmed_df = pd.read_csv('covid_19_confirmed_v1.csv')
deaths_df = pd.read_csv('covid_19_deaths_v1.csv')
recovered_df = pd.read_csv('covid_19_recovered_v1.csv')
        """, language="python")
    
    tab1, tab2, tab3 = st.tabs(["✅ Confirmed Cases", "💀 Deaths", "💚 Recovered"])
    for df, tab, name in zip([confirmed_df, deaths_df, recovered_df], [tab1, tab2, tab3], ["Confirmed", "Deaths", "Recovered"]):
        with tab:
            st.subheader(f"{name} Dataset")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                st.metric("Countries", df["Country/Region"].nunique())
            st.dataframe(df.head(), use_container_width=True)
