# 🦠 COVID-19 Data Analysis Dashboard

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.45+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Overview

A comprehensive data analysis project examining COVID-19 pandemic trends using Python, Pandas, and Streamlit. This project analyzes confirmed cases, deaths, and recoveries across different countries from January 22, 2020, to May 29, 2021.

## 🎯 Features

- **Interactive Data Exploration**: Analyze COVID-19 trends with dynamic visualizations
- **Multi-Dataset Analysis**: Combined analysis of confirmed cases, deaths, and recoveries
- **Country Comparisons**: Compare pandemic impact across different nations
- **Time Series Analysis**: Track pandemic progression over time
- **Data Transformation**: Clean and process real-world pandemic data

## 📊 Analysis Sections

1. **Data Loading**: Import and initial setup of COVID-19 datasets
2. **Data Exploration**: Structure analysis and top countries visualization
3. **Missing Data Handling**: Forward-fill imputation for time-series data
4. **Data Cleaning**: Standardization and preparation
5. **Independent Analysis**: Peak cases, recovery rates, and provincial analysis
6. **Data Transformation**: Wide-to-long format conversion
7. **Data Merging**: Comprehensive dataset combination
8. **Combined Analysis**: Advanced insights and comparisons

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Required packages (see `pyproject.toml`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/covid19-data-analysis.git
cd covid19-data-analysis

Install dependencies:pip install -r requirements.txt
Run the Streamlit app:streamlit run main.py
📁 Project Structure
COVID_19_v1/
├── main.py                          # Main Streamlit application
├── covid_19_confirmed_v1.csv        # Confirmed cases dataset
├── covid_19_deaths_v1.csv           # Deaths dataset
├── covid_19_recovered_v1.csv        # Recovered cases dataset
├── questions/                       # Analysis modules
│   ├── q1_data_loading.py
│   ├── q2_data_exploration.py
│   ├── q3_handling_missing_data.py
│   ├── q4_data_cleaning.py
│   ├── q5_independent_analysis.py
│   ├── q6_data_transformation.py
│   ├── q7_data_merging.py
│   └── q8_combined_analysis.py
├── pyproject.toml                   # Project dependencies
└── README.md
📈 Key Insights
Global Impact: Analysis of 276+ geographic regions
Time Period: 16+ months of pandemic data
Recovery Patterns: Country-wise recovery rate comparisons
Mortality Analysis: Death rate distributions and trends
Peak Analysis: Identification of surge periods
🛠️ Technologies Used
Python 3.11: Core programming language
Pandas: Data manipulation and analysis
Streamlit: Interactive web application framework
Matplotlib: Data visualization
Plotly: Interactive charts
NumPy: Numerical computations
📝 Analysis Questions Covered
Question 1: Data Loading
Loading COVID-19 datasets using Pandas
Question 2: Data Exploration
Dataset structure analysis
Top countries visualization
China-specific trends
Question 3: Missing Data Handling
Forward-fill imputation for time-series
Question 4: Data Cleaning
Province/State standardization
Question 5: Independent Analysis
Peak cases in Germany, France, Italy
Recovery rate comparisons (Canada vs Australia)
Provincial death rate analysis in Canada
Question 6: Data Transformation
Wide-to-long format conversion
Country-wise death totals
Average daily deaths analysis
US death evolution tracking
Question 7: Data Merging
Multi-dataset integration
Monthly progression analysis
US, Italy, Brazil focused comparison
Question 8: Combined Analysis
Highest death rate countries (2020)
South Africa recovery vs deaths
US monthly recovery ratios
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👨‍💻 Author
Pushkar Shukla

Data Science Cohort Project
Full Stack Data Science 1.0
🙏 Acknowledgments
COVID-19 data sources
Johns Hopkins University (potential data source)
Python data science community
⭐ Star this repository if you found it helpful!