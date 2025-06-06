import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def get_date_columns(df):
    meta_cols = {"Province/State", "Country/Region", "Lat", "Long"}
    return [col for col in df.columns if col not in meta_cols]

def show_handling_missing_data_section(confirmed_df, deaths_df, recovered_df):
    st.header("🧹 Question 3: Handling Missing Data")
    
    st.markdown("**Q3.1:** Identify missing values and replace them using forward filling for time-series data")
    
    datasets = [confirmed_df, deaths_df, recovered_df]
    names = ["Confirmed", "Deaths", "Recovered"]
    
    # Check missing values before cleaning
    st.subheader("Missing Values Before Cleaning")
    
    col1, col2, col3 = st.columns(3)
    for df, col, name in zip(datasets, [col1, col2, col3], names):
        with col:
            st.write(f"**{name} Dataset**")
            total_missing = df.isnull().sum().sum()
            st.write(f"Missing values: {total_missing}")
            st.write(f"Total cells: {df.shape[0] * df.shape[1]}")
    
    # Show missing values in Province/State column specifically
    st.subheader("Missing Values in Key Columns")
    for df, name in zip(datasets, names):
        province_missing = df["Province/State"].isnull().sum()
        st.write(f"**{name}**: {province_missing} missing Province/State values")
    
    # Apply forward filling
    st.subheader("Applying Forward Fill Method")
    st.write("Forward fill replaces missing values with the last valid observation, suitable for time-series data.")
    
    cleaned_datasets = []
    
    for df, name in zip(datasets, names):
        df_cleaned = df.copy()
        
        # Get date columns and apply forward fill
        date_cols = get_date_columns(df_cleaned)
        df_cleaned[date_cols] = df_cleaned[date_cols].fillna(method='ffill', axis=1)
        
        # Fill any remaining missing values with 0
        df_cleaned[date_cols] = df_cleaned[date_cols].fillna(0)
        
        # Handle missing Province/State
        if 'Province/State' in df_cleaned.columns:
            df_cleaned['Province/State'] = df_cleaned['Province/State'].fillna('Unknown')
        
        cleaned_datasets.append(df_cleaned)
    
    # Show results after cleaning
    st.subheader("Results After Forward Fill")
    
    col1, col2, col3 = st.columns(3)
    for df_clean, col, name in zip(cleaned_datasets, [col1, col2, col3], names):
        with col:
            st.write(f"**{name} Dataset**")
            total_missing_after = df_clean.isnull().sum().sum()
            st.write(f"Missing values after: {total_missing_after}")
            if total_missing_after == 0:
                st.success("✅ No missing values")
    
    # Simple before/after comparison
    st.subheader("Before vs After Comparison")
    comparison_data = []
    for i, name in enumerate(names):
        before = datasets[i].isnull().sum().sum()
        after = cleaned_datasets[i].isnull().sum().sum()
        comparison_data.append([name, before, after])
    
    comparison_df = pd.DataFrame(comparison_data, columns=['Dataset', 'Before', 'After'])
    st.dataframe(comparison_df)
    
    # Show example of forward fill effect
    st.subheader("Example: Forward Fill Effect")
    
    # Take first row of confirmed data to show effect
    sample_row = confirmed_df.iloc[0:1].copy()
    date_cols = get_date_columns(sample_row)[:10]  # First 10 date columns
    
    # Create some artificial missing values for demonstration
    sample_with_missing = sample_row.copy()
    sample_with_missing.loc[sample_row.index[0], date_cols[2:5]] = None
    
    # Apply forward fill
    sample_cleaned = sample_with_missing.copy()
    sample_cleaned[date_cols] = sample_cleaned[date_cols].fillna(method='ffill', axis=1)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Before (with some missing):**")
        st.dataframe(sample_with_missing[['Country/Region'] + date_cols])
    
    with col2:
        st.write("**After Forward Fill:**")
        st.dataframe(sample_cleaned[['Country/Region'] + date_cols])
    
    st.success("✅ Missing data handling completed using forward fill method")
    
    return cleaned_datasets[0], cleaned_datasets[1], cleaned_datasets[2]
