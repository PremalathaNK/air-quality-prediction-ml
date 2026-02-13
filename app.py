import streamlit as st
import numpy as np
import joblib
import os


# Page Configuration
st.set_page_config(
    page_title="Air Quality Prediction & Health Advisory",
    layout="centered"
)


# Load Model
MODEL_PATH = "model.pkl"

if not os.path.exists(MODEL_PATH):
    st.error("⚠️ Model not found. Please train and save the model first.")
    st.stop()

model = joblib.load(MODEL_PATH)


# Helper Functions
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"


def get_health_advice(category):
    advice = {
        "Good": "Air quality is good. Enjoy your day and outdoor activities.",
        "Satisfactory": "Air quality is acceptable. Sensitive individuals should be cautious.",
        "Moderate": "Air quality may cause mild discomfort. Reduce prolonged outdoor exposure.",
        "Poor": "Air quality is unhealthy. Avoid outdoor exercise and wear a mask if needed.",
        "Very Poor": "Air quality is very unhealthy. Children and elderly should stay indoors.",
        "Severe": "Air quality is hazardous. Everyone should avoid outdoor exposure."
    }
    return advice.get(category, "")


def check_input_ranges(pm25, pm10, co, no2, so2, o3):
    warnings = []

    if pm25 > 500:
        warnings.append("PM2.5 value is unusually high")
    if pm10 > 600:
        warnings.append("PM10 value is unusually high")
    if co > 5:
        warnings.append("CO value is higher than typical urban levels")
    if no2 > 200:
        warnings.append("NO₂ value is unusually high")
    if so2 > 200:
        warnings.append("SO₂ value is unusually high")
    if o3 > 200:
        warnings.append("O₃ value is unusually high")

    return warnings



# App UI
st.title("🌍 Air Quality Prediction & Health Advisory System")

st.write(
    "This application predicts the **Air Quality Index (AQI)** based on pollutant levels "
    "and translates the result into **simple health guidance** for citizens."
)

st.divider()


# User Inputs
st.subheader("🧪 Enter Pollutant Values")

pm25 = st.number_input("PM2.5", min_value=0.0, step=1.0)
pm10 = st.number_input("PM10", min_value=0.0, step=1.0)
co = st.number_input("CO", min_value=0.0, step=0.1)
no2 = st.number_input("NO₂", min_value=0.0, step=1.0)
so2 = st.number_input("SO₂", min_value=0.0, step=1.0)
o3 = st.number_input("O₃", min_value=0.0, step=1.0)


# Input Validation Warning
range_warnings = check_input_ranges(pm25, pm10, co, no2, so2, o3)

if range_warnings:
    st.warning(
        "Some entered values are outside typical urban air quality ranges. "
        "Predictions may be less reliable.\n\n• " + "\n• ".join(range_warnings)
    )


# Prediction
if st.button("Predict AQI"):
    input_data = np.array([[pm25, pm10, co, no2, so2, o3]])
    predicted_aqi = model.predict(input_data)[0]

    # Cap AQI at 500 (standard scale)
    predicted_aqi = round(min(predicted_aqi, 500), 2)

    category = get_aqi_category(predicted_aqi)
    advice = get_health_advice(category)

    st.divider()

    st.subheader("📊 Prediction Result")
    st.metric(label="Predicted AQI", value=predicted_aqi)
    st.write(f"**Category:** {category}")

    st.subheader("🩺 Health Advisory")
    st.info(advice)

    if predicted_aqi >= 400:
        st.error(
            "This AQI level indicates extremely hazardous air quality. "
            "All individuals should avoid outdoor exposure."
        )


# Social Impact Section
st.divider()

st.subheader("📌 Social Impact")

st.write(
    "Air pollution is a silent threat in many Indian cities. "
    "This project aims to convert complex air quality data into "
    "clear and understandable health guidance so that common citizens "
    "can take informed precautions."
)
