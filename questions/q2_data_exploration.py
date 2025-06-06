import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def extract_date_columns_from_dataframe(dataframe):
    """
    Extract date columns from COVID-19 dataset by excluding metadata columns.
    
    Args:
        dataframe (pd.DataFrame): COVID-19 dataset
        
    Returns:
        list: List of date column names
    """
    metadata_columns = {"Province/State", "Country/Region", "Lat", "Long"}
    date_columns = [column for column in dataframe.columns if column not in metadata_columns]
    return date_columns

def transform_wide_format_to_long_format(dataframe, value_column_name):
    """
    Transform COVID-19 dataset from wide format to long format for time series analysis.
    
    Args:
        dataframe (pd.DataFrame): Wide format COVID-19 dataset
        value_column_name (str): Name for the value column (e.g., "Confirmed", "Deaths", "Recovered")
        
    Returns:
        pd.DataFrame: Long format dataset with Date and value columns
    """
    available_date_columns = extract_date_columns_from_dataframe(dataframe)
    
    long_format_dataframe = dataframe.melt(
        id_vars=["Province/State", "Country/Region", "Lat", "Long"],
        value_vars=available_date_columns,
        var_name="Date",
        value_name=value_column_name
    )
    
    # Convert Date column to proper datetime format for time series analysis
    long_format_dataframe["Date"] = pd.to_datetime(long_format_dataframe["Date"])
    
    return long_format_dataframe

