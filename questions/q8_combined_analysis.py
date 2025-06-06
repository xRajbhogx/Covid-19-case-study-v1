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

def show_combined_analysis_section(confirmed_df, deaths_df, recovered_df):
    st.header("📊 Question 8: Combined Data Analysis")
    
    # Create merged dataset
    st.write("**Creating Combined Dataset...**")
    
    # Transform all datasets to long format
    confirmed_long = transform_to_long_format(confirmed_df, "Confirmed")
    deaths_long = transform_to_long_format(deaths_df, "Deaths")
    recovered_long = transform_to_long_format(recovered_df, "Recovered")
    
    # Merge datasets
    merged_df = pd.merge(confirmed_long, deaths_long, 
                        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], 
                        how='inner')
    merged_df = pd.merge(merged_df, recovered_long, 
                        on=['Province/State', 'Country/Region', 'Lat', 'Long', 'Date'], 
                        how='inner')
    
    st.success(f"✅ Combined dataset created: {merged_df.shape[0]:,} rows")
    
    # Q8.1: Countries with highest average death rates in 2020
    st.subheader("Q8.1: Highest Average Death Rates in 2020")
    st.markdown("**Identify the three countries with the highest average death rates (deaths/confirmed cases) throughout 2020**")
    
    # Filter data for 2020
    merged_2020 = merged_df[merged_df['Date'].dt.year == 2020]
    
    # Calculate death rates by country for each date in 2020
    country_death_rates = []
    
    for country in merged_2020['Country/Region'].unique():
        country_data = merged_2020[merged_2020['Country/Region'] == country]
        
        # Get monthly data to avoid daily fluctuations
        monthly_data = country_data.groupby(country_data['Date'].dt.to_period('M')).agg({
            'Confirmed': 'max',
            'Deaths': 'max'
        }).reset_index()
        
        # Calculate death rates for each month
        monthly_data['Death_Rate'] = (monthly_data['Deaths'] / monthly_data['Confirmed'] * 100).fillna(0)
        
        # Only include countries with significant case numbers
        if monthly_data['Confirmed'].max() >= 1000:
            avg_death_rate = monthly_data['Death_Rate'].mean()
            
            country_death_rates.append({
                'Country': country,
                'Average Death Rate (%)': round(avg_death_rate, 2),
                'Total Confirmed (2020)': int(monthly_data['Confirmed'].max()),
                'Total Deaths (2020)': int(monthly_data['Deaths'].max())
            })
    
    # Sort and get top 3
    death_rates_df = pd.DataFrame(country_death_rates)
    top_3_death_rates = death_rates_df.sort_values('Average Death Rate (%)', ascending=False).head(3)
    
    st.write("**Top 3 Countries with Highest Average Death Rates in 2020:**")
    st.dataframe(top_3_death_rates)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    countries = top_3_death_rates['Country']
    death_rates = top_3_death_rates['Average Death Rate (%)']
    
    bars = ax.bar(countries, death_rates, color=['darkred', 'red', 'crimson'], alpha=0.7)
    ax.set_title('Top 3 Countries by Average Death Rate in 2020', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Death Rate (%)', fontsize=12)
    ax.set_xlabel('Country', fontsize=12)
    
    # Add value labels on bars
    for bar, rate in zip(bars, death_rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
               f'{rate}%', ha='center', va='bottom', fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    st.pyplot(fig)
    
    # Analysis
    st.write("**📋 Analysis:**")
    top_country = top_3_death_rates.iloc[0]
    st.write(f"""
    • **{top_country['Country']}** had the highest average death rate at **{top_country['Average Death Rate (%)']}%**
    • This indicates potential challenges in healthcare capacity, treatment protocols, or demographic factors
    • High death rates could suggest overwhelmed healthcare systems or vulnerable populations
    • Early pandemic period may have lacked effective treatment protocols
    """)
    
    # Q8.2: South Africa recoveries vs deaths comparison
    st.subheader("Q8.2: South Africa - Recoveries vs Deaths")
    st.markdown("**Compare total recoveries to total deaths in South Africa**")
    
    # Filter data for South Africa
    sa_data = merged_df[merged_df['Country/Region'] == 'South Africa']
    
    if not sa_data.empty:
        # Get latest data
        latest_sa = sa_data[sa_data['Date'] == sa_data['Date'].max()]
        total_confirmed = latest_sa['Confirmed'].sum()
        total_deaths = latest_sa['Deaths'].sum()
        total_recovered = latest_sa['Recovered'].sum()
        
        # Calculate ratios
        recovery_rate = (total_recovered / total_confirmed * 100) if total_confirmed > 0 else 0
        death_rate = (total_deaths / total_confirmed * 100) if total_confirmed > 0 else 0
        
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Confirmed", f"{total_confirmed:,}")
        with col2:
            st.metric("Total Recoveries", f"{total_recovered:,}")
        with col3:
            st.metric("Total Deaths", f"{total_deaths:,}")
        
        # Create comparison chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Chart 1: Recoveries vs Deaths comparison
        categories = ['Recoveries', 'Deaths']
        values = [total_recovered, total_deaths]
        colors = ['green', 'red']
        
        bars = ax1.bar(categories, values, color=colors, alpha=0.7)
        ax1.set_title('South Africa: Recoveries vs Deaths', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Number of Cases', fontsize=12)
        
        # Add value labels
        for bar, value in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01, 
                    f'{value:,}', ha='center', va='bottom', fontweight='bold')
        
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Chart 2: Recovery and Death Rates
        rates = [recovery_rate, death_rate]
        rate_labels = [f'Recovery Rate\n{recovery_rate:.1f}%', f'Death Rate\n{death_rate:.1f}%']
        
        bars2 = ax2.bar(rate_labels, rates, color=colors, alpha=0.7)
        ax2.set_title('South Africa: Recovery vs Death Rates', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Percentage (%)', fontsize=12)
        
        # Add value labels
        for bar, rate in zip(bars2, rates):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(rates)*0.01, 
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Analysis
        st.write("**📋 Analysis:**")
        recovery_to_death_ratio = total_recovered / total_deaths if total_deaths > 0 else 0
        st.write(f"""
        • **Recovery to Death Ratio:** {recovery_to_death_ratio:.1f}:1 (For every death, {recovery_to_death_ratio:.1f} people recovered)
        • **Recovery Rate:** {recovery_rate:.1f}% of confirmed cases recovered
        • **Death Rate:** {death_rate:.1f}% of confirmed cases died
        • South Africa shows {"good" if recovery_rate > 80 else "moderate" if recovery_rate > 60 else "concerning"} recovery outcomes
        • This suggests {"effective" if recovery_rate > 80 else "adequate" if recovery_rate > 60 else "challenged"} healthcare management
        """)
    
    else:
        st.warning("No data found for South Africa")
    
    # Q8.3: US monthly recovery ratio analysis
    st.subheader("Q8.3: US Monthly Recovery Ratios (March 2020 - May 2021)")
    st.markdown("**Analyze recovery to confirmed cases ratio for United States monthly**")
    
    # Filter data for US
    us_data = merged_df[merged_df['Country/Region'] == 'US']
    
    if not us_data.empty:
        # Filter for March 2020 to May 2021
        start_date = pd.to_datetime('2020-03-01')
        end_date = pd.to_datetime('2021-05-31')
        us_period = us_data[(us_data['Date'] >= start_date) & (us_data['Date'] <= end_date)]
        
        # Group by month
        us_period['Month_Year'] = us_period['Date'].dt.to_period('M')
        monthly_us = us_period.groupby('Month_Year').agg({
            'Confirmed': 'max',
            'Recovered': 'max'
        }).reset_index()
        
        # Calculate recovery ratio
        monthly_us['Recovery_Ratio'] = (monthly_us['Recovered'] / monthly_us['Confirmed'] * 100).fillna(0)
        
        # Create line chart
        fig, ax = plt.subplots(figsize=(14, 6))
        
        months = monthly_us['Month_Year'].astype(str)
        recovery_ratios = monthly_us['Recovery_Ratio']
        
        ax.plot(months, recovery_ratios, marker='o', linewidth=3, markersize=8, color='blue')
        ax.fill_between(months, recovery_ratios, alpha=0.3, color='blue')
        
        ax.set_title('US Monthly Recovery Ratios (March 2020 - May 2021)', fontsize=14, fontweight='bold', horizontalalignment='right')
        ax.set_ylabel('Recovery Ratio (%)', fontsize=12)
        ax.set_xlabel('Month-Year', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Highlight highest point
        max_ratio_idx = recovery_ratios.idxmax()
        max_ratio = recovery_ratios.iloc[max_ratio_idx]
        max_month = months.iloc[max_ratio_idx]
        
        ax.scatter(max_month, max_ratio, color='red', s=100, zorder=5)
        ax.annotate(f'Highest: {max_ratio:.1f}%\n{max_month}', 
                   xy=(max_ratio_idx, max_ratio), 
                   xytext=(10, 20), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Show summary table
        st.write("**📊 Monthly Recovery Ratios Summary:**")
        summary_table = monthly_us[['Month_Year', 'Confirmed', 'Recovered', 'Recovery_Ratio']].copy()
        summary_table['Month_Year'] = summary_table['Month_Year'].astype(str)
        summary_table['Confirmed'] = summary_table['Confirmed'].apply(lambda x: f"{x:,}")
        summary_table['Recovered'] = summary_table['Recovered'].apply(lambda x: f"{x:,}")
        summary_table['Recovery_Ratio'] = summary_table['Recovery_Ratio'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(summary_table)
        
        # Analysis
        st.write("**📋 Analysis:**")
        highest_month = monthly_us.loc[monthly_us['Recovery_Ratio'].idxmax()]
        st.write(f"""
        • **Highest Recovery Ratio:** {highest_month['Recovery_Ratio']:.1f}% in {highest_month['Month_Year']}
        • **Potential Reasons for Peak Recovery:**
          - Improved treatment protocols and medical knowledge
          - Better healthcare capacity and resource allocation
          - Vaccine rollout effects (if applicable to timeframe)
          - Seasonal factors affecting recovery rates
          - Enhanced testing and case management systems
        """)
        
        # Show trend analysis
        early_avg = monthly_us.head(3)['Recovery_Ratio'].mean()
        late_avg = monthly_us.tail(3)['Recovery_Ratio'].mean()
        trend = "improving" if late_avg > early_avg else "declining"
        
        st.write(f"""
        • **Trend Analysis:** Recovery ratios show a **{trend}** trend over the period
        • **Early Period Average (first 3 months):** {early_avg:.1f}%
        • **Late Period Average (last 3 months):** {late_avg:.1f}%
        """)
    
    else:
        st.warning("No data found for United States")
    
    # Summary
    st.subheader("📊 Combined Analysis Summary")
    st.success("""
    ✅ **Combined Data Analysis Completed:**
    - Identified countries with highest death rates in 2020
    - Compared recovery outcomes in South Africa
    - Analyzed US recovery ratio trends over time
    - Generated insights on pandemic impact and healthcare effectiveness
    """)
