from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import joblib
import os


app = Flask(__name__)



# Configuration & shared constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "merged_output", "merged_aqi_india.csv")

# Permitted ranges for each pollutant (used on client & server)
PERMITTED_RANGES = {
    "pm25": {"label": "PM2.5", "min": 0.0, "max": 500.0},
    "pm10": {"label": "PM10", "min": 0.0, "max": 600.0},
    "co": {"label": "CO", "min": 0.0, "max": 5.0},
    "no2": {"label": "NO₂", "min": 0.0, "max": 200.0},
    "so2": {"label": "SO₂", "min": 0.0, "max": 200.0},
    "o3": {"label": "O₃", "min": 0.0, "max": 200.0},
}



# Load existing model and dataset
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def load_city_stats():
    """
    Load the merged AQI dataset and pre-compute average AQI per city.
    This reuses your existing dataset for "most polluted cities".
    """
    if not os.path.exists(DATA_PATH):
        return None

    try:
        df = pd.read_csv(DATA_PATH)
        # Drop unnamed columns
        df = df.drop(columns=[c for c in df.columns if "Unnamed" in c], errors="ignore")

        if "City" not in df.columns or "AQI" not in df.columns:
            return None

        city_stats = (
            df.groupby("City", as_index=False)["AQI"]
            .mean()
            .rename(columns={"AQI": "avg_aqi"})
        )
        # Sort descending by pollution
        city_stats = city_stats.sort_values("avg_aqi", ascending=False)
        return city_stats
    except Exception:
        return None


model = load_model()
city_stats_df = load_city_stats()



# Domain logic (reusing your AQI logic)
def get_aqi_category(aqi: float) -> str:
    """Copied from your existing Streamlit app for consistency."""
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


def get_health_advice(category: str) -> str:
    """
    Return user-friendly health advice and precautions
    based strictly on the AQI category.
    """
    advice_map = {
        "Good": (
            "Air quality is good. It is safe to enjoy outdoor "
            "activities and no special precautions are needed."
        ),
        "Satisfactory": (
            "Air quality is generally acceptable. People with asthma, "
            "children, and the elderly may experience minor breathing "
            "discomfort during prolonged outdoor activity."
        ),
        "Moderate": (
            "Air quality may cause discomfort after long exposure. "
            "Reduce prolonged or heavy outdoor exertion, especially "
            "for sensitive groups."
        ),
        "Poor": (
            "Air quality is unhealthy. Avoid outdoor activities where "
            "possible, wear a mask if you must go outside, and keep "
            "windows closed to limit indoor pollution."
        ),
        "Very Poor": (
            "Air quality can have serious health impacts. Stay indoors "
            "as much as possible, avoid any outdoor exercise, and "
            "consider using air purifiers or well‑fitting masks."
        ),
        "Severe": (
            "Air quality is at emergency levels. Everyone may experience "
            "serious health effects. Remain indoors with doors and "
            "windows closed, avoid all outdoor exposure, and follow "
            "medical advice or public health alerts."
        ),
    }
    return advice_map.get(category, "")


def validate_inputs(payload):
    """
    Server-side validation for the 6 pollutant inputs.
    Ensures presence, numeric type, and range constraints.
    """
    errors = {}
    cleaned = {}

    for key, meta in PERMITTED_RANGES.items():
        raw_value = (payload.get(key) or "").strip()

        if raw_value == "":
            errors[key] = "This field is required."
            continue

        try:
            value = float(raw_value)
        except ValueError:
            errors[key] = "Value must be a number."
            continue

        vmin = meta["min"]
        vmax = meta["max"]
        if value < vmin or value > vmax:
            errors[key] = f"Value must be between {vmin} and {vmax}."
            continue

        cleaned[key] = value

    return len(errors) == 0, errors, cleaned


def calculate_pollution_score(cleaned_inputs):
    """
    Use your trained model to calculate a pollution score (AQI).
    cleaned_inputs: dict with numeric values for pm25, pm10, co, no2, so2, o3.
    """
    if model is None:
        raise RuntimeError("Model is not loaded.")

    features = np.array(
        [
            [
                cleaned_inputs["pm25"],
                cleaned_inputs["pm10"],
                cleaned_inputs["co"],
                cleaned_inputs["no2"],
                cleaned_inputs["so2"],
                cleaned_inputs["o3"],
            ]
        ]
    )

    predicted_aqi = float(model.predict(features)[0])
    # Cap AQI for safety, mirroring your Streamlit app
    predicted_aqi = round(min(predicted_aqi, 500.0), 2)
    return predicted_aqi


def get_most_polluted_cities(limit=5):
    """
    Returns a list of the most polluted cities based on
    average AQI in your merged dataset.
    """
    if city_stats_df is None or city_stats_df.empty:
        return []

    top = city_stats_df.head(limit)
    results = []
    for _, row in top.iterrows():
        results.append(
            {
                "city": str(row["City"]),
                "avgAqi": round(float(row["avg_aqi"]), 2),
            }
        )
    return results



# Routes
@app.route("/", methods=["GET"])
def index():
    """
    Render the main page with the 6-input form.
    """
    model_available = model is not None
    return render_template(
        "index.html",
        ranges=PERMITTED_RANGES,
        model_available=model_available,
    )


@app.route("/api/pollution", methods=["POST"])
def api_pollution():
    """
    Accepts the form data, validates it, calculates pollution score using
    your existing model, and returns the most polluted cities list.
    """
    try:
        if request.is_json:
            payload = request.get_json() or {}
        else:
            payload = request.form.to_dict()

        is_valid, errors, cleaned = validate_inputs(payload)

        if not is_valid:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Validation failed.",
                        "errors": errors,
                    }
                ),
                400,
            )

        if model is None:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Prediction model is not available on the server.",
                    }
                ),
                500,
            )

        pollution_score = calculate_pollution_score(cleaned)
        category = get_aqi_category(pollution_score)
        advice = get_health_advice(category)
        most_polluted = get_most_polluted_cities(limit=5)

        return jsonify(
            {
                "success": True,
                "inputs": cleaned,
                "pollutionScore": pollution_score,
                "category": category,
                "advice": advice,
                "mostPolluted": most_polluted,
            }
        )

    except Exception:
        # In a real app, log the exception here.
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An unexpected server error occurred.",
                }
            ),
            500,
        )


if __name__ == "__main__":
    # Development server
    app.run(debug=True)

