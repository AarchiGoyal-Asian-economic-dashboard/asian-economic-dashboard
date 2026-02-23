import streamlit as st
import requests  # For direct API calls
import pandas as pd
import datetime
import plotly.express as px  # Add this line

# Title
st.markdown("<h1 style='color: red; font-weight: bold;'>Asian Economic Tracker Dashboard</h1>", unsafe_allow_html=True)

# Select countries (expanded list)
countries = {
    'China': 'CHN',
    'India': 'IND',
    'Japan': 'JPN',
    'South Korea': 'KOR',
    'Indonesia': 'IDN',
    'Thailand': 'THA',
    'Vietnam': 'VNM',
    'Philippines': 'PHL',
    'Malaysia': 'MYS',
    'Singapore': 'SGP',
    'Pakistan': 'PAK',
    'Bangladesh': 'BGD',
    'Sri Lanka': 'LKA',
    'Myanmar': 'MMR',
    'Cambodia': 'KHM',
    'Laos': 'LAO',
    'Nepal': 'NPL',
    'Bhutan': 'BTN',
    'Maldives': 'MDV',
    'Brunei': 'BRN',
    'Timor-Leste': 'TLS',
    'Mongolia': 'MNG',
    'Kazakhstan': 'KAZ',
    'Kyrgyzstan': 'KGZ',
    'Tajikistan': 'TJK',
    'Turkmenistan': 'TKM',
    'Uzbekistan': 'UZB'
}
selected_country = st.selectbox("Select a country:", list(countries.keys()))
# Date range options (5-year intervals starting from 2000)
date_ranges = {
    '2000-2005': (2000, 2005),
    '2005-2010': (2005, 2010),
    '2010-2015': (2010, 2015),
    '2015-2020': (2015, 2020),
    '2020-2025': (2020, 2025)
}
selected_range = st.selectbox("Select date range:", list(date_ranges.keys()))
start_year, end_year = date_ranges[selected_range]

# Define indicators (World Bank codes for metrics)
indicators = {
    'NY.GDP.MKTP.KD.ZG': 'GDP Growth (%)',  # Annual GDP growth
    'FP.CPI.TOTL.ZG': 'Inflation (%)',      # Inflation rate
    'SL.UEM.TOTL.ZS': 'Unemployment (%)',   # Unemployment rate
    'NY.GDP.MKTP.CD': 'GDP (USD)'           # GDP in USD (for scale)
}

# Function to fetch data from World Bank API
@st.cache_data
def fetch_world_bank_data(country_code, indicator_code, start_year=2000, end_year=2025):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&date={start_year}:{end_year}&per_page=1000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1 and data[1]:
            df = pd.DataFrame(data[1])
            df['date'] = pd.to_datetime(df['date'])
            df['date'] = df['date'].dt.year.astype(int)  # Convert to integer year
            df = df.set_index('date')
            df.index.name = 'year'  # Rename index to 'year' for tooltips
            df = df[['value']].rename(columns={'value': indicators[indicator_code]})
            return df
    return pd.DataFrame()  # Empty if no data

# Fetch data for the selected country
country_code = countries[selected_country]
data_frames = []
for indicator_code in indicators:
    df = fetch_world_bank_data(country_code, indicator_code, start_year, end_year)
    if not df.empty:
        data_frames.append(df)

# Combine all data into one DataFrame
if data_frames:
    data = pd.concat(data_frames, axis=1).sort_index()
else:
    data = pd.DataFrame()

# Display data if available
if not data.empty:
    st.subheader(f"Economic Data for {selected_country}")
    
    # GDP Growth Chart
    if 'GDP Growth (%)' in data.columns:
        st.write("**GDP Growth Rate**")
        fig = px.line(data, x=data.index, y='GDP Growth (%)', title='GDP Growth Rate', line_shape='linear', color_discrete_sequence=['darkblue'])
