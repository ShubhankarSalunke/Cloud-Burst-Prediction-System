import streamlit as st
import requests
import pandas as pd
import json
import joblib
from streamlit_option_menu import option_menu

with open(r"state_city.json", "r") as f:
    states_and_cities = json.load(f)

for state, cities in states_and_cities.items():
    unique_cities = sorted(set(cities))
    states_and_cities[state] = unique_cities

sorted_states = sorted(states_and_cities.keys())


landslide_model_path = r"landslide_predictor_model.pkl"
with open(landslide_model_path, "rb") as f:
    landslide_model = joblib.load(f)

cloudburst_model_path = r"random_forest_model.pkl"
with open(cloudburst_model_path, "rb") as f:
    cloudburst_model = joblib.load(f)


def get_weather(city_name, api_key):
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city_name, "aqi": "yes"}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "temperature_celsius": data["current"]["temp_c"],
            "precip_mm": data["current"]["precip_mm"],
            "humidity": data["current"]["humidity"],
            "wind_kph": data["current"]["wind_kph"],
            "pressure_in": data["current"]["pressure_in"],
            "air_quality_Sulphur_dioxide": data["current"]["air_quality"]["so2"],
            "air_quality_Nitrogen_dioxide": data["current"]["air_quality"]["no2"],
            "air_quality_Ozone": data["current"]["air_quality"]["o3"],
            "visibility_km": data["current"]["vis_km"],
            "wind_degree": data["current"]["wind_degree"],
            "latitude": data["location"]["lat"],
            "longitude": data["location"]["lon"],
        }
        return weather_info, None
    else:
        error_message = response.json().get("error", {}).get("message", "Unknown error")
        return None, error_message

selected = option_menu(
    menu_title="Main Menu",
    options=["Cloudburst Prediction", "Landslide Prediction"],
    icons=["cloud", "radioactive"],
    menu_icon="cast",
    default_index=0,
)

api_key = "YOUR_API_KEY"


if selected == "Cloudburst Prediction":
    st.title("Cloudburst Prediction System")


    selected_state = st.selectbox("Select a State", options=sorted_states, placeholder="Choose a State")

    if selected_state:
        cities = states_and_cities[selected_state]
        selected_city = st.selectbox("Select a City", options=cities, placeholder="Choose a City")

        if selected_city:
            weather_info, error_message = get_weather(selected_city, api_key)

            if weather_info:
                weather_df = pd.DataFrame([weather_info])
                st.write(f"Weather information fetched for {selected_city}:")
                st.dataframe(weather_df)


                st.write("")
                temperature = st.number_input("Temperature (°C)", value=weather_info['temperature_celsius'])
                precipitation = st.number_input("Precipitation (mm)", value=weather_info['precip_mm'])
                humidity = st.number_input("Humidity (%)", value=weather_info['humidity'])
                wind_speed = st.number_input("Wind Speed (kph)", value=weather_info['wind_kph'])
                pressure = st.number_input("Pressure (inches)", value=weather_info['pressure_in'])
                sulfur_dioxide = st.number_input("Sulfur Dioxide (SO2)", value=weather_info['air_quality_Sulphur_dioxide'])
                nitrogen_dioxide = st.number_input("Nitrogen Dioxide (NO2)", value=weather_info['air_quality_Nitrogen_dioxide'])
                ozone = st.number_input("Ozone (O3)", value=weather_info['air_quality_Ozone'])
                visibility = st.number_input("Visibility (km)", value=weather_info['visibility_km'])
                wind_degree = st.number_input("Wind Degree", value=weather_info['wind_degree'])
                latitude = st.number_input("Latitude", value=weather_info['latitude'])
                longitude = st.number_input("Longitude", value=weather_info['longitude'])


                cloudburst_input = {
                    "temperature_celsius": [temperature],
                    "precip_mm": [precipitation],
                    "humidity": [humidity],
                    "wind_kph": [wind_speed],
                    "pressure_in": [pressure],
                    "air_quality_Sulphur_dioxide": [sulfur_dioxide],
                    "air_quality_Nitrogen_dioxide": [nitrogen_dioxide],
                    "air_quality_Ozone": [ozone],
                    "visibility_km": [visibility],
                    "wind_degree": [wind_degree],
                    "latitude": [latitude],
                    "longitude": [longitude]
                }
                if st.button("Submit"):
                    cloudburst_df = pd.DataFrame(cloudburst_input)


                    cloudburst_prediction = cloudburst_model.predict(cloudburst_df)

                    if cloudburst_prediction[0] == 0:
                        st.subheader("Prediction: No Cloudburst!")
                    else:
                        st.subheader("Prediction: Cloudburst Risk Detected!")
            else:
                st.error(f"Unable to fetch weather data: {error_message}")



if selected == "Landslide Prediction":
    st.title("Landslide Prediction System")


    soil_options = ['Clay', 'Loam', 'Silt', 'Sand']
    land_options = ['Forest', 'Barren', 'Agriculture', 'Urban']

    elevation = st.number_input("Enter Elevation:")
    slope = st.number_input("Enter slope:")
    aspect = st.number_input("Enter aspect")
    soil_type = st.selectbox("Choose soil type", options=soil_options)
    soil_moisture = st.number_input("Enter soil moisture:")
    vegetation_cover = st.number_input("Enter vegetation cover:")
    precipitation = st.number_input("Enter precipitation:")
    humidity = st.number_input("Enter humidity:")
    wind_speed = st.number_input("Enter wind speed:")
    deforestation = st.number_input("Enter deforestation (0 for no and 1 for yes):")
    urbanization = st.number_input("Enter urbanization:")
    land_use = st.selectbox("Choose land use", options=land_options)
    proximity = st.number_input("Enter proximity to river:")


    landslide_info = {
        'elevation': [elevation],
        'slope': [slope],
        'aspect': [aspect],
        'soil_type': [soil_type],
        'soil_moisture': [soil_moisture],
        'vegetation_cover': [vegetation_cover],
        'precipitation': [precipitation],
        'humidity': [humidity],
        'wind_speed_kph': [wind_speed],
        'deforestation': [deforestation],
        'urbanization': [urbanization],
        'land_use': [land_use],
        'proximity_to_river': [proximity]
    }


    if st.button("Submit"):
        soil_types_mapping = {'Clay': 1, 'Loam': 2, 'Silt': 3, 'Sand': 4}
        land_use_mapping = {'Forest': 1, 'Barren': 2, 'Agriculture': 3, 'Urban': 4}


        landslide_df = pd.DataFrame(landslide_info)


        landslide_df['soil_type'] = landslide_df['soil_type'].map(soil_types_mapping)
        landslide_df['land_use'] = landslide_df['land_use'].map(land_use_mapping)


        land_prediction = landslide_model.predict(landslide_df)


        if land_prediction[0] == 0:
            st.subheader("Prediction: No Landslide!")
        else:
            st.subheader("Prediction: Landslide Risk Detected!")
