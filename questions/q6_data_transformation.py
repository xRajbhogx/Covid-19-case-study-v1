import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_date_columns(df):
    meta_cols = {"Province/State", "Country/Region", "Lat", "Long"}
    return [col for col in df.columns if col not in meta_cols]

def transform_to_long_format(df, value_column):
    """Transform dataset from wide to long format"""
    date_columns = get_date_columns(df)
    
    long_df = df.melt(
        id_vars=["Province/State", "Country/Region", "Lat", "Long"],
        value_vars=date_columns,
        var_name="Date",
        value_name=value_column
    )
    
    # Convert Date column to datetime format
    long_df["Date"] = pd.to_datetime(long_df["Date"])
    
    return long_df

def show_data_transformation_section(confirmed_df, deaths_df, recovered_df):
    st.header("🔄 Question 6: Data Transformation")
    
    # Q6.1: Transform deaths dataset from wide to long format (Enhanced)
    st.subheader("Q6.1: Wide to Long Format Transformation")
    st.markdown("**Transform the 'deaths' dataset from wide format to long format with datetime dates**")
    
    # Better explanation of wide vs long format
    st.markdown("""
    **Wide Format:** Each date is a separate column, making the dataset very wide.
    **Long Format:** Each date becomes a row, creating a normalized structure ideal for analysis.
    """)
    
    # Show original format sample with better presentation
    st.write("**🔍 Original Wide Format Structure:**")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"""
        **Current Structure:**
        - Rows: {deaths_df.shape[0]}
        - Columns: {deaths_df.shape[1]}
        - Date columns: {len(get_date_columns(deaths_df))}
        """)
    
    with col2:
        sample_wide = deaths_df.head(3)[["Province/State", "Country/Region"] + get_date_columns(deaths_df)[:5]]
        st.dataframe(sample_wide)
    
    # Enhanced transformation code explanation
    with st.expander("📋 View Detailed Transformation Process"):
        st.markdown("**Step-by-step transformation process:**")
        st.code("""
# Step 1: Identify date columns (exclude metadata columns)
date_columns = [col for col in deaths_df.columns 
                if col not in ["Province/State", "Country/Region", "Lat", "Long"]]

# Step 2: Transform from wide to long format using melt()
deaths_long = deaths_df.melt(
    id_vars=["Province/State", "Country/Region", "Lat", "Long"],  # Keep these as identifiers
    value_vars=date_columns,  # These columns become rows
    var_name="Date",          # Column header becomes 'Date' column
    value_name="Deaths"       # Values become 'Deaths' column
)

# Step 3: Convert Date column to proper datetime format
deaths_long["Date"] = pd.to_datetime(deaths_long["Date"])

# Result: Each row now represents one location on one specific date
        """, language="python")
    
    # Apply transformation
    deaths_long = transform_to_long_format(deaths_df, "Deaths")
    
    st.write("**🎯 Transformed Long Format Structure:**")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.success(f"""
        **New Structure:**
        - Rows: {deaths_long.shape[0]:,}
        - Columns: {deaths_long.shape[1]}
        - Date format: datetime64
        """)
    
    with col2:
        # Show sample with properly formatted data
        sample_long = deaths_long.head(8)
        sample_long_display = sample_long.copy()
        sample_long_display['Date'] = sample_long_display['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(sample_long_display)
    
    # Show data type verification
    st.write("**✅ Data Type Verification:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"Date column type: `{deaths_long['Date'].dtype}`")
    with col2:
        st.write(f"Date range: {deaths_long['Date'].min().strftime('%Y-%m-%d')} to {deaths_long['Date'].max().strftime('%Y-%m-%d')}")
    with col3:
        st.write(f"Total records: {len(deaths_long):,}")
    
    st.success(f"✅ Successfully transformed to long format with {deaths_long.shape[0]:,} rows")
    
    # Q6.2: Total deaths per country (Enhanced with dropdown)
    st.subheader("Q6.2: Total Deaths per Country")
    st.markdown("**Total number of deaths reported per country up to current date**")
    
    # Add dropdown to select number of countries
    num_countries = st.selectbox(
        "Select number of top countries to display:",
        options=[5, 10, 15, 20, 25, 30],
        index=2,  # Default to 15
        help="Choose how many top countries to show in the analysis"
    )
    
    # Get latest date and calculate total deaths per country
    latest_date = deaths_long["Date"].max()
    country_totals = deaths_long[deaths_long["Date"] == latest_date].groupby("Country/Region")["Deaths"].sum().sort_values(ascending=False)
    
    st.write(f"**Total Deaths by Country (as of {latest_date.strftime('%Y-%m-%d')}):**")
    
    # Show selected number of countries
    top_countries_deaths = country_totals.head(num_countries)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, max(8, num_countries * 0.4)))
    
    bars = ax.barh(range(len(top_countries_deaths)), top_countries_deaths.values, color='darkred', alpha=0.7)
    ax.set_yticks(range(len(top_countries_deaths)))
    ax.set_yticklabels(top_countries_deaths.index)
    ax.set_xlabel('Total Deaths', fontsize=12)
    ax.set_title(f'Top {num_countries} Countries by Total COVID-19 Deaths', fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, top_countries_deaths.values)):
        ax.text(bar.get_width() + max(top_countries_deaths.values) * 0.01, bar.get_y() + bar.get_height()/2, 
               f'{int(value):,}', ha='left', va='center', fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_axisbelow(True)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Show summary table
    st.dataframe(top_countries_deaths.reset_index().rename(columns={'Country/Region': 'Country', 'Deaths': 'Total Deaths'}))
    
    # Q6.3: Top 5 countries with highest average daily deaths
    st.subheader("Q6.3: Highest Average Daily Deaths")
    st.markdown("**Top 5 countries with the highest average daily deaths**")
    
    # Calculate daily deaths for each country
    country_daily_deaths = []
    
    for country in deaths_long["Country/Region"].unique():
        country_data = deaths_long[deaths_long["Country/Region"] == country]
        country_totals = country_data.groupby("Date")["Deaths"].sum().sort_index()
        
        # Calculate daily new deaths
        daily_new_deaths = country_totals.diff().fillna(0)
        avg_daily_deaths = daily_new_deaths.mean()
        
        if avg_daily_deaths > 0:  # Only include countries with deaths
            country_daily_deaths.append({
                'Country': country,
                'Average Daily Deaths': round(avg_daily_deaths, 2)
            })
    
    # Sort and get top 5
    daily_deaths_df = pd.DataFrame(country_daily_deaths)
    top_5_daily = daily_deaths_df.sort_values('Average Daily Deaths', ascending=False).head(5)
    
    st.dataframe(top_5_daily, use_container_width=True)
    
    # Create bar chart for top 5
    fig, ax = plt.subplots(figsize=(10, 6))
    
    countries = top_5_daily['Country']
    avg_deaths = top_5_daily['Average Daily Deaths']
    
    bars = ax.bar(countries, avg_deaths, color='crimson', alpha=0.7)
    ax.set_title('Top 5 Countries by Average Daily Deaths', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylabel('Average Daily Deaths', fontsize=12)
    ax.set_xlabel('Country', fontsize=12)
    
    # Add value labels on bars
    for bar, value in zip(bars, avg_deaths):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_deaths) * 0.01, 
               f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Q6.4: Deaths evolution in United States (Only Cumulative)
    st.subheader("Q6.4: Deaths Evolution in United States")
    st.markdown("**How total deaths evolved over time in the United States**")
    
    # Filter data for United States
    us_data = deaths_long[deaths_long["Country/Region"] == "US"]
    
    if not us_data.empty:
        # Calculate total deaths by date for US
        us_daily_totals = us_data.groupby("Date")["Deaths"].sum().sort_index()
        
        # Create single plot for cumulative deaths only
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot cumulative deaths
        ax.plot(us_daily_totals.index, us_daily_totals.values, color='darkred', linewidth=3)
        ax.fill_between(us_daily_totals.index, us_daily_totals.values, alpha=0.3, color='darkred')
        ax.set_title('United States - Cumulative COVID-19 Deaths Over Time', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Cumulative Deaths', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Add some key milestone annotations
        total_deaths = us_daily_totals.iloc[-1]
        first_100k = us_daily_totals[us_daily_totals >= 100000]
        if len(first_100k) > 0:
            date_100k = first_100k.index[0]
            ax.axvline(x=date_100k, color='orange', linestyle='--', alpha=0.7)
            ax.annotate('100,000 deaths', xy=(date_100k, 100000), xytext=(10, 20), 
                       textcoords='offset points', fontsize=10, 
                       bbox=dict(boxstyle='round,pad=0.3', fc='orange', alpha=0.7))
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Show key statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Deaths", f"{us_daily_totals.iloc[-1]:,.0f}")
        
        with col2:
            first_death_date = us_daily_totals[us_daily_totals > 0].index[0]
            st.metric("First Death Date", first_death_date.strftime("%Y-%m-%d"))
        
        with col3:
            latest_date_us = us_daily_totals.index[-1]
            st.metric("Latest Data Date", latest_date_us.strftime("%Y-%m-%d"))
        
        # Timeline analysis
        st.write("**📅 Key Milestones:**")
        milestones = [
            ("First Death", us_daily_totals[us_daily_totals > 0].index[0], us_daily_totals[us_daily_totals > 0].iloc[0]),
            ("10,000 Deaths", us_daily_totals[us_daily_totals >= 10000].index[0] if len(us_daily_totals[us_daily_totals >= 10000]) > 0 else None, 10000),
            ("100,000 Deaths", us_daily_totals[us_daily_totals >= 100000].index[0] if len(us_daily_totals[us_daily_totals >= 100000]) > 0 else None, 100000)
        ]
        
        for milestone, date, deaths in milestones:
            if date is not None:
                st.write(f"• **{milestone}**: {date.strftime('%Y-%m-%d')} ({deaths:,} total deaths)")
    
    else:
        st.warning("No data found for United States")
    
    # Summary
    st.subheader("📊 Transformation Summary")
    st.success("""
    ✅ **Data Transformation Completed:
    - Successfully transformed deaths dataset from wide to long format
    - Converted date columns to proper datetime format
    - Calculated total deaths per country with flexible display options
    - Identified top countries by average daily deaths
    - Analyzed cumulative death evolution in the United States
    """)