fig.update_layout(xaxis=dict(tickfont=dict(color='black')), yaxis=dict(tickfont=dict(color='black')))
fig.update_xaxes(type='category')  # This keeps years as plain text without commas
st.plotly_chart(fig)
    
    # Inflation Chart
if 'Inflation (%)' in data.columns:
    st.write("**Inflation Rate**")
    fig = px.line(data, x=data.index, y='Inflation (%)', title='Inflation Rate', line_shape='linear', color_discrete_sequence=['darkgreen'])
fig.update_layout(xaxis=dict(tickfont=dict(color='black')), yaxis=dict(tickfont=dict(color='black')))
fig.update_xaxes(type='category')
st.plotly_chart(fig)

# Unemployment Chart
if 'Unemployment (%)' in data.columns:
    st.write("**Unemployment Rate**")
    fig = px.bar(data, x=data.index, y='Unemployment (%)', title='Unemployment Rate', color_discrete_sequence=['saddlebrown'])  # Dark brown
fig.update_layout(xaxis=dict(tickfont=dict(color='black')), yaxis=dict(tickfont=dict(color='black')))
fig.update_xaxes(type='category')
st.plotly_chart(fig)

# GDP Value (as a number)
if 'GDP (USD)' in data.columns:
    latest_gdp = data['GDP (USD)'].dropna().iloc[-1] if not data['GDP (USD)'].empty else "N/A"
    st.write(f"**Latest GDP (in USD)**: {latest_gdp}")
else:
    st.write(f"No data available for {selected_country} in the selected period. Try another country or check World Bank for details.")

# ============================================
# COUNTRY COMPARISON SECTION
# ============================================
st.markdown("---")
st.subheader("Compare Two Countries")

selected_countries = st.multiselect("Select two countries to compare:", list(countries.keys()), max_selections=2)

if len(selected_countries) == 2:
    for country in selected_countries:
        st.write(f"### Data for {country}")
        country_code = countries[country]
        
        # Fetch data for the selected country and date range
        data_frames = []
        for indicator_code in indicators:
            df = fetch_world_bank_data(country_code, indicator_code, start_year, end_year)
            if not df.empty:
                data_frames.append(df)
        
        # Combine data
        if data_frames:
            data = pd.concat(data_frames, axis=1).sort_index()
        else:
            data = pd.DataFrame()
        
        # Display charts if data available
        if not data.empty:
            # GDP Growth Chart (Dark Blue)
            if 'GDP Growth (%)' in data.columns:
                st.write("**GDP Growth Rate**")
                fig = px.line(data, x=data.index, y='GDP Growth (%)', title='GDP Growth Rate',
                             line_shape='linear', color_discrete_sequence=['darkblue'])
                fig.update_xaxes(type='category')
                fig.update_layout(xaxis=dict(tickfont=dict(color='black')), 
                                 yaxis=dict(tickfont=dict(color='black')))
                st.plotly_chart(fig)
            
            # Inflation Chart (Dark Green)
            if 'Inflation (%)' in data.columns:
                st.write("**Inflation Rate**")
                fig = px.line(data, x=data.index, y='Inflation (%)', title='Inflation Rate',
                             line_shape='linear', color_discrete_sequence=['darkgreen'])
                fig.update_xaxes(type='category')
                fig.update_layout(xaxis=dict(tickfont=dict(color='black')), 
                                 yaxis=dict(tickfont=dict(color='black')))
                st.plotly_chart(fig)
            
            # Unemployment Chart (Dark Brown)
            if 'Unemployment (%)' in data.columns:
                st.write("**Unemployment Rate**")
                fig = px.bar(data, x=data.index, y='Unemployment (%)', title='Unemployment Rate',
                             color_discrete_sequence=['saddlebrown'])
                fig.update_xaxes(type='category')
                fig.update_layout(xaxis=dict(tickfont=dict(color='black')), 
                                 yaxis=dict(tickfont=dict(color='black')))
                st.plotly_chart(fig)
        else:
            st.write(f"No data available for {country} in the selected period.")
