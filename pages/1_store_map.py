import streamlit as st
import folium
import numpy as np
import pandas as pd 
from streamlit_folium import st_folium


# Define your dictionary of Emirate coordinates (replace with actual values)
emirate_coordinates =  {'Abu-Dhabi': [(24.508834, 54.407412), (24.501583, 54.376071), (24.490583, 54.358297), (24.434194, 54.414625), (24.481739, 54.366666)],
                'Dubai': [(25.025879, 55.104579), (25.227130, 55.273139), (25.274845, 55.370970)],
                'Sharjah': [(25.339613, 55.393396), (25.374701, 55.424769)],
                'RAK': [(25.774751, 55.993690)],
                'Ajman': [(25.388345, 55.464602)],
                'UAQ': [(25.514791, 55.556644)],
                'Fujairah': [(25.120179, 56.327506)]}
# Function to calculate average latitude and longitude
def calculate_average_location(coordinates):
    latitude_sum = 0
    longitude_sum = 0
    for lat, lon in coordinates:
        latitude_sum += lat
        longitude_sum += lon
    return [latitude_sum / len(coordinates), longitude_sum / len(coordinates)]

# Streamlit app setup
st.title("UAE Store Locations: Lucas")

st.write("this is using folium and open street map, also this is static page to demonstrate capability")

# Dropdown for choosing an emirate
selected_emirate = st.selectbox("Choose an Emirate", list(emirate_coordinates.keys()))

# Extract chosen emirate's coordinates
chosen_coordinates = emirate_coordinates[selected_emirate]

# Calculate average location
average_location = calculate_average_location(chosen_coordinates)

# Create the map
map = folium.Map(location=average_location, zoom_start=10, tiles='OpenStreetMap') # , tiles='OpenStreetMap') # 'Stamen.Toner')

# Convert coordinates to DataFrames
latitudes = [lat for lat, _ in chosen_coordinates]
longitudes = [lon for _, lon in chosen_coordinates]

data = pd.DataFrame({
    "latitude": latitudes,
    "longitude": longitudes
})

# Plot markers on the map
for i, row in data.iterrows():
    folium.Marker([row["latitude"], row["longitude"]], tooltip=f"Store {i+1}").add_to(map)

st_folium(map, width = 700)
# Display the map in Streamlit
# st.map(data)

