import streamlit as st
import pandas as pd

def show_data_cleaning_section(confirmed_df, deaths_df, recovered_df):
    st.header("✨ Question 4: Data Cleaning and Preparation")
    
    st.markdown("**Q4.1:** Replace blank values in the province column with 'All Provinces'")
    
    datasets = [confirmed_df, deaths_df, recovered_df]
    names = ["Confirmed", "Deaths", "Recovered"]
    
    # Check current state of Province/State column
    st.subheader("Before Cleaning - Province/State Column Analysis")
    
    col1, col2, col3 = st.columns(3)
    for df, col, name in zip(datasets, [col1, col2, col3], names):
        with col:
            st.write(f"**{name} Dataset**")
            
            # Count null and blank values
            null_count = df["Province/State"].isnull().sum()
            blank_count = (df["Province/State"] == "").sum()
            total_rows = len(df)
            
            st.write(f"Total rows: {total_rows}")
            st.write(f"Null values: {null_count}")
            st.write(f"Blank values: {blank_count}")
            st.write(f"Values to replace: {null_count + blank_count}")
    
    # Show sample of problematic rows
    st.subheader("Sample of Rows with Missing Province/State")
    
    # Find rows with missing province data
    sample_missing = confirmed_df[
        (confirmed_df["Province/State"].isnull()) | 
        (confirmed_df["Province/State"] == "")
    ].head(5)
    
    if not sample_missing.empty:
        st.write("**Examples of rows with missing Province/State:**")
        st.dataframe(sample_missing[["Province/State", "Country/Region", "Lat", "Long"]])
    else:
        st.info("No missing Province/State values found in the current data")
    
    # Apply data cleaning
    st.subheader("Applying Data Cleaning")
    st.write("Replacing null and blank values in Province/State column with 'All Provinces'")
    
    with st.expander("📋 View Code"):
        st.code("""
# Replace null and blank values with 'All Provinces'
df['Province/State'] = df['Province/State'].fillna('All Provinces')
df['Province/State'] = df['Province/State'].replace('', 'All Provinces')
        """, language="python")
    
    # Clean the datasets
    cleaned_datasets = []
    
    for df, name in zip(datasets, names):
        df_cleaned = df.copy()
        
        # Replace null values with 'All Provinces'
        df_cleaned['Province/State'] = df_cleaned['Province/State'].fillna('All Provinces')
        
        # Replace blank/empty strings with 'All Provinces'
        df_cleaned['Province/State'] = df_cleaned['Province/State'].replace('', 'All Provinces')
        
        cleaned_datasets.append(df_cleaned)
    
    # Show results after cleaning
    st.subheader("After Cleaning - Results")
    
    col1, col2, col3 = st.columns(3)
    for df_clean, col, name in zip(cleaned_datasets, [col1, col2, col3], names):
        with col:
            st.write(f"**{name} Dataset**")
            
            # Count remaining issues
            null_count_after = df_clean["Province/State"].isnull().sum()
            blank_count_after = (df_clean["Province/State"] == "").sum()
            all_provinces_count = (df_clean["Province/State"] == "All Provinces").sum()
            
            st.write(f"Null values: {null_count_after}")
            st.write(f"Blank values: {blank_count_after}")
            st.write(f"'All Provinces': {all_provinces_count}")
            
            if null_count_after == 0 and blank_count_after == 0:
                st.success("✅ Cleaned successfully")
    
    # Show before/after comparison
    st.subheader("Before vs After Comparison")
    
    comparison_data = []
    for i, name in enumerate(names):
        before_null = datasets[i]["Province/State"].isnull().sum()
        before_blank = (datasets[i]["Province/State"] == "").sum()
        before_total = before_null + before_blank
        
        after_null = cleaned_datasets[i]["Province/State"].isnull().sum()
        after_blank = (cleaned_datasets[i]["Province/State"] == "").sum()
        after_total = after_null + after_blank
        
        comparison_data.append({
            'Dataset': name,
            'Before (Missing)': before_total,
            'After (Missing)': after_total,
            'Cleaned': before_total - after_total
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)
    
    # Show sample of cleaned data
    st.subheader("Sample of Cleaned Data")
    
    # Show rows that were changed
    cleaned_sample = cleaned_datasets[0][
        cleaned_datasets[0]["Province/State"] == "All Provinces"
    ].head(5)
    
    if not cleaned_sample.empty:
        st.write("**Examples of cleaned rows (now showing 'All Provinces'):**")
        st.dataframe(cleaned_sample[["Province/State", "Country/Region", "Lat", "Long"]])
    
    # Show unique values in Province/State column
    st.subheader("Province/State Column Summary")
    
    tab1, tab2, tab3 = st.tabs(["✅ Confirmed", "💀 Deaths", "💚 Recovered"])
    
    for df_clean, tab, name in zip(cleaned_datasets, [tab1, tab2, tab3], names):
        with tab:
            unique_provinces = df_clean["Province/State"].value_counts().head(10)
            st.write(f"**Top 10 Province/State values in {name} dataset:**")
            for province, count in unique_provinces.items():
                st.write(f"• {province}: {count} entries")
    
    st.success("✅ Data cleaning completed: All blank and null values in Province/State column replaced with 'All Provinces'")
    
    # Return cleaned datasets for use in other questions
    return cleaned_datasets[0], cleaned_datasets[1], cleaned_datasets[2]
