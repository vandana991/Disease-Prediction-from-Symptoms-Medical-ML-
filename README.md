<<<<<<< HEAD
# MedPredict AI: Disease Prediction from Symptoms

MedPredict AI is a complete web application designed to predict potential medical conditions based on user-selected symptoms. It combines a robust machine learning backend trained on a standard clinical dataset using a **Random Forest Classifier** with a premium, responsive, and interactive frontend built using Vanilla HTML, CSS, and JavaScript.

---
# Deployment Link:https://disease-prediction-from-symptoms-me.vercel.app/
## Technical Stack
- **Core backend**: Python, Flask
- **Machine Learning**: Scikit-Learn, Pandas, NumPy, Joblib
- **Frontend Design**: Semantic HTML5, Custom Responsive CSS Variables, Vanilla ES6 JavaScript
- **Typography**: Outfit & Inter (via Google Fonts)
- **Dataset Source**: Synthetic symptom-disease dataset mapped from public medical diagnostic databases.

---

## Folder Structure

```
DiseasePrediction/
│
├── dataset/                      # Dataset CSVs (auto-downloaded on train)
│   ├── Training.csv
│   ├── Testing.csv
│   ├── symptom_Description.csv
│   └── symptom_precaution.csv
│
├── model/                        # Machine learning assets and lookup files
│   ├── disease_model.pkl         # Serialized Random Forest model
│   ├── symptom_list.json         # Array of 132 symptoms for vector alignment
│   └── disease_details.json      # Merged dictionary of descriptions & precautions
│
├── templates/
│   └── index.html                # Main frontend template
│
├── static/
│   ├── style.css                 # Premium medical-themed styles & layouts
│   └── script.js                 # Autocomplete, state tracking & rendering logic
│
├── train_model.py                # Pipeline script to download files & train model
├── app.py                        # Flask API web server
├── requirements.txt              # Project package requirements
└── README.md                     # Project documentation
```

---

## Quick Setup and Launch Instructions

Follow these three steps to run the application locally on your machine.

### 1. Install Dependencies
Ensure you have Python 3.8+ installed. Open a terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 2. Train the Machine Learning Model
Run the model training pipeline script. This will automatically download all required clinical datasets from GitHub, preprocess the inputs, train a Random Forest Classifier, and export all necessary inference files inside the `model/` directory:
```bash
python train_model.py
```
*Expected console output: Model Accuracy on Testing Data: 1.0000 (100.00%) along with classification reports.*

### 3. Launch the Web Server
Start the Flask application backend by running:
```bash
python app.py
```
Open your web browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## Machine Learning & Preprocessing Details
1. **Symptom Vectorization**: The model uses a feature vector of length 132, where each entry represents a symptom (e.g. `high_fever`, `vomiting`, `skin_rash`) mapped as `0` (absent) or `1` (present).
2. **Standardization & Casing**: To prevent KeyErrors caused by spelling inconsistencies and spacing inside Kaggle clinical datasets, the pipeline standardizes all disease prediction lookups. It strips whitespace, standardizes spaces, and matches keys case-insensitively.
3. **Random Forest Classifier**: A Random Forest Classifier with 100 estimators is trained to map vectors to one of 41 unique disease categories, yielding a highly accurate classification match based on the standard training splits.
4. **Statistical Match Ranking (Top 3 Predictions)**: Instead of just returning the top classification, the Flask backend computes probability scores across the entire label vector using `predict_proba`. It ranks classes in descending order to return the **Top 3 most probable conditions** to the frontend, which are displayed as interactive, expandable cards.

---

## Medical Prototype Disclaimer
> [!WARNING]
> This application is an educational prototype built to demonstrate machine learning classification on synthetic healthcare datasets. It is not intended for clinical use, does not represent certified medical software, and should never be used as a substitute for professional medical consultation, diagnosis, or treatment. If you are experiencing severe symptoms, please seek immediate assistance from a licensed medical professional.
=======
# Disease-Prediction-from-Symptoms-Medical-ML-
>>>>>>> d2ec88cc68407a119ca32d128bb1dfc5340385b0
