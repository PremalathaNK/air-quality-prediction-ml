import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

print("Loading dataset...")

# Correct dataset path
data = pd.read_csv("data/merged_output/merged_aqi_india.csv")

# Drop unnamed columns
data = data.drop(columns=[col for col in data.columns if "Unnamed" in col])

# Rename column
data = data.rename(columns={"PM2_5": "PM2.5"})

# Select required columns
columns = ["PM2.5", "PM10", "CO", "NO2", "SO2", "O3", "AQI"]
data = data[columns]

# Drop missing values
data = data.dropna()

print("Dataset cleaned")

# Features & target
X = data[["PM2.5", "PM10", "CO", "NO2", "SO2", "O3"]]
y = data["AQI"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training model...")

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print("Model trained successfully ✅")
print("MAE:", round(mae, 2))

# Save model
joblib.dump(model, "model.pkl")
print("model.pkl saved ✅")