def display_comprehensive_data_exploration_section(confirmed_cases_dataframe, deaths_dataframe, recovered_cases_dataframe):
    """
    Display comprehensive data exploration section with dataset structure analysis and visualizations.
    
    Args:
        confirmed_cases_dataframe (pd.DataFrame): COVID-19 confirmed cases dataset
        deaths_dataframe (pd.DataFrame): COVID-19 deaths dataset  
        recovered_cases_dataframe (pd.DataFrame): COVID-19 recovered cases dataset
    """
    st.header("🔍 Question 2: Comprehensive Data Exploration")
    st.markdown("**Objective:** Analyze dataset structures and visualize COVID-19 trends for top affected countries")
    
    # Q2.1: Detailed structure analysis of all datasets
    st.subheader("Q2.1: Dataset Structure Analysis")
    st.markdown("**Comprehensive overview of each dataset's structure, dimensions, and coverage**")
    
    # Create organized columns for better layout
    structure_analysis_column_1, structure_analysis_column_2, structure_analysis_column_3 = st.columns(3)
    
    covid_datasets_list = [confirmed_cases_dataframe, deaths_dataframe, recovered_cases_dataframe]
    dataset_names_list = ["📈 Confirmed Cases", "💀 Deaths", "🏥 Recovery Cases"]
    analysis_columns_list = [structure_analysis_column_1, structure_analysis_column_2, structure_analysis_column_3]
    
    # Display structure information for each dataset
    for current_dataset, current_column, dataset_display_name in zip(covid_datasets_list, analysis_columns_list, dataset_names_list):
        with current_column:
            st.subheader(dataset_display_name)
            
            # Calculate key metrics
            total_rows_count = current_dataset.shape[0]
            total_columns_count = current_dataset.shape[1]
            unique_countries_count = current_dataset['Country/Region'].nunique()
            unique_provinces_count = current_dataset['Province/State'].nunique()
            available_date_columns = extract_date_columns_from_dataframe(current_dataset)
            date_range_span = len(available_date_columns)
            
            # Display metrics in organized format
            st.metric("Total Locations", f"{total_rows_count:,}")
            st.metric("Total Columns", f"{total_columns_count:,}")
            st.metric("Countries Covered", f"{unique_countries_count:,}")
            st.metric("Date Range (Days)", f"{date_range_span:,}")
            
            # Show date range information
            if available_date_columns:
                first_date = available_date_columns[0]
                last_date = available_date_columns[-1]
                st.info(f"**Period:** {first_date} to {last_date}")
    
    # Enhanced summary section
    st.markdown("---")
    st.subheader("📊 Dataset Summary Comparison")
    
    summary_comparison_dataframe = pd.DataFrame({
        'Dataset Type': ['Confirmed Cases', 'Deaths', 'Recovery Cases'],
        'Total Locations': [df.shape[0] for df in covid_datasets_list],
        'Countries': [df['Country/Region'].nunique() for df in covid_datasets_list],
        'Date Columns': [len(extract_date_columns_from_dataframe(df)) for df in covid_datasets_list]
    })
    
    st.dataframe(summary_comparison_dataframe, use_container_width=True)
    
    # Q2.2: Interactive visualization of top countries over time
    st.subheader("Q2.2: Top Countries COVID-19 Confirmed Cases Timeline")
    st.markdown("**Interactive analysis of confirmed cases progression for most affected countries**")
    
    # Enhanced country selection interface
    countries_selection_column_1, countries_selection_column_2 = st.columns([1, 1])
    
    with countries_selection_column_1:
        number_of_top_countries_to_display = st.selectbox(
            "📊 Select number of top countries to analyze:",
            options=[5, 10, 15, 20, 25, 30],
            index=0,
            help="Choose how many top countries by confirmed cases to display"
        )
    
    with countries_selection_column_2:
        visualization_style_option = st.selectbox(
            "🎨 Select visualization style:",
            options=["Line Plot", "Area Plot"],
            index=0,
            help="Choose the type of visualization for the time series data"
        )
    
    # Calculate top countries based on latest confirmed cases
    available_date_columns_for_confirmed = extract_date_columns_from_dataframe(confirmed_cases_dataframe)
    most_recent_date_column = available_date_columns_for_confirmed[-1]
    
    # Get top countries by aggregating all provinces/states per country
    top_countries_by_confirmed_cases = (confirmed_cases_dataframe
                                       .groupby('Country/Region')[most_recent_date_column]
                                       .sum()
                                       .sort_values(ascending=False)
                                       .head(number_of_top_countries_to_display))
    
    # Transform confirmed cases data to long format for visualization
    confirmed_cases_long_format = transform_wide_format_to_long_format(confirmed_cases_dataframe, "Confirmed_Cases")
    
    # Filter data for selected top countries
    top_countries_time_series_data = confirmed_cases_long_format[
        confirmed_cases_long_format['Country/Region'].isin(top_countries_by_confirmed_cases.index)
    ]
    
    # Create enhanced visualization
    matplotlib_figure, matplotlib_axes = plt.subplots(figsize=(14, 8))
    
    # Set color palette for better distinction
    color_palette_for_countries = plt.cm.Set3(range(len(top_countries_by_confirmed_cases.index)))
    
    # Plot data for each country
    for country_index, selected_country_name in enumerate(top_countries_by_confirmed_cases.index):
        country_specific_data = top_countries_time_series_data[
            top_countries_time_series_data['Country/Region'] == selected_country_name
        ]
        
        # Aggregate data by date for countries with multiple provinces
        country_daily_totals = country_specific_data.groupby('Date')['Confirmed_Cases'].sum()
        
        current_country_color = color_palette_for_countries[country_index]
        
        if visualization_style_option == "Area Plot":
            matplotlib_axes.fill_between(
                country_daily_totals.index, 
                country_daily_totals.values, 
                alpha=0.3, 
                color=current_country_color,
                label=selected_country_name
            )
            matplotlib_axes.plot(
                country_daily_totals.index, 
                country_daily_totals.values, 
                color=current_country_color, 
                linewidth=2
            )
        else:
            matplotlib_axes.plot(
                country_daily_totals.index, 
                country_daily_totals.values, 
                label=selected_country_name, 
                linewidth=2.5,
                color=current_country_color
            )
    
    # Enhanced plot formatting
    matplotlib_axes.set_title(
        f'COVID-19 Confirmed Cases Timeline - Top {number_of_top_countries_to_display} Countries', 
        fontsize=16, 
        fontweight='bold',
        pad=20
    )
    matplotlib_axes.set_xlabel('Date', fontsize=12, fontweight='bold')
    matplotlib_axes.set_ylabel('Confirmed Cases', fontsize=12, fontweight='bold')
    
    # Improved legend positioning
    matplotlib_axes.legend(
        bbox_to_anchor=(1.05, 1), 
        loc='upper left',
        fontsize=10,
        frameon=True,
        fancybox=True,
        shadow=True
    )
    
    matplotlib_axes.grid(True, alpha=0.3, linestyle='--')
    matplotlib_axes.tick_params(axis='x', rotation=45)
    
    # Format y-axis for better readability
    matplotlib_axes.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
    
    plt.tight_layout()
    st.pyplot(matplotlib_figure)
    
    # Display detailed statistics table
    st.subheader(f"📋 Top {number_of_top_countries_to_display} Countries Statistics")
    
    countries_statistics_dataframe = pd.DataFrame({
        'Rank': range(1, len(top_countries_by_confirmed_cases) + 1),
        'Country': top_countries_by_confirmed_cases.index,
        'Total Confirmed Cases': [f"{cases:,}" for cases in top_countries_by_confirmed_cases.values],
        'Percentage of Global Cases': [f"{(cases/top_countries_by_confirmed_cases.sum()*100):.1f}%" 
                                     for cases in top_countries_by_confirmed_cases.values]
    })
    
    st.dataframe(countries_statistics_dataframe, use_container_width=True, hide_index=True)
    
    # Q2.3: Detailed China-specific analysis
    st.subheader("Q2.3: China COVID-19 Confirmed Cases - Detailed Analysis")
    st.markdown("**Comprehensive analysis of COVID-19 progression in China as the initial epicenter**")
    
    # Transform and filter data for China
    china_specific_time_series_data = confirmed_cases_long_format[
        confirmed_cases_long_format['Country/Region'] == 'China'
    ]
    
    if not china_specific_time_series_data.empty:
        # Calculate daily totals for all Chinese provinces
        china_daily_confirmed_totals = china_specific_time_series_data.groupby('Date')['Confirmed_Cases'].sum()
        
        # Create comprehensive China visualization
        china_analysis_figure, china_analysis_axes = plt.subplots(figsize=(12, 6))
        
        # Main trend line
        china_analysis_axes.plot(
            china_daily_confirmed_totals.index, 
            china_daily_confirmed_totals.values, 
            color='#d62728', 
            linewidth=4, 
            label='Total Confirmed Cases',
            marker='o',
            markersize=2,
            alpha=0.8
        )
        
        # Add filled area for visual appeal
        china_analysis_axes.fill_between(
            china_daily_confirmed_totals.index, 
            china_daily_confirmed_totals.values, 
            alpha=0.2, 
            color='#d62728'
        )
        
        # Enhanced plot formatting
        china_analysis_axes.set_title(
            'COVID-19 Confirmed Cases Evolution - China', 
            fontsize=16, 
            fontweight='bold',
            pad=20
        )
        china_analysis_axes.set_xlabel('Date', fontsize=12, fontweight='bold')
        china_analysis_axes.set_ylabel('Confirmed Cases', fontsize=12, fontweight='bold')
        china_analysis_axes.grid(True, alpha=0.3, linestyle='--')
        china_analysis_axes.tick_params(axis='x', rotation=45)
        
        # Format y-axis for better readability
        china_analysis_axes.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f'{x/1e3:.0f}K' if x >= 1e3 else f'{x:.0f}')
        )
        
        plt.tight_layout()
        st.pyplot(china_analysis_figure)
        
        # Detailed China statistics
        china_statistics_column_1, china_statistics_column_2, china_statistics_column_3, china_statistics_column_4 = st.columns(4)
        
        # Calculate key metrics for China
        china_total_cases = int(china_daily_confirmed_totals.iloc[-1])
        china_first_case_series = china_daily_confirmed_totals[china_daily_confirmed_totals > 0]
        china_first_case_date = china_first_case_series.index[0] if len(china_first_case_series) > 0 else None
        china_peak_cases = int(china_daily_confirmed_totals.max())
        china_peak_date = china_daily_confirmed_totals.idxmax()
        
        # Display comprehensive metrics
        with china_statistics_column_1:
            st.metric(
                "Total Confirmed Cases", 
                f"{china_total_cases:,}",
                help="Total cumulative confirmed cases in China"
            )
        
        with china_statistics_column_2:
            if china_first_case_date:
                st.metric(
                    "First Case Reported", 
                    china_first_case_date.strftime("%Y-%m-%d"),
                    help="Date when first case was reported"
                )
        
        with china_statistics_column_3:
            st.metric(
                "Peak Daily Total", 
                f"{china_peak_cases:,}",
                help="Highest cumulative case count reached"
            )
        
        with china_statistics_column_4:
            st.metric(
                "Peak Date", 
                china_peak_date.strftime("%Y-%m-%d"),
                help="Date when peak cases were reached"
            )
        
        # Additional insights section
        st.markdown("---")
        st.subheader("🔍 Key Insights from China Analysis")
        
        insights_column_1, insights_column_2 = st.columns(2)
        
        with insights_column_1:
            st.success(f"""
            **Timeline Analysis:**
            - First case reported: {china_first_case_date.strftime("%B %d, %Y") if china_first_case_date else "N/A"}
            - Peak reached on: {china_peak_date.strftime("%B %d, %Y")}
            - Total confirmed cases: {china_total_cases:,}
            """)
        
        with insights_column_2:
            # Calculate growth metrics
            if len(china_daily_confirmed_totals) > 30:
                cases_30_days_ago = china_daily_confirmed_totals.iloc[-30]
                recent_growth_rate = ((china_total_cases - cases_30_days_ago) / cases_30_days_ago * 100) if cases_30_days_ago > 0 else 0
                
                st.info(f"""
                **Growth Analysis:**
                - Peak cases: {china_peak_cases:,}
                - 30-day growth rate: {recent_growth_rate:.2f}%
                - Data coverage: {len(china_daily_confirmed_totals)} days
                """)
            
    else:
        st.warning("⚠️ No data found for China in the confirmed cases dataset.")
        st.info("This might indicate that China is listed under a different name or the data is not available.")
    
    # Summary section
    st.markdown("---")
    st.subheader("📊 Data Exploration Summary")
    st.success(f"""
    ✅ **Analysis Completed Successfully:**
    
    **Dataset Structure Analysis:**
    - Analyzed {len(covid_datasets_list)} COVID-19 datasets with comprehensive metrics
    - Covered {confirmed_cases_dataframe['Country/Region'].nunique()} countries and regions
    - Time series data spanning {len(extract_date_columns_from_dataframe(confirmed_cases_dataframe))} days
    
    **Top Countries Visualization:**
    - Displayed trends for top {number_of_top_countries_to_display} countries by confirmed cases
    - Used {visualization_style_option.lower()} visualization for clear trend analysis
    - Provided detailed statistics and percentage breakdowns
    
    **China-Specific Analysis:**
    - Comprehensive timeline analysis of COVID-19 progression
    - Key milestone identification and growth pattern analysis
    - Statistical insights for the initial pandemic epicenter
    """)

# Maintain compatibility with main.py by providing the expected function name
def show_data_exploration_section(confirmed_df, deaths_df, recovered_df):
    """
    Wrapper function to maintain compatibility with main.py
    
    Args:
        confirmed_df (pd.DataFrame): COVID-19 confirmed cases dataset
        deaths_df (pd.DataFrame): COVID-19 deaths dataset
        recovered_df (pd.DataFrame): COVID-19 recovered cases dataset
    """
    display_comprehensive_data_exploration_section(confirmed_df, deaths_df, recovered_df)
