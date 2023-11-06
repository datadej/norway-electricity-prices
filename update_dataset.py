import requests
import pandas as pd
from datetime import datetime, timedelta

# Define the URL pattern for the API
base_url = "https://www.hvakosterstrommen.no/api/v1/prices/{year}/{date}_{area}.json"

# Define the list of areas
areas = ["NO1", "NO2", "NO3", "NO4", "NO5"]

# Define the range of years and start date
current_date = datetime.now()
formatted_date = datetime.now().strftime("%m-%d")

# Initialize an empty list to store the data
all_data = []


for area in areas:
    # Create the URL for the current date and area
    url = base_url.format(year=current_date.year, date=formatted_date, area=area)

    # Make a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Add the data to the list with the area information
        for entry in data:
            entry["area"] = area
        all_data.extend(data)
    else:
        print(f"Failed to fetch data for {url}")

# Convert the list of data into a pandas DataFrame
df = pd.DataFrame(all_data)
df.head()

# Append the DataFrame to an existing CSV file
df.to_csv('strompriser_dataset.csv', mode='a', header=False, index=False)


# Print a message when the process is complete
print("Data retrieval and storage complete.")
