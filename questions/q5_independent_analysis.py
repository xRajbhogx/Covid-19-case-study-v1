import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def get_date_columns(df):
    meta_cols = {"Province/State", "Country/Region", "Lat", "Long"}
    return [col for col in df.columns if col not in meta_cols]

def show_independent_analysis_section(confirmed_df, deaths_df, recovered_df):
    st.header("📈 Question 5: Independent Dataset Analysis")
    
    # Q5.1: Peak daily new cases in Germany, France, and Italy
    st.subheader("Q5.1: Peak Daily New Cases Analysis")
    st.markdown("**Analyze the peak number of daily new cases in Germany, France, and Italy**")
    
    countries_to_analyze = ['Germany', 'France', 'Italy']
    date_cols = get_date_columns(confirmed_df)
    
    # Calculate daily new cases for each country
    peak_data = []
    
    # Create individual plots for each country in rows
    for i, country in enumerate(countries_to_analyze):
        # Get country data
        country_data = confirmed_df[confirmed_df['Country/Region'] == country]
        
        if not country_data.empty:
            # Sum all provinces/states for the country
            country_totals = country_data[date_cols].sum()
            
            # Calculate daily new cases
            daily_new = country_totals.diff().fillna(0)
            
            # Find peak day
            peak_day = daily_new.idxmax()
            peak_value = daily_new.max()
            
            peak_data.append({
                'Country': country,
                'Peak Daily Cases': int(peak_value),
                'Peak Date': peak_day
            })
            
            # Create individual plot for each country
            fig, ax = plt.subplots(figsize=(12, 4))
            
            # Convert dates to numeric for plotting
            dates = pd.to_datetime(daily_new.index)
            ax.plot(dates, daily_new.values, linewidth=2.5, 
                   color=['#1f77b4', '#ff7f0e', '#2ca02c'][i], alpha=0.8)
            
            # Fill area under curve
            ax.fill_between(dates, daily_new.values, alpha=0.3, 
                          color=['#1f77b4', '#ff7f0e', '#2ca02c'][i])
            
            # Mark the peak point
            peak_date_dt = pd.to_datetime(peak_day)
            ax.scatter(peak_date_dt, peak_value, color='red', s=100, zorder=5)
            ax.annotate(f'Peak: {int(peak_value):,} cases\n{peak_day}', 
                       xy=(peak_date_dt, peak_value), 
                       xytext=(20, 20), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            ax.set_title(f'{country} - Daily New COVID-19 Cases', fontsize=16, fontweight='bold', pad=20,horizontalalignment='right')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Daily New Cases', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
    
    # Show peak data summary table
    st.markdown("### 📊 Peak Cases Summary")
    peak_df = pd.DataFrame(peak_data)
    peak_df = peak_df.sort_values('Peak Daily Cases', ascending=False)
    
    st.dataframe(peak_df, use_container_width=True)
    
    # Highlight the highest with better formatting
    highest_country = peak_df.iloc[0]
    st.success(f"🏆 **{highest_country['Country']}** experienced the highest single-day surge of **{highest_country['Peak Daily Cases']:,}** cases on **{highest_country['Peak Date']}**")
    
    # Q5.2: Recovery rates comparison between Canada and Australia
    st.subheader("Q5.2: Recovery Rates Comparison")
    st.markdown("**Compare recovery rates between Canada and Australia as of December 31, 2020**")
    
    target_date = '12/31/20'
    countries_recovery = ['Canada', 'Australia']
    
    if target_date in date_cols:
        recovery_comparison = []
        
        for country in countries_recovery:
            # Get confirmed cases
            confirmed_country = confirmed_df[confirmed_df['Country/Region'] == country]
            total_confirmed = confirmed_country[target_date].sum()
            
            # Get recovered cases
            recovered_country = recovered_df[recovered_df['Country/Region'] == country]
            total_recovered = recovered_country[target_date].sum()
            
            # Calculate recovery rate
            recovery_rate = (total_recovered / total_confirmed) * 100 if total_confirmed > 0 else 0
            
            recovery_comparison.append({
                'Country': country,
                'Confirmed Cases': int(total_confirmed),
                'Recovered Cases': int(total_recovered),
                'Recovery Rate (%)': round(recovery_rate, 2)
            })
        
        recovery_df = pd.DataFrame(recovery_comparison)
        st.dataframe(recovery_df, use_container_width=True)
        
        # Create enhanced bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        countries = recovery_df['Country']
        rates = recovery_df['Recovery Rate (%)']
        
        bars = ax.bar(countries, rates, color=['#FF6B6B', '#4ECDC4'], alpha=0.8, width=0.6)
        
        # Add pattern to bars for better distinction
        bars[0].set_hatch('///')
        bars[1].set_hatch('...')
        
        ax.set_title(f'COVID-19 Recovery Rates Comparison\n(as of {target_date})', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Recovery Rate (%)', fontsize=12)
        ax.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, rate in zip(bars, rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1, 
                   f'{rate}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_axisbelow(True)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Determine better management
        better_country = recovery_df.loc[recovery_df['Recovery Rate (%)'].idxmax(), 'Country']
        better_rate = recovery_df.loc[recovery_df['Recovery Rate (%)'].idxmax(), 'Recovery Rate (%)']
        
        st.success(f"🏥 **{better_country}** showed better pandemic management with a recovery rate of **{better_rate}%**")
    
    else:
        st.warning(f"Date {target_date} not found in the dataset")
    
    # Q5.3: Death rates among Canadian provinces
    st.subheader("Q5.3: Death Rates Distribution in Canadian Provinces")
    st.markdown("**Distribution of death rates among provinces in Canada**")
    
    # Get latest date
    latest_date = date_cols[-1]
    
    # Filter Canadian provinces
    canada_confirmed = confirmed_df[confirmed_df['Country/Region'] == 'Canada']
    canada_deaths = deaths_df[deaths_df['Country/Region'] == 'Canada']
    
    province_death_rates = []
    
    for _, province_row in canada_confirmed.iterrows():
        province = province_row['Province/State']
        confirmed_cases = province_row[latest_date]
        
        # Find corresponding death data
        death_row = canada_deaths[canada_deaths['Province/State'] == province]
        if not death_row.empty:
            deaths_count = death_row[latest_date].iloc[0]
            death_rate = (deaths_count / confirmed_cases) * 100 if confirmed_cases > 0 else 0
            
            province_death_rates.append({
                'Province': province,
                'Confirmed Cases': int(confirmed_cases),
                'Deaths': int(deaths_count),
                'Death Rate (%)': round(death_rate, 2)
            })
    
    death_rates_df = pd.DataFrame(province_death_rates)
    death_rates_df = death_rates_df.sort_values('Death Rate (%)', ascending=False)
    
    st.write(f"**Death Rates by Province (as of {latest_date}):**")
    st.dataframe(death_rates_df, use_container_width=True)
    
    # Create enhanced horizontal bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    provinces = death_rates_df['Province']
    rates = death_rates_df['Death Rate (%)']
    
    # Create color gradient
    colors = plt.cm.Reds(np.linspace(0.3, 0.8, len(provinces)))
    bars = ax.barh(provinces, rates, color=colors, alpha=0.8)
    
    ax.set_title('COVID-19 Death Rates by Canadian Province/Territory', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Death Rate (%)', fontsize=12)
    
    # Add value labels
    for i, (bar, rate) in enumerate(zip(bars, rates)):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, 
               f'{rate}%', ha='left', va='center', fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_axisbelow(True)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Identify highest and lowest
    if not death_rates_df.empty:
        highest_province = death_rates_df.iloc[0]
        lowest_province = death_rates_df.iloc[-1]
        
        col1, col2 = st.columns(2)
        with col1:
            st.error(f"🔴 **Highest Death Rate:** {highest_province['Province']} - {highest_province['Death Rate (%)']}%")
        with col2:
            st.success(f"🟢 **Lowest Death Rate:** {lowest_province['Province']} - {lowest_province['Death Rate (%)']}%")
  