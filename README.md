# 🌍 Air Quality – Pollution Explorer

Air pollution affects our daily life and health, especially in cities.  
This project is a web application that predicts the **Air Quality Index (AQI)** using air pollutant values and shows the **most polluted cities in India**. It also provides **easy-to-understand health advice** based on the AQI level.

---

## 📌 About the Project

Understanding air quality numbers can be confusing for common people.  
This project solves that by:

- Taking common air pollutant values as input  
- Predicting the AQI using a machine learning model  
- Classifying air quality (Good, Moderate, Poor, etc.)  
- Giving simple health precautions  
- Displaying cities with the highest average AQI  

The goal is to make air quality information **simple, useful, and practical**.

---

## ✨ What This Application Does

- Predicts AQI using 6 air pollutants  
- Allows only valid and permitted input values  
- Shows AQI category in clear terms  
- Displays health advice for each AQI level  
- Lists the most polluted cities in India  
- Clean and responsive user interface  
- Works as a complete frontend + backend project  

---

## 🧪 Inputs Used

The user needs to enter the following values:

- PM2.5 (µg/m³)  
- PM10 (µg/m³)  
- CO (mg/m³)  
- NO₂ (µg/m³)  
- SO₂ (µg/m³)  
- O₃ (µg/m³)  

All inputs are validated so that **invalid or unrealistic values are not accepted**.

---

## 📊 AQI Levels Explained

- **Good** – Safe air quality  
- **Satisfactory** – Minor breathing discomfort for sensitive people  
- **Moderate** – Discomfort for people with lung problems  
- **Poor** – Unhealthy air, avoid outdoor activity  
- **Very Poor** – Serious health effects  
- **Severe** – Emergency conditions  

---

## 🩺 Health Advice

Based on the predicted AQI, the application provides **simple health suggestions**, such as:

- Reducing outdoor activities  
- Wearing masks  
- Staying indoors for sensitive groups  

This helps users take quick and practical precautions.

---

## 🛠️ Technologies Used

### Frontend
- HTML  
- CSS  
- JavaScript  

### Backend
- Python  
- Flask (for handling requests and predictions)


### Machine Learning
- Random Forest Regressor (for AQI prediction)
- Scikit-learn

### Other Tools
- Pandas  
- NumPy  
- Joblib  

---
## 🚀 Live Demo
https://air-quality-prediction-ml-t0ia.onrender.com/


## ▶️ How to Run the Project

```bash
# Step 1: Clone the repository
git clone https://github.com/PremalathaNK/air-quality-pollution-explorer.git
cd air-quality-pollution-explorer

# Step 2: Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Step 3: Install required packages
pip install -r requirements.txt

# Step 4: Run the application
python app.py

# Step 5: Open in browser
http://127.0.0.1:5000
```
