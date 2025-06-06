import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

def show_data_merging_section(confirmed_df, deaths_df, recovered_df):
    st.header("🔗 Question 7: Data Merging")
    
    # Q7.1: Merge the transformed datasets
    st.subheader("Q7.1: Merging Transformed Datasets")
    st.markdown("**Merge confirmed cases, deaths, and recoveries datasets on 'Country/Region' and 'Date' columns**")
    
    # Transform all datasets to long format
    st.write("**Step 1: Transform all datasets to long format**")
    
    confirmed_long = transform_to_long_format(confirmed_df, "Confirmed")
    deaths_long = transform_to_long_format(deaths_df, "Deaths")
    recovered_long = transform_to_long_format(recovered_df, "Recovered")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Confirmed Long:** {confirmed_long.shape[0]:,} rows")
    with col2:
        st.write(f"**Deaths Long:** {deaths_long.shape[0]:,} rows")
    with col3:
        st.write(f"**Recovered Long:** {recovered_long.shape[0]:,} rows")
    
    # Show merging process
    st.write("**Step 2: Merge datasets on Country/Region and Date**")
    
    with st.expander("📋 View Merging Code"):
        st.code("""
# Step 1: Transform datasets to long format
confirmed_long = transform_to_long_format(confirmed_df, "Confirmed")
deaths_long = transform_to_long_format(deaths_df, "Deaths")
recovered_long = transform_to_long_format(recovered_df, "Recovered")

# Step 2: Merge datasets step by step
# First merge confirmed and deaths
merged_df = pd.merge(
    confirmed_long, 
    deaths_long, 
    on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], 
    how='inner'
)

# Then merge with recovered
merged_df = pd.merge(
    merged_df, 
    recovered_long, 
    on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], 
    how='inner'
)
        """, language="python")
    
    # Perform the merge
    # First merge confirmed and deaths
    merged_df = pd.merge(
        confirmed_long, 
        deaths_long, 
        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], 
        how='inner'
    )
    
    # Then merge with recovered
    merged_df = pd.merge(
        merged_df, 
        recovered_long, 
        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], 
        how='inner'
    )
    
    st.success(f"✅ Successfully merged datasets: {merged_df.shape[0]:,} rows × {merged_df.shape[1]} columns")
    
    # Show sample of merged data
    st.write("**📊 Sample of Merged Dataset:**")
    sample_merged = merged_df.head(10)
    sample_display = sample_merged.copy()
    sample_display['Date'] = sample_display['Date'].dt.strftime('%Y-%m-%d')
    st.dataframe(sample_display)
    
    # Show data summary
    st.write("**📈 Merged Dataset Summary:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{merged_df.shape[0]:,}")
    with col2:
        st.metric("Countries", merged_df['Country/Region'].nunique())
    with col3:
        st.metric("Date Range", f"{(merged_df['Date'].max() - merged_df['Date'].min()).days} days")
    with col4:
        st.metric("Columns", merged_df.shape[1])
    
    # Q7.2: Monthly analysis for countries [SIMPLIFIED VERSION]
    st.subheader("Q7.2: Monthly Sum Analysis - Countries")
    st.markdown("**Analyze the monthly sum of confirmed cases, deaths, and recoveries for countries**")
    
    # Add dropdown for number of countries
    num_countries = st.selectbox(
        "Select number of top countries to display:",
        options=[5, 10, 15, 20, 25, 30],
        index=1,  # Default to 10
        help="Choose how many top countries to show in the monthly analysis"
    )
    
    # Add month-year column
    merged_df['Month_Year'] = merged_df['Date'].dt.to_period('M')
    
    # Calculate monthly sums by country
    monthly_country = merged_df.groupby(['Country/Region', 'Month_Year']).agg({
        'Confirmed': 'max',  # Use max since data is cumulative
        'Deaths': 'max',
        'Recovered': 'max'
    }).reset_index()
    
    # Get top countries by total confirmed cases
    latest_month = monthly_country['Month_Year'].max()
    top_countries_list = monthly_country[monthly_country['Month_Year'] == latest_month].nlargest(num_countries, 'Confirmed')['Country/Region'].tolist()
    
    # Filter data for selected countries
    monthly_top = monthly_country[monthly_country['Country/Region'].isin(top_countries_list)]
    
    # Create simple line plots
    fig, axes = plt.subplots(3, 1, figsize=(12, 12))
    
    # Plot 1: Monthly Confirmed Cases
    for country in top_countries_list[:5]:  # Show only top 5 for clarity
        country_data = monthly_top[monthly_top['Country/Region'] == country]
        if not country_data.empty:
            axes[0].plot(country_data['Month_Year'].astype(str), country_data['Confirmed'], 
                        marker='o', linewidth=2, label=country)
    
    axes[0].set_title('Monthly Confirmed Cases (Cumulative)', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Confirmed Cases', fontsize=12)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)
    
    # Plot 2: Monthly Deaths
    for country in top_countries_list[:5]:
        country_data = monthly_top[monthly_top['Country/Region'] == country]
        if not country_data.empty:
            axes[1].plot(country_data['Month_Year'].astype(str), country_data['Deaths'], 
                        marker='s', linewidth=2, label=country)
    
    axes[1].set_title('Monthly Deaths (Cumulative)', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Deaths', fontsize=12)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].tick_params(axis='x', rotation=45)
    
    # Plot 3: Monthly Recoveries
    for country in top_countries_list[:5]:
        country_data = monthly_top[monthly_top['Country/Region'] == country]
        if not country_data.empty:
            axes[2].plot(country_data['Month_Year'].astype(str), country_data['Recovered'], 
                        marker='^', linewidth=2, label=country)
    
    axes[2].set_title('Monthly Recoveries (Cumulative)', fontsize=14, fontweight='bold')
    axes[2].set_ylabel('Recoveries', fontsize=12)
    axes[2].set_xlabel('Month-Year', fontsize=12)
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Show summary table
    st.write(f"**📊 Monthly Summary for Top {num_countries} Countries (Latest Data):**")
    latest_data_summary = monthly_top[monthly_top['Month_Year'] == latest_month][['Country/Region', 'Confirmed', 'Deaths', 'Recovered']].sort_values('Confirmed', ascending=False)
    st.dataframe(latest_data_summary)
    
    # Q7.3: Specific analysis for US, Italy, and Brazil [SIMPLIFIED VERSION]
    st.subheader("Q7.3: Monthly Analysis - US, Italy, and Brazil")
    st.markdown("**Redo the analysis in Question 7.2 for the United States, Italy, and Brazil**")
    
    focus_countries = ['US', 'Italy', 'Brazil']
    focus_monthly = monthly_country[monthly_country['Country/Region'].isin(focus_countries)]
    
    # Create simple 3-panel plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 12))
    
    # Plot 1: Confirmed Cases for US, Italy, Brazil
    for country in focus_countries:
        country_data = focus_monthly[focus_monthly['Country/Region'] == country]
        if not country_data.empty:
            axes[0].plot(country_data['Month_Year'].astype(str), country_data['Confirmed'], 
                        marker='o', linewidth=3, label=country)
    
    axes[0].set_title('Monthly Confirmed Cases - US, Italy, Brazil', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Confirmed Cases', fontsize=12)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)
    
    # Plot 2: Deaths for US, Italy, Brazil
    for country in focus_countries:
        country_data = focus_monthly[focus_monthly['Country/Region'] == country]
        if not country_data.empty:
            axes[1].plot(country_data['Month_Year'].astype(str), country_data['Deaths'], 
                        marker='s', linewidth=3, label=country)
    
    axes[1].set_title('Monthly Deaths - US, Italy, Brazil', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Deaths', fontsize=12)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].tick_params(axis='x', rotation=45)
    
    # Plot 3: Recoveries for US, Italy, Brazil
    for country in focus_countries:
        country_data = focus_monthly[focus_monthly['Country/Region'] == country]
        if not country_data.empty:
            axes[2].plot(country_data['Month_Year'].astype(str), country_data['Recovered'], 
                        marker='^', linewidth=3, label=country)
    
    axes[2].set_title('Monthly Recoveries - US, Italy, Brazil', fontsize=14, fontweight='bold')
    axes[2].set_ylabel('Recoveries', fontsize=12)
    axes[2].set_xlabel('Month-Year', fontsize=12)
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Show statistics table for US, Italy, Brazil
    st.write("**📊 Statistics for US, Italy, Brazil (Latest Data):**")
    
    final_stats = []
    latest_month = focus_monthly['Month_Year'].max()
    
    for country in focus_countries:
        country_latest = focus_monthly[
            (focus_monthly['Country/Region'] == country) & 
            (focus_monthly['Month_Year'] == latest_month)
        ]
        
        if not country_latest.empty:
            row = country_latest.iloc[0]
            final_stats.append({
                'Country': country,
                'Total Confirmed': f"{row['Confirmed']:,}",
                'Total Deaths': f"{row['Deaths']:,}",
                'Total Recovered': f"{row['Recovered']:,}"
            })
    
    stats_df = pd.DataFrame(final_stats)
    st.dataframe(stats_df, use_container_width=True)
    
    # Key insights
    st.write("**🔍 Key Insights:**")
    
    # Find highest totals among the three countries
    latest_data = focus_monthly[focus_monthly['Month_Year'] == latest_month]
    
    highest_confirmed = latest_data.loc[latest_data['Confirmed'].idxmax()]
    highest_deaths = latest_data.loc[latest_data['Deaths'].idxmax()]
    highest_recovered = latest_data.loc[latest_data['Recovered'].idxmax()]
    
    st.write(f"• **Highest confirmed cases:** {highest_confirmed['Country/Region']} with {highest_confirmed['Confirmed']:,} cases")
    st.write(f"• **Highest deaths:** {highest_deaths['Country/Region']} with {highest_deaths['Deaths']:,} deaths")
    st.write(f"• **Highest recoveries:** {highest_recovered['Country/Region']} with {highest_recovered['Recovered']:,} recoveries")
    
    # Summary
    st.subheader("📊 Data Merging Summary")
    st.success("""
    ✅ **Data Merging Completed:
    - Successfully merged confirmed, deaths, and recovered datasets
    - Analyzed monthly progression of pandemic for top countries
    - Compared US, Italy, and Brazil across all three metrics
    - Generated clear insights on pandemic patterns
    """)
