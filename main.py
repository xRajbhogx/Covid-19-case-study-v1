import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import question modules
from questions.q1_data_loading import show_data_loading_section
from questions.q2_data_exploration import show_data_exploration_section
from questions.q3_handling_missing_data import show_handling_missing_data_section
from questions.q4_data_cleaning import show_data_cleaning_section
from questions.q5_independent_analysis import show_independent_analysis_section
from questions.q6_data_transformation import show_data_transformation_section
from questions.q7_data_merging import show_data_merging_section
from questions.q8_combined_analysis import show_combined_analysis_section
from questions.q9_ai_insights import show_ai_insights_section
from questions.summary_insights import show_summary_insights_section  # Add this import

st.set_page_config(
    page_title="COVID-19 Data Analysis",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🦠 COVID-19 Data Analysis Dashboard")
st.divider()

st.sidebar.title("📊 Navigation")
question_list = [
    "🏠 Overview",
    "📊 Executive Summary",  # Add this new page
    "🤖 AI Data Assistant",
    "📥 Q1: Data Loading",
    "🔍 Q2: Data Exploration", 
    "🧹 Q3: Handling Missing Data",
    "✨ Q4: Data Cleaning and Preparation",
    "📈 Q5: Independent Dataset Analysis",
    "🔄 Q6: Data Transformation",
    "🔗 Q7: Data Merging",
    "📊 Q8: Combined Data Analysis"
]
selected_question = st.sidebar.selectbox("Select Analysis Section:", question_list)

# --- Helper functions for robust column handling ---
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

def get_date_columns(df):
    # Date columns are those not in the metadata columns
    meta_cols = {"Province/State", "Country/Region", "Lat", "Long"}
    return [col for col in df.columns if col not in meta_cols]

def convert_to_long_format(df, value_column):
    date_columns = get_date_columns(df)
    long_df = df.melt(
        id_vars=["Province/State", "Country/Region", "Lat", "Long"],
        value_vars=date_columns,
        var_name="Date",
        value_name=value_column
    )
    long_df["Date"] = pd.to_datetime(long_df["Date"])
    return long_df

def clean_province_column(df):
    # Replace missing or blank province/state with "All Provinces"
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
        # Standardize columns
        confirmed = standardize_dataframe_columns(confirmed)
        deaths = standardize_dataframe_columns(deaths)
        recovered = standardize_dataframe_columns(recovered)
        # Clean province/state
        confirmed = clean_province_column(confirmed)
        deaths = clean_province_column(deaths)
        recovered = clean_province_column(recovered)
        return confirmed, deaths, recovered
    except Exception as e:
        st.error(f"Dataset file not found or error: {e}")
        return None, None, None

confirmed_df, deaths_df, recovered_df = load_and_prepare_datasets()

if confirmed_df is None or deaths_df is None or recovered_df is None:
    st.stop()

# Check for required columns
required_columns = ["Province/State", "Country/Region", "Lat", "Long"]
for df, name in zip([confirmed_df, deaths_df, recovered_df], ["Confirmed", "Deaths", "Recovered"]):
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Column '{col}' missing in {name} dataset. Columns found: {list(df.columns)}")
            st.stop()

# Use these standard names everywhere in your code:
country_col = "Country/Region"
province_col = "Province/State"
lat_col = "Lat"
long_col = "Long"

# --- Streamlit Sections ---

if selected_question == "🏠 Overview":
    st.header("📋 Project Overview")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🎯 Background")
        st.markdown("""
        The COVID-19 pandemic, caused by the SARS-CoV-2 virus, emerged in late 2019 and rapidly spread globally, 
        leading to significant health, economic, and social impacts. This unprecedented health crisis highlighted 
        the crucial role of data analysis in managing such pandemics. By meticulously tracking and analyzing data 
        on confirmed cases, recoveries, and deaths, policymakers and health professionals can make informed 
        decisions to control the spread of the virus and allocate resources effectively.
        """)
        
        st.subheader("🚀 Special Features")
        st.success("""
        **🤖 AI Data Assistant:** This project includes an interactive AI assistant that can answer 
        any questions about the COVID-19 data in real-time. Ask about trends, comparisons, statistics, 
        or any insights you're curious about!
        """)
        
        st.subheader("📊 Dataset Details")
        st.markdown("""
        This case study utilizes three key datasets, each providing daily updates on different aspects of the pandemic:
        - **Confirmed Cases Dataset:** Cumulative confirmed COVID-19 cases (Jan 22, 2020 - May 29, 2021)
        - **Deaths Dataset:** Cumulative deaths attributed to COVID-19
        - **Recovered Cases Dataset:** Cumulative recoveries from COVID-19
        
        Each dataset includes Province/State, Country/Region, coordinates (Lat, Long), and daily cumulative totals.
        """)
        
        # Add AI Assistance Disclaimer
        st.subheader("🤖 AI Assistance Acknowledgment")
        st.info("""
        **Important Note:** This project was developed with significant assistance from AI tools and technologies. 
        While the analysis, insights, and learning outcomes are genuine, substantial help was taken from AI for:
        
        - Code optimization and debugging
        - Data visualization enhancement
        - Documentation and commenting
        - Problem-solving approaches
        - Best practices implementation
        
        This project represents a collaborative effort between human learning and AI assistance, 
        demonstrating modern data science development practices.
        """)
        
    with col2:
        st.subheader("📈 Dataset Summary")
        st.metric("Confirmed Dataset", f"{confirmed_df.shape[0]} rows", f"{confirmed_df.shape[1]} columns")
        st.metric("Deaths Dataset", f"{deaths_df.shape[0]} rows", f"{deaths_df.shape[1]} columns")
        st.metric("Recovered Dataset", f"{recovered_df.shape[0]} rows", f"{recovered_df.shape[1]} columns")
        
        # Add feature highlight
        st.markdown("### 🌟 Key Features")
        st.success("🤖 **AI Assistant**\nInteractive data insights")
        st.info("📊 **8 Analysis Questions**\nComprehensive data exploration")
        st.warning("📈 **Visual Analytics**\nInteractive charts & graphs")
        
        st.info("**Analysis by Pushkar Shukla**")
        st.warning("⚠️ **AI-Assisted Project**")

elif selected_question == "📊 Executive Summary":
    # Call the summary insights function
    show_summary_insights_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "🤖 AI Data Assistant":
    # Call the AI insights function
    show_ai_insights_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "📥 Q1: Data Loading":
    # Call the modular function from questions folder
    show_data_loading_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "🔍 Q2: Data Exploration":
    # Call the modular function from questions folder
    show_data_exploration_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "🧹 Q3: Handling Missing Data":
    # Call the modular function from questions folder
    confirmed_clean, deaths_clean, recovered_clean = show_handling_missing_data_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "✨ Q4: Data Cleaning and Preparation":
    # Call the modular function from questions folder
    confirmed_clean, deaths_clean, recovered_clean = show_data_cleaning_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "📈 Q5: Independent Dataset Analysis":
    # Call the modular function from questions folder
    show_independent_analysis_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "🔄 Q6: Data Transformation":
    # Call the modular function from questions folder
    show_data_transformation_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "🔗 Q7: Data Merging":
    # Call the modular function from questions folder
    show_data_merging_section(confirmed_df, deaths_df, recovered_df)

elif selected_question == "📊 Q8: Combined Data Analysis":
    # Call the modular function from questions folder
    show_combined_analysis_section(confirmed_df, deaths_df, recovered_df)

st.markdown("---")
st.markdown("**Analysis completed using Python, Pandas, Plotly, and Streamlit**")
st.markdown("*Data Source: COVID-19 Time Series Data*")
