# Norway's Electricity Prices Dashboard

This Streamlit web application allows users to explore real-time and historical electricity prices in different regions of Norway. Users can select their preferred area, customize the date range, and choose their desired currency to analyze energy costs.

## Data Retrieval

The app retrieves electricity price data from the [hvakosterstrommen.no API](https://www.hvakosterstrommen.no/strompris-api). It fetches hourly price data for a specific date and area by making API requests and handles the data using the Pandas library. The user selects their area of interest, and the app fetches the price data for that area.

The `get_energy_prices_for_date` function fetches data for a specific date and area from the API. If the API request is successful, it creates a Pandas DataFrame with the retrieved data.

## User Interaction

### Area Selection
Users can choose their area of interest from the sidebar. The available areas are:
- Oslo / Øst-Norge (NO1)
- Kristiansand / Sør-Norge (NO2)
- Trondheim / Midt-Norge (NO3)
- Tromsø / Nord-Norge (NO4)
- Bergen / Vest-Norge (NO5)

### Date Range Selection
Users can customize their date range by selecting a start date and end date. The app ensures that the start date is before or the same as the end date to prevent errors.
The default start and end dates are the current user date, so a minimal amount of API calls is made.

### Currency Selection
Users can choose between Norwegian Krone (NOK) and Euro (EUR) as their preferred currency. The app allows users to view electricity prices in their selected currency.

## Data Handling and Caching

The app efficiently manages data by caching it with the `@st.cache` decorator. It accumulates data for the selected date range, combining data from multiple API requests into a single Pandas DataFrame. This approach improves performance by reducing redundant API calls for overlapping date ranges.

## Charting

The app uses the Plotly Graph Objects library to create a responsive line chart displaying hourly electricity prices. The chart's title reflects the selected date range. Users can visualize how electricity prices fluctuate over time in their chosen area.

## Dynamic Information

The app displays dynamic information about the current electricity price for the selected area and currency. As users change their currency preference, the app updates the current price accordingly.

## Data Source

The data used in this app is sourced from the [hvakosterstrommen.no API](https://www.hvakosterstrommen.no/strompris-api).

Explore electricity prices in Norway, gain insights into historical data, and stay informed about the current electricity prices in your preferred region using this interactive dashboard.