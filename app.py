import streamlit as st
import requests  # For direct API calls
import pandas as pd
import datetime
import plotly.express as px  # Add this line

# Title
st.markdown("<h1 style='color: red; font-weight: bold;'>Asia Economic Tracker Dashboard</h1>", unsafe_allow_html=True)

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

# Research Note Section
st.markdown("---")
st.subheader("Research Note")
st.write("Download the full research note on macroeconomic indicators, methodologies, and trends for Asian countries.")

# Absolute path to the PDF
pdf_path = r"C:\Users\Asus1\Desktop\Economic Dashboard\Asian_Macroeconomic_Research_Note.pdf"

try:
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    st.download_button(
        label="Download Research Note PDF",
        data=pdf_data,
        file_name="Asian_Macroeconomic_Research_Note.pdf",
        mime="application/pdf"
    )
except FileNotFoundError:
    st.error(r"PDF file not found. Please ensure 'Asian_Macroeconomic_Research_Note.pdf' is in: C:\Users\Asus1\Desktop\Economic Dashboard")

# Country Comparison Section
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
            # GDP Growth Chart
            if 'GDP Growth (%)' in data.columns:
                st.write("**GDP Growth Rate**")
                fig = px.line(data, x=data.index, y='GDP Growth (%)', title='GDP Growth Rate')
                fig.update_xaxes(type='category')
                st.plotly_chart(fig)
            
            # Inflation Chart
            if 'Inflation (%)' in data.columns:
                st.write("**Inflation Rate**")
                fig = px.line(data, x=data.index, y='Inflation (%)', title='Inflation Rate')
                fig.update_xaxes(type='category')
                st.plotly_chart(fig)
            
            # Unemployment Chart
            if 'Unemployment (%)' in data.columns:
                st.write("**Unemployment Rate**")
                fig = px.bar(data, x=data.index, y='Unemployment (%)', title='Unemployment Rate')
                fig.update_xaxes(type='category')
                st.plotly_chart(fig)
            
            # GDP Value
            if 'GDP (USD)' in data.columns:
                latest_gdp = data['GDP (USD)'].dropna().iloc[-1] if not data['GDP (USD)'].empty else "N/A"
                st.write(f"**Latest GDP (in USD)**: {latest_gdp}")
        else:
            st.write(f"No data available for {country} in the selected period.")
else:
    st.write("Please select exactly two countries to compare.")
            
# Footer
st.write("Data source: World Bank. Refresh the page to update.")
st.markdown("---")  # Adds a horizontal line for separation
st.write("**Created by [Aarchi Goyal]** - Economic tracker Dashboard for Asian Countries. For personal use only.")