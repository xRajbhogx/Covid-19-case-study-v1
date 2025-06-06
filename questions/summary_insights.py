import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def get_date_columns(df):
    """Get date columns from dataframe"""
    return [col for col in df.columns if col not in ['Province/State', 'Country/Region', 'Lat', 'Long']]

def show_summary_insights_section(confirmed_df, deaths_df, recovered_df):
    st.header("📊 Executive Summary: Key COVID-19 Insights")
    st.markdown("""
    **🎯 This comprehensive overview presents the most critical findings from our detailed COVID-19 data analysis, 
    covering the period from January 2020 to May 2021.**
    """)
    
    # Global Statistics Overview
    st.subheader("🌍 Global Impact Summary")
    
    date_cols = get_date_columns(confirmed_df)
    latest_date = date_cols[-1]
    
    # Calculate global totals
    global_confirmed = confirmed_df[latest_date].sum()
    global_deaths = deaths_df[latest_date].sum()
    global_recovered = recovered_df[latest_date].sum()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Confirmed Cases", f"{global_confirmed:,.0f}", help="Cumulative confirmed cases globally")
    with col2:
        st.metric("Total Deaths", f"{global_deaths:,.0f}", help="Total deaths attributed to COVID-19")
    with col3:
        st.metric("Total Recovered", f"{global_recovered:,.0f}", help="Total recoveries from COVID-19")
    with col4:
        death_rate = (global_deaths / global_confirmed) * 100
        st.metric("Global Death Rate", f"{death_rate:.2f}%", help="Percentage of confirmed cases that resulted in death")
    
    # Key Findings Section
    st.subheader("🔍 Critical Findings")
    
    # Top 10 Most Affected Countries
    top_countries = confirmed_df.groupby('Country/Region')[latest_date].sum().sort_values(ascending=False).head(10)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🏆 Top 10 Most Affected Countries")
        
        # Create interactive bar chart
        fig = px.bar(
            x=top_countries.values,
            y=top_countries.index,
            orientation='h',
            title="Countries by Total Confirmed Cases",
            labels={'x': 'Confirmed Cases', 'y': 'Country'},
            color=top_countries.values,
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📋 Key Statistics")
        for i, (country, cases) in enumerate(top_countries.head(5).items(), 1):
            st.write(f"**{i}. {country}:** {cases:,.0f}")
        
        st.markdown("---")
        st.info(f"""
        **🎯 Top 3 Impact:**
        - **{top_countries.index[0]}** leads with {top_countries.iloc[0]:,.0f} cases
        - **{top_countries.index[1]}** follows with {top_countries.iloc[1]:,.0f} cases
        - **{top_countries.index[2]}** third with {top_countries.iloc[2]:,.0f} cases
        """)
    
    # Death Rate Analysis
    st.subheader("💀 Death Rate Analysis")
    
    # Calculate death rates for countries with >10,000 cases
    country_confirmed = confirmed_df.groupby('Country/Region')[latest_date].sum()
    country_deaths = deaths_df.groupby('Country/Region')[latest_date].sum()
    
    # Filter countries with significant cases
    significant_countries = country_confirmed[country_confirmed >= 10000]
    death_rates = (country_deaths[significant_countries.index] / significant_countries * 100).sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Highest Death Rates (>10K cases)")
        top_death_rates = death_rates.head(10)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(range(len(top_death_rates)), top_death_rates.values, color='darkred', alpha=0.7)
        ax.set_yticks(range(len(top_death_rates)))
        ax.set_yticklabels(top_death_rates.index)
        ax.set_xlabel('Death Rate (%)')
        ax.set_title('Countries with Highest Death Rates')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{width:.1f}%', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.markdown("#### 🟢 Best Recovery Performance")
        
        # Calculate recovery rates
        country_recovered = recovered_df.groupby('Country/Region')[latest_date].sum()
        recovery_rates = (country_recovered[significant_countries.index] / significant_countries * 100).sort_values(ascending=False)
        
        top_recovery = recovery_rates.head(10)
        
        for i, (country, rate) in enumerate(top_recovery.head(5).items(), 1):
            st.write(f"**{i}. {country}:** {rate:.1f}% recovery rate")
        
        st.success(f"""
        **🏥 Recovery Champions:**
        - **{top_recovery.index[0]}** leads with {top_recovery.iloc[0]:.1f}% recovery
        - Global average recovery: {(global_recovered/global_confirmed*100):.1f}%
        - Countries above 90% recovery: {len(recovery_rates[recovery_rates > 90])}
        """)
    
    # Timeline Analysis
    st.subheader("📈 Pandemic Timeline & Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚀 Global Growth Timeline")
        
        # Sample key dates for timeline
        key_dates = date_cols[::30]  # Every 30 days
        global_timeline = []
        
        for date in key_dates:
            total_cases = confirmed_df[date].sum()
            global_timeline.append({'Date': date, 'Cases': total_cases})
        
        timeline_df = pd.DataFrame(global_timeline)
        timeline_df['Date'] = pd.to_datetime(timeline_df['Date'])
        
        fig = px.line(timeline_df, x='Date', y='Cases', 
                     title='Global COVID-19 Case Growth Over Time',
                     labels={'Cases': 'Total Confirmed Cases'})
        fig.update_traces(line_color='red', line_width=3)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Peak Analysis by Region")
        
        # Analyze peak cases for major countries
        major_countries = ['US', 'India', 'Brazil', 'Russia', 'France']
        peak_data = []
        
        for country in major_countries:
            if country in confirmed_df['Country/Region'].values:
                country_data = confirmed_df[confirmed_df['Country/Region'] == country][date_cols].sum()
                daily_new = country_data.diff().fillna(0)
                peak_day = daily_new.idxmax()
                peak_value = daily_new.max()
                
                peak_data.append({
                    'Country': country,
                    'Peak Daily Cases': int(peak_value),
                    'Peak Date': peak_day
                })
        
        peak_df = pd.DataFrame(peak_data).sort_values('Peak Daily Cases', ascending=False)
        
        for _, row in peak_df.iterrows():
            st.write(f"**{row['Country']}:** {row['Peak Daily Cases']:,} cases on {row['Peak Date']}")
    
    # Regional Comparison
    st.subheader("🌏 Regional Impact Comparison")
    
    # Define regions (simplified)
    regions = {
        'North America': ['US', 'Canada', 'Mexico'],
        'Europe': ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom'],
        'Asia': ['China', 'India', 'Japan', 'Korea, South', 'Iran'],
        'South America': ['Brazil', 'Argentina', 'Chile', 'Peru', 'Colombia']
    }
    
    regional_data = []
    for region, countries in regions.items():
        region_confirmed = 0
        region_deaths = 0
        region_recovered = 0
        
        for country in countries:
            if country in confirmed_df['Country/Region'].values:
                region_confirmed += confirmed_df[confirmed_df['Country/Region'] == country][latest_date].sum()
                region_deaths += deaths_df[deaths_df['Country/Region'] == country][latest_date].sum()
                region_recovered += recovered_df[recovered_df['Country/Region'] == country][latest_date].sum()
        
        if region_confirmed > 0:
            regional_data.append({
                'Region': region,
                'Confirmed': region_confirmed,
                'Deaths': region_deaths,
                'Recovered': region_recovered,
                'Death Rate (%)': (region_deaths / region_confirmed * 100),
                'Recovery Rate (%)': (region_recovered / region_confirmed * 100)
            })
    
    regional_df = pd.DataFrame(regional_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Regional cases comparison
        fig = px.bar(regional_df, x='Region', y='Confirmed', 
                    title='Total Cases by Region',
                    color='Confirmed',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Regional death rates
        fig = px.bar(regional_df, x='Region', y='Death Rate (%)', 
                    title='Death Rates by Region',
                    color='Death Rate (%)',
                    color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    # Key Insights Summary
    st.subheader("💡 Strategic Insights & Conclusions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Impact Insights")
        st.info(f"""
        **Most Affected:**
        • {top_countries.index[0]} leads globally
        • {len(country_confirmed[country_confirmed > 100000])} countries >100K cases
        • {len(country_confirmed[country_confirmed > 1000000])} countries >1M cases
        
        **Timeline:**
        • Pandemic peak periods varied by region
        • Multiple waves observed globally
        • Recovery rates improved over time
        """)
    
    with col2:
        st.markdown("#### 📊 Performance Metrics")
        best_recovery_country = recovery_rates.index[0]
        worst_death_country = death_rates.index[0]
        
        st.success(f"""
        **Best Performers:**
        • Highest recovery: {best_recovery_country} ({recovery_rates.iloc[0]:.1f}%)
        • Lowest death rates in major countries show effective healthcare
        
        **Challenges:**
        • Highest death rate: {worst_death_country} ({death_rates.iloc[0]:.1f}%)
        • Healthcare system stress indicators
        • Resource allocation patterns
        """)
    
    with col3:
        st.markdown("#### 🔮 Data Quality & Coverage")
        st.warning(f"""
        **Dataset Coverage:**
        • {confirmed_df['Country/Region'].nunique()} countries/regions
        • {len(date_cols)} days of data
        • Period: Jan 2020 - May 2021
        
        **Data Completeness:**
        • Confirmed cases: Most complete
        • Recovery data: Some limitations
        • Death reporting: Generally reliable
        """)
    
    # Final Summary Box
    st.markdown("---")
    st.subheader("📋 Executive Summary")
    
    summary_text = f"""
    **🌍 Global Impact:** The COVID-19 pandemic affected {confirmed_df['Country/Region'].nunique()} countries with {global_confirmed:,.0f} confirmed cases, 
    resulting in {global_deaths:,.0f} deaths and {global_recovered:,.0f} recoveries by May 2021.
    
    **🏆 Most Affected:** {top_countries.index[0]} led with {top_countries.iloc[0]:,.0f} cases, followed by {top_countries.index[1]} 
    and {top_countries.index[2]}.
    
    **💀 Mortality Patterns:** Global death rate of {death_rate:.2f}%, with significant variation by country ranging from 
    <1% to >{death_rates.iloc[0]:.1f}% in worst-affected regions.
    
    **🏥 Recovery Success:** Countries like {recovery_rates.index[0]} achieved {recovery_rates.iloc[0]:.1f}% recovery rates, 
    demonstrating effective healthcare responses.
    
    **📈 Timeline Insights:** The pandemic showed multiple waves globally, with peak daily cases varying significantly 
    by region and healthcare capacity.
    """
    
    st.success(summary_text)
    
    # Action Items / Recommendations
    st.subheader("🎯 Key Takeaways for Future Preparedness")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Success Factors")
        st.write("""
        • **Early intervention** in countries with lower death rates
        • **Healthcare capacity** correlation with better outcomes
        • **Data transparency** enabling better response coordination
        • **Recovery protocols** improving over time
        • **Regional cooperation** showing positive impacts
        """)
    
    with col2:
        st.markdown("#### ⚠️ Risk Factors")
        st.write("""
        • **Population density** affecting transmission rates
        • **Healthcare infrastructure** limiting treatment capacity  
        • **Delayed response** correlating with higher death rates
        • **Data gaps** hindering effective policy making
        • **Economic constraints** affecting pandemic response
        """)
    
    # Footer
    st.markdown("---")
    st.info("""
    **📊 Analysis Period:** January 22, 2020 - May 29, 2021 | 
    **🔍 Data Source:** COVID-19 Time Series Data | 
    **👨‍💻 Analyst:** Pushkar Shukla | 
    **🤖 Enhanced with AI Analytics**
    """)