else:
    st.write("Please select exactly two countries to compare.")

# ============================================
# NEW SECTION: Full Country Analysis (2000-2025)
# ============================================
st.markdown("---")
st.subheader("Full Country Analysis (2000-2025)")

st.write("Select a country to view complete macroeconomic indicators from 2000 to 2025.")

# Country selection for full analysis
selected_country_full = st.selectbox("Select a country for full analysis:", list(countries.keys()))

if selected_country_full:
    country_code_full = countries[selected_country_full]
    
    # Fetch data for 2000-2025 (full period)
    data_frames_full = []
    for indicator_code in indicators:
        df = fetch_world_bank_data(country_code_full, indicator_code, 2000, 2025)
        if not df.empty:
            data_frames_full.append(df)
    
    # Combine data
    if data_frames_full:
        data_full = pd.concat(data_frames_full, axis=1).sort_index()
    else:
        data_full = pd.DataFrame()
    
    # Display charts if data available
    if not data_full.empty:
        st.write(f"### Economic Data for {selected_country_full} (2000-2025)")
        
        # GDP Growth Chart
        if 'GDP Growth (%)' in data_full.columns:
            st.write("**GDP Growth Rate (2000-2025)**")
            fig = px.line(data_full, x=data_full.index, y='GDP Growth (%)', 
                         title=f'GDP Growth Rate for {selected_country_full} (2000-2025)',
                         line_shape='linear', color_discrete_sequence=['darkblue'])
            fig.update_xaxes(type='category', title='Year')
            fig.update_yaxes(title='GDP Growth (%)')
            fig.update_layout(xaxis=dict(tickfont=dict(color='black')), 
                             yaxis=dict(tickfont=dict(color='black')))
            st.plotly_chart(fig)
        
        # Inflation Chart
        if 'Inflation (%)' in data_full.columns:
            st.write("**Inflation Rate (2000-2025)**")
            fig = px.line(data_full, x=data_full.index, y='Inflation (%)',
                         title=f'Inflation Rate for {selected_country_full} (2000-2025)',
                         line_shape='linear', color_discrete_sequence=['darkgreen'])
            fig.update_xaxes(type='category', title='Year')
            fig.update_yaxes(title='Inflation (%)')
            fig.update_layout(xaxis=dict(tickfont=dict(color='black')), 
                             yaxis=dict(tickfont=dict(color='black')))
            st.plotly_chart(fig)
        
        # Unemployment Chart
        if 'Unemployment (%)' in data_full.columns:
            st.write("**Unemployment Rate (2000-2025)**")
            fig = px.bar(data_full, x=data_full.index, y='Unemployment (%)',
                         title=f'Unemployment Rate for {selected_country_full} (2000-2025)',
                         color_discrete_sequence=['saddlebrown'])
            fig.update_xaxes(type='category', title='Year')
            fig.update_yaxes(title='Unemployment (%)')
            fig.update_layout(xaxis=dict(tickfont=dict(color='black')), 
                             yaxis=dict(tickfont=dict(color='black')))
            st.plotly_chart(fig)
        
        # GDP Value
        if 'GDP (USD)' in data_full.columns:
            latest_gdp_full = data_full['GDP (USD)'].dropna().iloc[-1] if not data_full['GDP (USD)'].dropna().empty else "N/A"
            st.write(f"**Latest GDP (in USD)**: {latest_gdp_full}")
        
        # Data Source Note
        st.write("Data source: World Bank. Refresh the page to update.")
    else:
        st.write(f"No data available for {selected_country_full} in the selected period. Try another country or check World Bank for details.")

# Research Note Section
st.markdown("---")
st.subheader("Research Note")
st.write("Download the full research note on macroeconomic indicators, methodologies, and trends for Asian countries.")

