# 🦠 COVID-19 Data Analysis Dashboard

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.45+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen.svg)

## 📋 Overview

A comprehensive COVID-19 data analysis dashboard built with Streamlit, featuring interactive visualizations, statistical analysis, and an AI-powered assistant for real-time data insights. This project analyzes COVID-19 confirmed cases, deaths, and recoveries from January 2020 to May 2021.

## 🎯 Features

- **📊 Interactive Dashboard**: Beautiful, responsive Streamlit interface
- **🤖 AI-Powered Assistant**: Real-time data analysis with GitHub's AI models
- **📈 Comprehensive Analysis**: 8 detailed analysis sections covering all aspects of the data
- **🌍 Global Coverage**: Data from 180+ countries and regions
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🔍 Real-time Insights**: Ask the AI assistant any questions about the data

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token (for AI features)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/covid19-data-analysis.git
cd covid19-data-analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (for AI features):**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your GitHub token
# Get your token from: https://github.com/settings/tokens
```

4. **Run the Streamlit app:**
```bash
streamlit run main.py
```

## 🤖 AI Features Setup

The AI assistant requires a GitHub Personal Access Token for enhanced features:

1. **Get a GitHub Token:**
   - Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `read:user`
   - Copy the generated token

2. **Configure the token:**
   ```bash
   # Method 1: Using .env file (recommended)
   echo "GITHUB_TOKEN=your_token_here" > .env
   
   # Method 2: Environment variable
   export GITHUB_TOKEN=your_token_here  # Linux/Mac
   set GITHUB_TOKEN=your_token_here     # Windows
   ```

3. **Restart the application**

> **Note:** The app works fully without AI features - they're an optional enhancement!

## 📁 Project Structure

```
COVID_19_v1/
├── main.py                          # Main Streamlit application
├── covid_19_confirmed_v1.csv        # Confirmed cases dataset
├── covid_19_deaths_v1.csv           # Deaths dataset
├── covid_19_recovered_v1.csv        # Recovered cases dataset
├── questions/                       # Analysis modules
│   ├── q1_data_loading.py          # Data loading and overview
│   ├── q2_data_exploration.py      # Exploratory data analysis
│   ├── q3_handling_missing_data.py # Missing data handling
│   ├── q4_data_cleaning.py         # Data cleaning
│   ├── q5_independent_analysis.py  # Individual dataset analysis
│   ├── q6_data_transformation.py   # Data transformation
│   ├── q7_data_merging.py          # Data merging techniques
│   ├── q8_combined_analysis.py     # Combined analysis
│   └── q9_ai_insights.py           # AI-powered insights
├── requirements.txt                 # Dependencies
├── pyproject.toml                  # Project configuration
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 📊 Analysis Sections

### **Question 1: Data Loading**
- Dataset overview and structure
- Basic statistics and data types
- Initial data quality assessment

### **Question 2: Data Exploration**
- Country-wise analysis and rankings
- Time series visualizations
- China-specific analysis (pandemic origin)

### **Question 3: Missing Data Handling**
- Missing data identification
- Forward-fill imputation for time-series
- Data completeness analysis

### **Question 4: Data Cleaning**
- Province/State standardization
- Data consistency checks
- Outlier detection and handling

### **Question 5: Independent Analysis**
- Peak cases in Germany, France, Italy
- Recovery rate comparisons (Canada vs Australia)
- Provincial death rate analysis in Canada

### **Question 6: Data Transformation**
- Wide-to-long format conversion
- Country-wise death totals
- Average daily deaths analysis
- US death evolution tracking

### **Question 7: Data Merging**
- Multi-dataset integration
- Monthly progression analysis
- US, Italy, Brazil focused comparison

### **Question 8: Combined Analysis**
- Highest death rate countries (2020)
- South Africa recovery vs deaths
- US monthly recovery ratios

### **🤖 AI Data Assistant**
- Real-time data analysis
- Natural language queries
- Country comparisons
- Statistical calculations on demand

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **AI Integration**: Azure AI Inference (GitHub Models)
- **Environment Management**: python-dotenv

## 📊 Dataset Information

- **Source**: COVID-19 time series data
- **Period**: January 22, 2020 - May 29, 2021
- **Coverage**: 180+ countries and regions
- **Granularity**: Daily cumulative counts
- **Variables**: Confirmed cases, Deaths, Recoveries

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required for AI features
GITHUB_TOKEN=your_github_personal_access_token

# Optional
ENVIRONMENT=production
```

### Streamlit Configuration

The app uses default Streamlit settings. For custom configuration, create `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "localhost"

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Pushkar Shukla**
- Data Science Cohort Project
- Full Stack Data Science 1.0

## 🙏 Acknowledgments

- COVID-19 data sources and contributors
- Johns Hopkins University (potential data source)
- Python data science community
- **AI Tools & Assistance**: This project was developed with significant help from AI technologies for code optimization, problem-solving, and best practices implementation

## ⚠️ Important Disclaimer

This project was completed with substantial assistance from AI tools and technologies. While the learning outcomes and insights are genuine, the development process involved AI support for:

- Code structure and optimization
- Data analysis techniques
- Visualization improvements
- Documentation and commenting
- Debugging and troubleshooting

This represents a modern approach to data science learning, combining human curiosity with AI capabilities.

## 🚀 Deployment

### Local Development
```bash
streamlit run main.py
```

### Production Deployment

The app can be deployed on various platforms:

- **Streamlit Cloud**: Connect your GitHub repo for automatic deployment
- **Heroku**: Use the provided `Procfile`
- **AWS/GCP/Azure**: Container-based deployment with Docker

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/covid19-data-analysis/issues) page
2. Create a new issue with detailed information
3. Ensure you have the latest version of dependencies

## ⭐ Star this repository if you found it helpful!

---

**Note**: This is an educational project demonstrating data science techniques and AI integration. Always verify critical health information with official sources.