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

paragraph_text = 'Explore real-time and historical electricity prices in different regions of Norway. From the sidebar select your area and your preferred currency to analyze energy costs.'

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
    #title=f"Electricity prices for {selected_price_area} on {current_date.strftime('%Y-%m-%d')}",
    xaxis_title="Time",
    yaxis_title=f"{currency} per kWh",
    autosize=True,  # Set autosize to True for responsiveness
)

# Display dynamic information
if currency == 'NOK':
    current_price = all_data.iloc[-1]["NOK_per_kWh"]
else:
    current_price = all_data.iloc[-1]["EUR_per_kWh"]

#From df dataframe select the current price using current_date. 
current_price = round(all_data[all_data['time_start'].str.contains(current_date.strftime("%H"), case=False, na=False)][currency_column].values[0],5)

# Display the current price
st.markdown(f"The electricity price in <strong>{price_area}</strong> is now <strong>{current_price} {currency}</strong> per kWh.", unsafe_allow_html=True)
st.markdown("Today's data is accessed in real time via the API of our data source")

# Display the chart using st.plotly_chart
st.plotly_chart(fig)


#Prepare data for second chart

# Load the dataset from the CSV file
historical_prices_data = pd.read_csv('strompriser_dataset.csv')

#Convert the 'time_start' and 'time_end' columns to datetime objects
historical_prices_data['time_start'] = pd.to_datetime(historical_prices_data['time_start'], utc = True)
historical_prices_data['time_end'] = pd.to_datetime(historical_prices_data['time_end'], utc = True)

# Extract the date portion from 'time_start'
historical_prices_data['date'] = historical_prices_data['time_start'].dt.date

# Group by 'area' and 'date', and calculate the mean of NOK and EUR prices
daily_historical_prices = historical_prices_data.groupby(['area', 'date'])[['NOK_per_kWh', 'EUR_per_kWh']].mean().reset_index()

# Streamlit app title and header
st.header("Historical Daily Prices Chart")

# Display today's average price
today_average_price = round(all_data[currency_column].mean(),5)
st.markdown(f"The average electricity price of today in <strong>{price_area}</strong> is <strong>{today_average_price} {currency}</strong> per kWh.", unsafe_allow_html=True)
st.markdown("Historical data is updated daily at 23:00 UTC by a GitHub workflow running daily and is stored in the [GitHub repository](https://github.com/datadej/norway-electricity-prices) of this dashboard")


# Create a line chart for historical daily prices using Plotly Graph Objects
fig = go.Figure()

# Iterate through unique areas and create a line for each
for area in daily_historical_prices['area'].unique():
    area_data = daily_historical_prices[daily_historical_prices['area'] == area]
    
    # Get the label for the area using price_area_mapping
    label = [key for key, value in price_area_mapping.items() if value == area][0]
    
    # Add a trace with the label
    fig.add_trace(go.Scatter(x=area_data['date'], y=area_data[currency_column], mode='lines', name=label))

# Customize the layout of the chart
fig.update_layout(
    #title="Historical Daily Electricity Prices",
    xaxis_title="Date",
    yaxis_title=f"{currency} per kWH",
)

# Display the historical daily prices chart using st.plotly_chart
st.plotly_chart(fig)

# Add a footer link to the data source
st.sidebar.markdown('Data Provided by:')
st.sidebar.markdown('<p><a href="https://www.hvakosterstrommen.no/strompris-api"><img src="https://ik.imagekit.io/ajdfkwyt/hva-koster-strommen/strompriser-levert-av-hvakosterstrommen_oTtWvqeiB.png" alt="Electricity Prices Source: Hva koster strømmen.no" width="200" height="45"></a></p>', unsafe_allow_html=True)

