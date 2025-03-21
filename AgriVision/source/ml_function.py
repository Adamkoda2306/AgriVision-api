import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
import os

def train_model(csv_path, model_path="models/crop_model.pkl"):
    df = pd.read_csv(csv_path)
    X = df.drop("label", axis=1)
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_test_enc = le.transform(y_test)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    clf = RandomForestClassifier(n_estimators=30, random_state=42)  #clf=classifier,le=LabelEncoder,scaler=StandardScaler
    clf.fit(X_train_scaled, y_train_enc)
    joblib.dump((clf, le, scaler), model_path)
    return clf, le, scaler


def load_model(model_path=None):
    if model_path is None:
        # Get absolute path relative to model.py
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        model_path = os.path.join(base_dir, "..", "models", "crop_model.pkl")
        model_path = os.path.abspath(model_path)  # Ensure absolute path

    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        print(f"❌ Model file not found at: {model_path}")
        raise
    except Exception as e:
        print(f"❌ Error loading model: {e}")

def evaluate_model(clf, X_test, y_test, classes):
    y_pred = clf.predict(X_test)
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()
    print(classification_report(y_test, y_pred))

def give_crop(lat, lon, manual_data=None, default_P=53.362727, default_K=48.149091):
    clf, le, scaler = load_model()
    
    try:
        if manual_data:
            data = manual_data
        else:
            from . import utils
            data = utils.get_combined_data(lat, lon)
        
        # Convert input values to float, replacing empty strings with default values
        nitrogen = float(data.get("N", 0) or 0) * 1350 * 0.05 * 0.1  
        phosphorus = float(data.get("P", default_P) or default_P)
        potassium = float(data.get("K", default_K) or default_K)
        temperature = float(data.get("Temperature (°C)", 0) or 0)
        humidity = float(data.get("Humidity (%)", 0) or 0)
        ph = float(data.get("ph", 0) or 0)
        rainfall = float(data.get("Rainfall (mm)", 0) or 0)

        # ✅ Fix feature names to match training data
        features_dict = {
            "N": nitrogen,
            "P": phosphorus,
            "K": potassium,
            "temperature": temperature,   # Renamed to match training data
            "humidity": humidity,         # Renamed to match training data
            "ph": ph,
            "rainfall": rainfall          # Renamed to match training data
        }

        # Create DataFrame
        features_df = pd.DataFrame([features_dict])

        # Scale input data
        features_scaled = scaler.transform(features_df)

        # Predict crop
        pred = clf.predict(features_scaled)
        return le.inverse_transform(pred)[0]

    except ValueError as e:
        return f"Prediction failed: Invalid data format ({e})"
    except Exception as e:
        return f"Prediction failed: {e}"



def get_fertilizer_suggestion(soil_data, crop):
    """Wrapper for fertilizer recommendation"""
    from . import utils
    return utils.get_fertilizer_recommendation(soil_data, crop)