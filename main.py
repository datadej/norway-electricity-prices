import requests
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import altair as alt

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

# Set year, month, and day to the current date
current_date = datetime.now()
year = current_date.year
month = current_date.strftime("%m")
day = current_date.strftime("%d")

# Create a Streamlit app with the sidebar open by default
st.title("Norway's Energy Prices")
st.sidebar.header("Selections")

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

# Date range selection in the sidebar
start_date = st.sidebar.date_input("Select Start Date", value=current_date - timedelta(days=0))
end_date = st.sidebar.date_input("Select End Date", value=current_date)

if start_date > end_date:
    st.error("Start date should be before or the same as the end date.")

# Fetch and accumulate data for the selected date range
@st.cache(allow_output_mutation=True)
def fetch_data(start_date, end_date, selected_price_area):
    date_range = pd.date_range(start=start_date, end=end_date)
    data_frames = []
    for date in date_range:
        data_frame = get_energy_prices_for_date(date, selected_price_area)
        if data_frame is not None:
            data_frames.append(data_frame)
    return pd.concat(data_frames)

all_data = fetch_data(start_date, end_date, selected_price_area)

# Create a line chart for hourly prices
chart = alt.Chart(all_data).mark_line().encode(
    x=alt.X('time_start:T', title="Time"),
    y=alt.Y(st.sidebar.selectbox("Select Currency", ["NOK_per_kWh", "EUR_per_kWh"]), title="Price per kWh"),
    tooltip=["time_start:T", "NOK_per_kWh:Q", "EUR_per_kWh:Q"]
).properties(
    width=800,
    height=400,
    title="Hourly Prices"
)

# Display the chart
st.altair_chart(chart)


#Add footer lik to data source
# Create a footer at the bottom of the sidebar
st.sidebar.markdown('<div style="text-align: center;">Data source API: <a href="https://www.hvakosterstrommen.no/strompris-api">hvakosterstrommen.no</a></div>', unsafe_allow_html=True)
st.sidebar.markdown('<p><a href="https://www.hvakosterstrommen.no"><img src="https://ik.imagekit.io/ajdfkwyt/hva-koster-strommen/strompriser-levert-av-hvakosterstrommen_oTtWvqeiB.png" alt="Strømpriser levert av Hva koster strømmen.no" width="200" height="45"></a></p>')