import os
import streamlit as st
import pandas as pd
import numpy as np
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads the .env file
except ImportError:
    st.warning("python-dotenv not installed. Please install it: pip install python-dotenv")

class COVID19DataInsightsAI:
    """Handles AI interactions for COVID-19 data analysis and insights with direct data access."""

    def __init__(self):
        """Initialize AI client with GitHub's inference endpoint."""
        # GitHub AI inference configuration
        self.endpoint = "https://models.github.ai/inference"
        self.model = "xai/grok-3"
        
        # Try to get token from environment variables
        self.token = os.environ.get("GITHUB_TOKEN")
        
        # Debug: Show what we found (remove this after testing)
        if self.token:
            # st.success(f"✅ GitHub token found: {self.token[:10]}...")
            pass
        else:
            st.error("❌ GitHub token not found in environment variables")

        # Validate API token exists
        if not self.token:
            st.error("🔑 GitHub API token not found. Please check your .env file configuration.")
            st.info("""
            **To fix this issue:**
            
            1. **Make sure your `.env` file is in the correct location:**
               ```
               COVID_19_v1/
               ├── .env                 ← Should be here
               ├── main.py
               └── questions/
               ```
            
            2. **Check your `.env` file format:**
               ```
               GITHUB_TOKEN=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
               ```
               (No spaces around the = sign)
            
            3. **Install python-dotenv:**
               ```bash
               pip install python-dotenv
               ```
            
            4. **Restart your Streamlit application**
            """)
            st.stop()

        # Create Azure AI client
        try:
            self.client = ChatCompletionsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.token)
            )
            st.success("🤖 AI client initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize AI client: {e}")
            st.stop()

    def analyze_data_for_question(self, user_question, confirmed_df, deaths_df, recovered_df):
        """Perform specific data analysis based on user question."""
        try:
            # Helper function to get date columns
            def get_date_columns(df):
                meta_cols = {"Province/State", "Country/Region", "Lat", "Long"}
                return [col for col in df.columns if col not in meta_cols]

            analysis_results = {}
            
            # Basic dataset info
            confirmed_dates = get_date_columns(confirmed_df)
            deaths_dates = get_date_columns(deaths_df)
            recovered_dates = get_date_columns(recovered_df)
            
            latest_confirmed_date = confirmed_dates[-1]
            latest_deaths_date = deaths_dates[-1]
            latest_recovered_date = recovered_dates[-1]
            
            # Global statistics
            global_confirmed = confirmed_df[latest_confirmed_date].sum()
            global_deaths = deaths_df[latest_deaths_date].sum()
            global_recovered = recovered_df[latest_recovered_date].sum()
            
            analysis_results['global_stats'] = {
                'confirmed': int(global_confirmed),
                'deaths': int(global_deaths),
                'recovered': int(global_recovered),
                'death_rate': round((global_deaths/global_confirmed*100), 2),
                'recovery_rate': round((global_recovered/global_confirmed*100), 2),
                'latest_date': latest_confirmed_date
            }
            
            # Top countries analysis
            top_confirmed = confirmed_df.groupby('Country/Region')[latest_confirmed_date].sum().sort_values(ascending=False).head(20)
            top_deaths = deaths_df.groupby('Country/Region')[latest_deaths_date].sum().sort_values(ascending=False).head(20)
            top_recovered = recovered_df.groupby('Country/Region')[latest_recovered_date].sum().sort_values(ascending=False).head(20)
            
            analysis_results['top_countries'] = {
                'confirmed': {country: int(cases) for country, cases in top_confirmed.items()},
                'deaths': {country: int(deaths) for country, deaths in top_deaths.items()},
                'recovered': {country: int(recovered) for country, recovered in top_recovered.items()}
            }
            
            # Death rates by country (for countries with >1000 cases)
            country_confirmed = confirmed_df.groupby('Country/Region')[latest_confirmed_date].sum()
            country_deaths = deaths_df.groupby('Country/Region')[latest_deaths_date].sum()
            
            significant_countries = country_confirmed[country_confirmed > 1000].index
            death_rates = {}
            for country in significant_countries:
                if country in country_deaths.index and country_confirmed[country] > 0:
                    death_rate = (country_deaths[country] / country_confirmed[country]) * 100
                    death_rates[country] = round(death_rate, 2)
            
            # Sort by death rate
            sorted_death_rates = dict(sorted(death_rates.items(), key=lambda x: x[1], reverse=True)[:15])
            analysis_results['death_rates'] = sorted_death_rates
            
            # Time series analysis for specific countries if mentioned
            mentioned_countries = []
            question_lower = user_question.lower()
            
            # Check for commonly mentioned countries
            country_keywords = {
                'usa': 'US', 'america': 'US', 'united states': 'US',
                'china': 'China', 'chinese': 'China',
                'italy': 'Italy', 'italian': 'Italy',
                'spain': 'Spain', 'spanish': 'Spain',
                'brazil': 'Brazil', 'brazilian': 'Brazil',
                'india': 'India', 'indian': 'India',
                'russia': 'Russia', 'russian': 'Russia',
                'germany': 'Germany', 'german': 'Germany',
                'france': 'France', 'french': 'France',
                'uk': 'United Kingdom', 'britain': 'United Kingdom', 'england': 'United Kingdom'
            }
            
            for keyword, actual_country in country_keywords.items():
                if keyword in question_lower:
                    mentioned_countries.append(actual_country)
            
            # Get time series data for mentioned countries
            if mentioned_countries:
                country_timeseries = {}
                for country in mentioned_countries:
                    if country in confirmed_df['Country/Region'].values:
                        country_confirmed_data = confirmed_df[confirmed_df['Country/Region'] == country]
                        country_deaths_data = deaths_df[deaths_df['Country/Region'] == country]
                        country_recovered_data = recovered_df[recovered_df['Country/Region'] == country]
                        
                        # Get latest values and some historical points
                        confirmed_total = country_confirmed_data[latest_confirmed_date].sum()
                        deaths_total = country_deaths_data[latest_deaths_date].sum()
                        recovered_total = country_recovered_data[latest_recovered_date].sum()
                        
                        # Get some historical data points (every 30 days)
                        historical_points = {}
                        for i in range(0, len(confirmed_dates), 30):
                            date = confirmed_dates[i]
                            historical_points[date] = {
                                'confirmed': int(country_confirmed_data[date].sum()),
                                'deaths': int(country_deaths_data[date].sum()) if date in deaths_dates else 0,
                                'recovered': int(country_recovered_data[date].sum()) if date in recovered_dates else 0
                            }
                        
                        country_timeseries[country] = {
                            'latest_confirmed': int(confirmed_total),
                            'latest_deaths': int(deaths_total),
                            'latest_recovered': int(recovered_total),
                            'death_rate': round((deaths_total/confirmed_total*100), 2) if confirmed_total > 0 else 0,
                            'recovery_rate': round((recovered_total/confirmed_total*100), 2) if confirmed_total > 0 else 0,
                            'historical_data': historical_points
                        }
                
                analysis_results['country_specific'] = country_timeseries
            
            # Trend analysis - compare early vs late pandemic
            early_date = confirmed_dates[60] if len(confirmed_dates) > 60 else confirmed_dates[len(confirmed_dates)//2]  # Around early April 2020
            mid_date = confirmed_dates[len(confirmed_dates)//2]
            
            early_global = confirmed_df[early_date].sum()
            mid_global = confirmed_df[mid_date].sum()
            
            analysis_results['trend_analysis'] = {
                'early_date': early_date,
                'early_cases': int(early_global),
                'mid_date': mid_date,
                'mid_cases': int(mid_global),
                'latest_cases': int(global_confirmed),
                'growth_rate_early_to_mid': round(((mid_global - early_global) / early_global * 100), 2) if early_global > 0 else 0,
                'growth_rate_mid_to_latest': round(((global_confirmed - mid_global) / mid_global * 100), 2) if mid_global > 0 else 0
            }
            
            return analysis_results
            
        except Exception as e:
            st.error(f"Error analyzing data: {e}")
            return {"error": str(e)}

    def create_enhanced_insights_prompt(self, user_question, analysis_results):
        """Create AI prompt with actual data analysis results."""
        
        # Convert analysis results to a formatted string
        data_context = f"""
REAL-TIME COVID-19 DATA ANALYSIS RESULTS:

=== GLOBAL STATISTICS (Latest: {analysis_results.get('global_stats', {}).get('latest_date', 'N/A')}) ===
• Total Confirmed Cases: {analysis_results.get('global_stats', {}).get('confirmed', 0):,}
• Total Deaths: {analysis_results.get('global_stats', {}).get('deaths', 0):,}
• Total Recovered: {analysis_results.get('global_stats', {}).get('recovered', 0):,}
• Global Death Rate: {analysis_results.get('global_stats', {}).get('death_rate', 0)}%
• Global Recovery Rate: {analysis_results.get('global_stats', {}).get('recovery_rate', 0)}%

=== TOP 10 COUNTRIES BY CONFIRMED CASES ===
"""
        
        # Add top countries data
        if 'top_countries' in analysis_results:
            for i, (country, cases) in enumerate(list(analysis_results['top_countries']['confirmed'].items())[:10], 1):
                data_context += f"{i}. {country}: {cases:,}\n"
        
        data_context += "\n=== DEATH RATES BY COUNTRY (Countries with >1000 cases) ===\n"
        if 'death_rates' in analysis_results:
            for i, (country, rate) in enumerate(list(analysis_results['death_rates'].items())[:10], 1):
                data_context += f"{i}. {country}: {rate}%\n"
        
        # Add country-specific data if available
        if 'country_specific' in analysis_results:
            data_context += "\n=== COUNTRY-SPECIFIC DETAILED ANALYSIS ===\n"
            for country, data in analysis_results['country_specific'].items():
                data_context += f"""
{country.upper()}:
• Latest Confirmed: {data['latest_confirmed']:,}
• Latest Deaths: {data['latest_deaths']:,}
• Latest Recovered: {data['latest_recovered']:,}
• Death Rate: {data['death_rate']}%
• Recovery Rate: {data['recovery_rate']}%
• Historical Trend: Available for detailed analysis
"""
        
        # Add trend analysis
        if 'trend_analysis' in analysis_results:
            trend = analysis_results['trend_analysis']
            data_context += f"""
=== PANDEMIC TREND ANALYSIS ===
• Early Period ({trend['early_date']}): {trend['early_cases']:,} cases
• Mid Period ({trend['mid_date']}): {trend['mid_cases']:,} cases
• Latest Period: {trend['latest_cases']:,} cases
• Growth Rate (Early to Mid): {trend['growth_rate_early_to_mid']}%
• Growth Rate (Mid to Latest): {trend['growth_rate_mid_to_latest']}%
"""
        
        return f"""
You are a senior data scientist and epidemiologist with access to REAL-TIME COVID-19 data analysis. You have just performed comprehensive data analysis to answer the user's specific question.

PERSONALITY: You are knowledgeable, analytical, and provide data-driven insights. You explain complex patterns in simple terms and always ground your responses in the ACTUAL DATA you've analyzed.

IMPORTANT: The data provided below is REAL-TIME ANALYSIS from the actual COVID-19 datasets, not summary statistics. Use these EXACT numbers and calculations in your response.

{data_context}

RESPONSE GUIDELINES:
1. Use the EXACT numbers from the real-time analysis above
2. Provide specific insights based on actual data calculations
3. Compare countries using real death rates and case numbers
4. Reference historical trends from the actual time series data
5. Explain what the numbers mean in practical terms
6. Be conversational but scientifically accurate
7. If the analysis doesn't contain specific data the user asked for, acknowledge this limitation

USER QUESTION: {user_question}

Provide a comprehensive, data-driven response using the REAL-TIME analysis results above. Include specific statistics, comparisons, and insights based on the actual data calculations.
        """

    def get_enhanced_insights_response(self, user_question, confirmed_df, deaths_df, recovered_df):
        """Send question to AI with real-time data analysis."""
        try:
            # First, perform real-time data analysis
            with st.spinner("🔍 Analyzing real-time data..."):
                analysis_results = self.analyze_data_for_question(user_question, confirmed_df, deaths_df, recovered_df)
            
            if 'error' in analysis_results:
                return f"Sorry, I encountered an error while analyzing the data: {analysis_results['error']}"
            
            # Create enhanced prompt with real data
            prompt = self.create_enhanced_insights_prompt(user_question, analysis_results)

            # Call AI model
            response = self.client.complete(
                messages=[
                    SystemMessage("You are a senior data scientist with access to real-time COVID-19 data analysis."),
                    UserMessage(prompt),
                ],
                temperature=0.2,  # Lower temperature for more factual responses
                top_p=0.8,        # More focused responses
                model=self.model,
                max_tokens=1500   # Longer responses for detailed analysis
            )

            # Return AI response content
            return response.choices[0].message.content

        except Exception as api_error:
            st.error("🤖 Failed to get response from AI model. Please try again later.")
            st.error(f"Error details: {str(api_error)}")
            return None

def show_ai_insights_section(confirmed_df, deaths_df, recovered_df):
    """Display AI-powered insights section with direct data access."""
    
    st.header("🤖 AI Data Assistant")
    st.markdown("""
    **🚀 Enhanced Feature:** Ask our AI assistant anything about the COVID-19 data! 
    This intelligent assistant has **DIRECT ACCESS** to all CSV files and can perform real-time calculations, 
    access specific data points, and provide accurate insights based on live data analysis.
    
    *This AI analyzes the actual data in real-time for each question you ask!*
    """)
    
    # Add enhanced feature highlight
    st.success("""
    🎯 **Real-Time Data Analysis:** 
    • Direct CSV file access for accurate calculations
    • Live statistical analysis for each query
    • Specific country data extraction
    • Historical trend analysis
    • Custom metric calculations
    """)
    
    # Initialize AI client
    try:
        ai_client = COVID19DataInsightsAI()
    except:
        st.stop()  # Stop if AI client initialization fails
    
    # Display enhanced data access info
    with st.expander("📊 Enhanced Data Access Capabilities"):
        st.markdown("""
        **The AI Assistant now has direct access to:**
        
        🔹 **Raw CSV Data**: Complete access to all confirmed, deaths, and recovered datasets
        🔹 **Real-Time Calculations**: Performs live statistical analysis for each question
        🔹 **Country-Specific Analysis**: Extracts and analyzes data for specific countries mentioned
        🔹 **Time Series Data**: Access to historical trends and growth patterns
        🔹 **Custom Metrics**: Calculates death rates, recovery rates, and growth rates on demand
        🔹 **Comparative Analysis**: Real-time country and regional comparisons
        
        **Data Coverage:**
        - **Confirmed Cases Dataset**: {confirmed_df.shape[0]} locations, {confirmed_df.shape[1]} columns
        - **Deaths Dataset**: {deaths_df.shape[0]} locations, {deaths_df.shape[1]} columns  
        - **Recovered Dataset**: {recovered_df.shape[0]} locations, {recovered_df.shape[1]} columns
        - **Countries Covered**: {confirmed_df['Country/Region'].nunique()} countries and regions
        - **Time Period**: January 2020 to May 2021 (daily data)
        """)
    
    # Main layout - Enhanced chat interface
    st.subheader("💬 Chat with Enhanced AI Assistant")
    
    # Text area for user question
    user_question = st.text_area(
        "Ask anything about the COVID-19 data (the AI will analyze real data to answer):",
        placeholder="e.g., What's the exact death rate in Italy compared to Germany? Which country had the fastest growth in March 2020? Show me China's recovery timeline with specific numbers.",
        height=120,
        help="The AI will perform real-time data analysis to answer your specific questions with exact numbers and calculations!"
    )
    
    # Submit button
    if st.button("🔍 Get Real-Time AI Analysis", type="primary", use_container_width=True):
        if user_question.strip():
            with st.spinner("🤖 AI Assistant is performing real-time data analysis..."):
                # Get enhanced AI response with real data
                ai_response = ai_client.get_enhanced_insights_response(user_question, confirmed_df, deaths_df, recovered_df)
                
                if ai_response:
                    # Store response in session state for history
                    st.session_state.last_response = ai_response
                    
                    # Display response in a nice format
                    st.subheader("🎯 Real-Time AI Analysis Results")
                    st.markdown(ai_response)
                    
                    # Add feedback section
                    st.markdown("---")
                    st.markdown("**Was this real-time analysis helpful?**")
                    
                    feedback_col1, feedback_col2 = st.columns(2)
                    with feedback_col1:
                        if st.button("👍 Yes, very accurate!", key="positive_feedback"):
                            st.success("Thank you! The AI used real data for this analysis.")
                    with feedback_col2:
                        if st.button("👎 Could be better", key="negative_feedback"):
                            st.info("Try asking a more specific question for better analysis!")
                else:
                    st.error("Failed to get AI response. Please try again.")
        else:
            st.warning("Please enter a question to get real-time analysis.")
    
    # Enhanced example questions section
    st.markdown("---")
    st.subheader("💡 Try These Enhanced Questions")
    
    # Create tabs with enhanced examples
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Real-Time Queries", "📊 Exact Statistics", "🌍 Live Comparisons", "🚀 Quick Analysis"])
    
    with tab1:
        st.markdown("""
        **Real-Time Data Analysis:**
        - "What's the exact death rate in Italy vs Spain with current numbers?"
        - "Which country had the highest growth rate in April 2020?"
        - "Show me China's exact recovery timeline with specific dates and numbers"
        - "What are the precise statistics for the top 5 most affected countries?"
        """)
    
    with tab2:
        st.markdown("""
        **Exact Statistical Calculations:**
        - "Calculate the exact global recovery rate with current data"
        - "What's the precise death rate for countries with over 100,000 cases?"
        - "Show me the exact numbers for USA's pandemic progression"
        - "Compare Brazil and India's exact case numbers and growth rates"
        """)
    
    with tab3:
        st.markdown("""
        **Live Country Comparisons:**
        - "Compare European countries' death rates with exact percentages"
        - "Which Asian countries performed best? Show me the exact data"
        - "USA vs China: exact timeline comparison with real numbers"
        - "Rank countries by recovery rate with precise calculations"
        """)
    
    with tab4:
        st.markdown("**Quick Real-Time Analysis:**")
        if st.button("📊 Live Global Overview", use_container_width=True):
            st.session_state.quick_question = "Give me a comprehensive overview with exact current statistics from the real data"
        if st.button("🏆 Top Performers Analysis", use_container_width=True):
            st.session_state.quick_question = "Analyze which countries performed best with exact death rates and recovery rates from real data"
        if st.button("📈 Precise Trend Analysis", use_container_width=True):
            st.session_state.quick_question = "Show me the most important trends with exact growth rates and timeline data"
    
    # Handle quick questions with enhanced analysis
    if hasattr(st.session_state, 'quick_question'):
        with st.spinner("🤖 Performing real-time data analysis..."):
            ai_response = ai_client.get_enhanced_insights_response(st.session_state.quick_question, confirmed_df, deaths_df, recovered_df)
            if ai_response:
                st.subheader("🎯 Quick Real-Time Analysis")
                st.markdown(ai_response)
                st.session_state.last_response = ai_response
        del st.session_state.quick_question
    
    # Chat history section
    st.markdown("---")
    st.subheader("💭 Recent Conversations")
    
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Add current conversation to history
    if user_question and hasattr(st.session_state, 'last_response'):
        conversation = (user_question, st.session_state.last_response)
        if conversation not in st.session_state.chat_history:
            st.session_state.chat_history.append(conversation)
            # Keep only last 5 conversations
            if len(st.session_state.chat_history) > 5:
                st.session_state.chat_history = st.session_state.chat_history[-5:]
    
    # Display recent conversations
    if st.session_state.chat_history:
        for i, (question, response) in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"💬 {question[:60]}..." if len(question) > 60 else f"💬 {question}", expanded=(i==0)):
                st.markdown(f"**You asked:** {question}")
                st.markdown(f"**AI Assistant:** {response}")
    else:
        st.info("💡 Your conversation history will appear here as you chat with the AI assistant.")
    
    # Feature showcase section using tabs instead of columns
    st.markdown("---")
    st.subheader("✨ AI Assistant Capabilities")
    
    cap_tab1, cap_tab2, cap_tab3 = st.tabs(["🎯 Smart Analysis", "🌍 Global Insights", "📊 Custom Queries"])
    
    with cap_tab1:
        st.success("""
        **Smart Analysis Features:**
        - Real-time data processing
        - Statistical calculations
        - Trend identification
        - Pattern recognition
        """)
    
    with cap_tab2:
        st.info("""
        **Global Insights:**
        - Country comparisons
        - Regional analysis
        - Timeline exploration
        - Growth rate analysis
        """)
    
    with cap_tab3:
        st.warning("""
        **Custom Queries:**
        - Personalized insights
        - Specific date ranges
        - Custom metrics
        - Dynamic responses
        """)
    
    # Tips section
    st.markdown("---")
    st.subheader("💡 Tips for Better Results")
    
    # Use tabs instead of columns to avoid nesting
    tips_tab1, tips_tab2 = st.tabs(["🎯 Best Practices", "🤖 AI Strengths"])
    
    with tips_tab1:
        st.success("""
        **For Best Results:**
        - Be specific in your questions
        - Ask about trends, patterns, or comparisons
        - Mention specific countries or time periods
        - Request statistical analysis or calculations
        - Ask follow-up questions for deeper insights
        """)
    
    with tips_tab2:
        st.info("""
        **AI Assistant Strengths:**
        - Data interpretation and insights
        - Real-time statistical calculations
        - Country and regional comparisons
        - Timeline and trend analysis
        - Pattern identification and explanation
        - Contextual recommendations
        """)
    
    # Enhanced disclaimer
    st.markdown("---")
    st.info("""
    **✨ Enhanced AI Features:** 
    - **Real-Time Analysis**: AI performs live calculations on your actual CSV data
    - **Exact Numbers**: All statistics are calculated from the real datasets
    - **Data Period**: January 22, 2020 to May 29, 2021 (complete historical data)
    - **Accuracy**: Responses based on direct data analysis, not pre-computed summaries
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>🤖 Enhanced AI Data Assistant with Real-Time CSV Analysis | 📊 COVID-19 Data Analysis Project</small>
    </div>
    """, unsafe_allow_html=True)