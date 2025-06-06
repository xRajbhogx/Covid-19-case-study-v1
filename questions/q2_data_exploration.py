import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_date_columns(df):
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

def show_data_exploration_section(confirmed_df, deaths_df, recovered_df):
    st.header("🔍 Question 2: Data Exploration")
    
    # Q2.1: Structure of datasets
    st.markdown("**Q2.1:** Structure of each dataset (rows, columns, data types)")
    
    col1, col2, col3 = st.columns(3)
    datasets = [confirmed_df, deaths_df, recovered_df]
    names = ["Confirmed", "Deaths", "Recovered"]
    
    for df, col, name in zip(datasets, [col1, col2, col3], names):
        with col:
            st.subheader(f"{name} Dataset")
            st.write(f"Rows: {df.shape[0]}")
            st.write(f"Columns: {df.shape[1]}")
            st.write(f"Countries: {df['Country/Region'].nunique()}")
    
    # Q2.2: Top countries plot
    st.markdown("**Q2.2:** Plots of confirmed cases over time for top countries")
    
    # Simple dropdown for number of countries
    num_countries = st.selectbox("Select number of top countries:", [5, 10, 15, 20], index=0)
    
    # Get top countries by latest confirmed cases
    date_cols = get_date_columns(confirmed_df)
    latest_date = date_cols[-1]
    top_countries = confirmed_df.groupby('Country/Region')[latest_date].sum().sort_values(ascending=False).head(num_countries)
    
    # Convert to long format
    confirmed_long = convert_to_long_format(confirmed_df, "Confirmed")
    top_data = confirmed_long[confirmed_long['Country/Region'].isin(top_countries.index)]
    
    # Create matplotlib plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for country in top_countries.index:
        country_data = top_data[top_data['Country/Region'] == country]
        country_daily = country_data.groupby('Date')['Confirmed'].sum()
        ax.plot(country_daily.index, country_daily.values, label=country, linewidth=2)
    
    ax.set_title(f'COVID-19 Confirmed Cases - Top {num_countries} Countries', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Confirmed Cases', fontsize=12)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # Show top countries list
    st.write(f"**Top {num_countries} Countries:**")
    for i, (country, cases) in enumerate(top_countries.items(), 1):
        st.write(f"{i}. {country}: {cases:,}")
    
    # Q2.3: China plot
    st.markdown("**Q2.3:** Plots of confirmed cases over time for China")
    
    # Filter data for China
    china_data = confirmed_long[confirmed_long['Country/Region'] == 'China']
    
    if not china_data.empty:
        china_daily = china_data.groupby('Date')['Confirmed'].sum()
        
        # Create simple matplotlib plot for China
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(china_daily.index, china_daily.values, color='red', linewidth=3, label='China')
        ax.fill_between(china_daily.index, china_daily.values, alpha=0.3, color='red')
        
        ax.set_title('COVID-19 Confirmed Cases - China', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Confirmed Cases', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Show China statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cases", f"{china_daily.iloc[-1]:,}")
        with col2:
            first_date = china_daily[china_daily > 0].index[0]
            st.metric("First Case Date", first_date.strftime("%Y-%m-%d"))
            
    else:
        st.warning("No data found for China in the dataset.")