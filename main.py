import requests
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Function to get energy prices for a specific date and area
def get_energy_prices_for_date(date, price_area):
    base_url = "https://www.hvakosterstrommen.no/api/v1/prices"
    endpoint = f"{date.year}/{date.strftime('%m')}-{date.strftime('%d')}_{price_area}.json"
    full_url = f"{base_url}/{endpoint}"
    
    response = requests.get(full_url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        st.error(f"Failed to fetch data from {full_url}. Status code: {response.status_code}")
        return None

# Create a Streamlit app
st.title("🇳🇴⚡️ Norway's Electricity Prices")

paragraph_text = 'Explore real-time and historical electricity prices in different regions of Norway. From the sidebar select your area, customize your date range, and choose your preferred currency to analyze energy costs.'

st.markdown(f'<span style="font-size: 18px;">{paragraph_text}</span>', unsafe_allow_html=True)

st.header("Today's Hourly Prices Chart")

# Area selection in the sidebar
price_area = st.sidebar.selectbox("Select Area", ["NO1 - Oslo / Øst-Norge", "NO2 - Kristiansand / Sør-Norge", "NO3 - Trondheim / Midt-Norge", "NO4 - Tromsø / Nord-Norge", "NO5 - Bergen / Vest-Norge"])
price_area_mapping = {
    "NO1 - Oslo / Øst-Norge": "NO1",
    "NO2 - Kristiansand / Sør-Norge": "NO2",
    "NO3 - Trondheim / Midt-Norge": "NO3",
    "NO4 - Tromsø / Nord-Norge": "NO4",
    "NO5 - Bergen / Vest-Norge": "NO5"
}
selected_price_area = price_area_mapping[price_area]

# Use the current date for the API query
current_date = datetime.now()

# Fetch and accumulate data for the current date and selected price area
@st.cache(allow_output_mutation=True)
def fetch_data(current_date, selected_price_area):
    date_range = pd.date_range(start=current_date, periods=1, freq='H')
    data_frames = []
    for date in date_range:
        data_frame = get_energy_prices_for_date(date, selected_price_area)
        if data_frame is not None:
            data_frames.append(data_frame)
    return pd.concat(data_frames)

all_data = fetch_data(current_date, selected_price_area)

# User selects the currency in the sidebar
currency = st.sidebar.selectbox('Select Currency', ['NOK', 'EUR'])
currency_mapping = {
    'NOK': 'NOK_per_kWh',
    'EUR': 'EUR_per_kWh',
}
currency_column = currency_mapping[currency]

# Create a responsive line chart for hourly prices using Plotly Graph Objects
fig = go.Figure()

# Add the line chart trace
fig.add_trace(go.Scatter(x=all_data['time_start'], y=all_data[currency_column], mode='lines', line_shape='hv', name='Hourly Prices'))

# Update the layout to make the chart responsive
fig.update_layout(
    title=f"Electricity prices for {selected_price_area} on {current_date.strftime('%Y-%m-%d')}",
    xaxis_title="Time",
    yaxis_title=f"{currency} per kWh",
    autosize=True,  # Set autosize to True for responsiveness
)

# Display the chart using st.plotly_chart
st.plotly_chart(fig)

# Display dynamic information
if currency == 'NOK':
    current_price = all_data.iloc[-1]["NOK_per_kWh"]
else:
    current_price = all_data.iloc[-1]["EUR_per_kWh"]

st.markdown(f"The current price for <strong>{price_area}</strong> on {current_date.strftime('%Y-%m-%d')} is <strong>{current_price} {currency}</strong> per kWh.", unsafe_allow_html=True)

# Add a new section for the historical prices chart
st.header("Historical Prices Chart")

# Load the dataset from the CSV file
historical_prices_data = pd.read_csv('strompriser_dataset.csv')

# Convert the 'time_start' and 'time_end' columns to datetime objects
historical_prices_data['time_start'] = pd.to_datetime(historical_prices_data['time_start'])
historical_prices_data['time_end'] = pd.to_datetime(historical_prices_data['time_end'])

# Find the earliest 'time_start' in the dataset
earliest_time_start = historical_prices_data['time_start'].min().strftime('%Y-%m-%d')

# Find the latest 'time_end' in the dataset
latest_time_end = historical_prices_data['time_end'].max().strftime('%Y-%m-%d')

# Create a dictionary to map area codes to their meanings
area_mapping = {
    'NO1': 'Oslo / Øst-Norge',
    'NO2': 'Kristiansand / Sør-Norge',
    'NO3': 'Trondheim / Midt-Norge',
    'NO4': 'Tromsø / Nord-Norge',
    'NO5': 'Bergen / Vest-Norge'
}

# Map the area codes to their meanings in the DataFrame
historical_prices_data['area'] = historical_prices_data['area'].map(area_mapping)

# Create a line chart for historical hourly prices using Plotly Express
historical_prices_chart = px.line(historical_prices_data, x='time_start', y=currency_column, color='area',
                                  title=f"Historical Hourly Prices from {earliest_time_start} until {latest_time_end}",
                                  labels={"area": "Area"})
historical_prices_chart.update_xaxes(title_text="Time")
historical_prices_chart.update_yaxes(title_text=f"{currency} per kWh")

# Display the historical prices chart using st.plotly_chart
st.plotly_chart(historical_prices_chart)

# Add a footer link to the data source
st.sidebar.markdown('<div style="text-align: center;">Data source API: <a href="https://www.hvakosterstrommen.no/strompris-api">hvakosterstrommen.no</a></div>', unsafe_allow_html=True)
# Add a dummy st.markdown element at the end of the sidebar
st.sidebar.markdown('')  # This element doesn't do anything