# Link to PDF on GitHub
pdf_url = "https://github.com/AarchiGoyal-Asian-economic-dashboard/asian-economic-dashboard/raw/main/Asian_Macroeconomic_Research_Note.pdf"  
st.markdown(f"[Download Research Note PDF]({pdf_url})", unsafe_allow_html=True)

# ============================================
# CUMULATIVE COUNTRY ANALYSIS (2000-2025)
# ============================================
st.markdown("---")
st.subheader("Cumulative Country Analysis (2000-2025)")

st.write("Compare aggregate macroeconomic indicators across all Asian countries for the full 25-year period.")

# Create tabs for different indicators (ONLY 3 TABS NOW)
tab1, tab2, tab3 = st.tabs(["GDP Growth", "Inflation", "Unemployment"])

# Fetch and display data for each indicator
with tab1:  # GDP Growth
    st.write("**Average GDP Growth Rate (2000-2025)**")
    gdp_data = []
    for country_name, country_code in countries.items():
        df = fetch_world_bank_data(country_code, 'NY.GDP.MKTP.KD.ZG', 2000, 2025)
        if not df.empty:
            avg_gdp = df['GDP Growth (%)'].mean()
            gdp_data.append({'Country': country_name, 'Average GDP Growth (%)': avg_gdp})
    
    if gdp_data:
        gdp_df = pd.DataFrame(gdp_data)
        gdp_df = gdp_df.sort_values('Average GDP Growth (%)', ascending=False)
        fig = px.bar(gdp_df, x='Country', y='Average GDP Growth (%)', 
                     title='Average GDP Growth Rate (2000-2025)',
                     color='Average GDP Growth (%)',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig)
        
        # Display data table
        st.write("Data Table:")
        st.dataframe(gdp_df)

with tab2:  # Inflation
    st.write("**Average Inflation Rate (2000-2025)**")
    inflation_data = []
    for country_name, country_code in countries.items():
        df = fetch_world_bank_data(country_code, 'FP.CPI.TOTL.ZG', 2000, 2025)
        if not df.empty:
            avg_inflation = df['Inflation (%)'].mean()
            inflation_data.append({'Country': country_name, 'Average Inflation (%)': avg_inflation})
    
    if inflation_data:
        inflation_df = pd.DataFrame(inflation_data)
        inflation_df = inflation_df.sort_values('Average Inflation (%)', ascending=False)
        fig = px.bar(inflation_df, x='Country', y='Average Inflation (%)',
                     title='Average Inflation Rate (2000-2025)',
                     color='Average Inflation (%)',
                     color_continuous_scale='Greens')
        st.plotly_chart(fig)
        
        st.write("Data Table:")
        st.dataframe(inflation_df)

with tab3:  # Unemployment
    st.write("**Average Unemployment Rate (2000-2025)**")
    unemployment_data = []
    for country_name, country_code in countries.items():
        df = fetch_world_bank_data(country_code, 'SL.UEM.TOTL.ZS', 2000, 2025)
        if not df.empty:
            avg_unemployment = df['Unemployment (%)'].mean()
            unemployment_data.append({'Country': country_name, 'Average Unemployment (%)': avg_unemployment})
    
    if unemployment_data:
        unemployment_df = pd.DataFrame(unemployment_data)
        unemployment_df = unemployment_df.sort_values('Average Unemployment (%)', ascending=False)
        fig = px.bar(unemployment_df, x='Country', y='Average Unemployment (%)',
                     title='Average Unemployment Rate (2000-2025)',
                     color='Average Unemployment (%)',
                     color_continuous_scale='Reds')
        st.plotly_chart(fig)
        
        st.write("Data Table:")
        st.dataframe(unemployment_df)

st.write("Note: Data sourced from World Bank API. Averages calculated over 2000-2025 period.") 

# Footer
st.write("Data source: World Bank. Refresh the page to update.")
st.markdown("---")  # Adds a horizontal line for separation
st.write("**Created by [Aarchi Goyal]** - Economic tracker Dashboard for Asian Countries. For personal use only.")