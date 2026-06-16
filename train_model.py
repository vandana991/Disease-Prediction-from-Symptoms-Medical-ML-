import os
import json
import urllib.request
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Constants
DATASET_DIR = "dataset"
MODEL_DIR = "model"

URLS = {
    "Training.csv": "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/Training.csv",
    "Testing.csv": "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/Testing.csv",
    "symptom_Description.csv": "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/symptom_Description.csv",
    "symptom_precaution.csv": "https://raw.githubusercontent.com/yash-naikk/HEALTH-CARE-CHATBOT/master/symptom_precaution.csv"
}

def download_file(url, filepath):
    print(f"Downloading {url} to {filepath}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Successfully downloaded {filepath}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        raise

def normalize_name(name):
    """Normalize disease names to avoid lookup key mismatches due to typos, case, or trailing spaces."""
    if not isinstance(name, str):
        return ""
    return " ".join(name.strip().lower().split())

def main():
    # Ensure directories exist
    os.makedirs(DATASET_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Download datasets if they don't exist
    for filename, url in URLS.items():
        filepath = os.path.join(DATASET_DIR, filename)
        if not os.path.exists(filepath):
            download_file(url, filepath)
        else:
            print(f"File {filepath} already exists. Skipping download.")

    print("\n--- Loading and Preprocessing Data ---")
    train_path = os.path.join(DATASET_DIR, "Training.csv")
    test_path = os.path.join(DATASET_DIR, "Testing.csv")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    # Drop the artifact column 'Unnamed: 133' if present
    if "Unnamed: 133" in train_df.columns:
        train_df = train_df.drop(columns=["Unnamed: 133"])
    if "Unnamed: 133" in test_df.columns:
        test_df = test_df.drop(columns=["Unnamed: 133"])

    # Separate features and target
    X_train = train_df.drop(columns=["prognosis"])
    y_train = train_df["prognosis"]
    X_test = test_df.drop(columns=["prognosis"])
    y_test = test_df["prognosis"]

    print(f"Training set features shape: {X_train.shape}")
    print(f"Testing set features shape: {X_test.shape}")

    # Train Random Forest
    print("\n--- Training Random Forest Classifier ---")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("Model training completed successfully.")

    # Evaluate model
    print("\n--- Evaluating Model ---")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy on Testing Data: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save trained model and symptom list
    model_path = os.path.join(MODEL_DIR, "disease_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    symptoms = list(X_train.columns)
    symptom_list_path = os.path.join(MODEL_DIR, "symptom_list.json")
    with open(symptom_list_path, "w", encoding="utf-8") as f:
        json.dump(symptoms, f, indent=4)
    print(f"Symptom list saved to {symptom_list_path}")

    # Process and merge descriptions & precautions
    print("\n--- Merging Disease Descriptions and Precautions ---")
    desc_path = os.path.join(DATASET_DIR, "symptom_Description.csv")
    prec_path = os.path.join(DATASET_DIR, "symptom_precaution.csv")

    desc_df = pd.read_csv(desc_path, header=None, names=["Disease", "Description"])
    prec_df = pd.read_csv(prec_path, header=None, names=["Disease", "Precaution_1", "Precaution_2", "Precaution_3", "Precaution_4"])

    details_dict = {}

    # Load descriptions
    for _, row in desc_df.iterrows():
        disease_raw = row["Disease"]
        desc = row["Description"]
        norm_key = normalize_name(disease_raw)
        
        details_dict[norm_key] = {
            "disease_name": disease_raw.strip(),
            "description": desc.strip() if isinstance(desc, str) else "",
            "precautions": []
        }

    # Load precautions
    for _, row in prec_df.iterrows():
        disease_raw = row["Disease"]
        norm_key = normalize_name(disease_raw)

        # Get all precaution columns
        precaution_cols = ["Precaution_1", "Precaution_2", "Precaution_3", "Precaution_4"]
        precautions = []
        for col in precaution_cols:
            if col in row and pd.notna(row[col]):
                val = str(row[col]).strip()
                if val:
                    precautions.append(val)

        if norm_key in details_dict:
            details_dict[norm_key]["precautions"] = precautions
        else:
            # If disease was not in descriptions, create entry
            details_dict[norm_key] = {
                "disease_name": disease_raw.strip(),
                "description": "No description available.",
                "precautions": precautions
            }

    # Add fallback descriptions/precautions for any prognosis classes that might be missing in CSVs
    unique_prognoses = y_train.unique()
    for disease in unique_prognoses:
        norm_key = normalize_name(disease)
        if norm_key not in details_dict:
            print(f"Warning: {disease} not found in description or precaution files. Adding placeholder.")
            details_dict[norm_key] = {
                "disease_name": disease.strip(),
                "description": f"No detailed medical description is currently available for {disease.strip()}.",
                "precautions": ["Consult a medical professional", "Monitor symptoms", "Get plenty of rest"]
            }

    # Save to details JSON
    details_path = os.path.join(MODEL_DIR, "disease_details.json")
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(details_dict, f, indent=4)
    print(f"Disease details dictionary saved to {details_path}")

    print("\n--- Training Pipeline Finished Successfully ---")

if __name__ == "__main__":
    main()
