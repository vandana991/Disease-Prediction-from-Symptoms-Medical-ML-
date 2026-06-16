import os
import json
import logging
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenRouter client
# You can set the OPENROUTER_API_KEY environment variable or replace the placeholder
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY","your_new_api_key_here")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Paths
MODEL_PATH = os.path.join("model", "disease_model.pkl")
SYMPTOM_LIST_PATH = os.path.join("model", "symptom_list.json")
DETAILS_PATH = os.path.join("model", "disease_details.json")

# Global variables for model and metadata
model = None
symptom_list = None
disease_details = None

def load_artifacts():
    global model, symptom_list, disease_details
    
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SYMPTOM_LIST_PATH) or not os.path.exists(DETAILS_PATH):
        logger.warning("Artifacts missing! Please run 'python train_model.py' to generate the model and metadata.")
        return False
    
    try:
        model = joblib.load(MODEL_PATH)
        
        with open(SYMPTOM_LIST_PATH, "r", encoding="utf-8") as f:
            symptom_list = json.load(f)
            
        with open(DETAILS_PATH, "r", encoding="utf-8") as f:
            disease_details = json.load(f)
            
        logger.info("Successfully loaded all machine learning artifacts.")
        return True
    except Exception as e:
        logger.error(f"Error loading artifacts: {e}")
        return False

# Try loading artifacts on startup
artifacts_loaded = load_artifacts()

def normalize_name(name):
    """Normalize disease names to standard lowercase single-space representation."""
    if not isinstance(name, str):
        return ""
    return " ".join(name.strip().lower().split())

@app.route("/")
def home():
    # If artifacts aren't loaded, try loading them again (in case train_model.py was run after app.py started)
    global artifacts_loaded
    if not artifacts_loaded:
        artifacts_loaded = load_artifacts()
        
    # Send symptoms to frontend so it can dynamically generate checkboxes/search items
    symptoms_to_send = []
    if symptom_list:
        # Format symptom names for display (e.g. replacing underscores with spaces, capitalizing)
        symptoms_to_send = [
            {"id": sym, "name": sym.replace("_", " ").strip().title()}
            for sym in symptom_list
        ]
        
    return render_template("index.html", symptoms=symptoms_to_send, model_status=artifacts_loaded)

@app.route("/predict", methods=["POST"])
def predict():
    global model, symptom_list, disease_details, artifacts_loaded
    
    # Reload if they weren't loaded previously
    if not artifacts_loaded:
        artifacts_loaded = load_artifacts()
        if not artifacts_loaded:
            return jsonify({
                "status": "error",
                "message": "Model files not found. Please run 'python train_model.py' to train and save the model."
            }), 500

    try:
        data = request.get_json()
        if not data or "description" not in data:
            return jsonify({
                "status": "error",
                "message": "Invalid request. Please provide a description."
            }), 400

        user_description = data["description"]
        if not user_description.strip():
            return jsonify({
                "status": "error",
                "message": "Please provide a valid description for analysis."
            }), 400

        # Use LLM to extract symptoms and analyze conditions
        try:
            prompt = f"""You are an experienced clinical symptom analysis assistant.

Analyze the patient's description carefully and identify ALL symptoms, triggers, severity indicators, duration information, age-related factors, and possible medical conditions.

Instructions:

1. Extract symptoms explicitly mentioned by the patient.
2. Infer medically relevant symptoms only when strongly supported by the description.
3. Consider age and gender when evaluating possible conditions.
4. Identify symptom triggers (exercise, food, allergens, weather, stress, etc.).
5. Rank the top 3 most likely conditions with confidence percentages.
6. Explain why each condition matches the symptoms.
7. Recommend whether the patient should seek urgent medical attention.
8. If the description is insufficient, explain what additional information is needed.

Return ONLY a valid JSON object with the following schema:
{{
  "symptoms": ["list", "of", "strings"],
  "triggers": ["list", "of", "strings"],
  "severity_indicators": ["list", "of", "strings"],
  "duration_information": "string or null",
  "age_related_factors": "string or null",
  "top_3": [
    {{
      "disease_name": "string",
      "confidence": float (e.g., 85.5),
      "description": "string",
      "precautions": ["list", "of", "strings"]
    }}
  ],
  "urgent_medical_attention_recommended": boolean,
  "additional_information_needed": "string or null"
}}

Patient Description:
"{user_description}"
"""
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            resp_text = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting
            if resp_text.startswith("```json"):
                resp_text = resp_text[7:]
            if resp_text.startswith("```"):
                resp_text = resp_text[3:]
            if resp_text.endswith("```"):
                resp_text = resp_text[:-3]
            resp_text = resp_text.strip()
            
            analysis_data = json.loads(resp_text)
            
        except Exception as e:
            logger.error(f"Error calling LLM or parsing response: {e}")
            return jsonify({
                "status": "error",
                "message": f"Failed to analyze symptoms using AI model: {str(e)}"
            }), 500

        top_3 = analysis_data.get("top_3", [])
        if not top_3:
            return jsonify({
                "status": "error",
                "message": analysis_data.get("additional_information_needed", "Could not identify any conditions from the given description.")
            }), 400

        top_prediction = top_3[0]
        selected_symptoms = analysis_data.get("symptoms", [])

        # Return response
        return jsonify({
            "status": "success",
            "predicted_disease": top_prediction.get("disease_name", "Unknown"),
            "confidence": top_prediction.get("confidence", 0),
            "description": top_prediction.get("description", ""),
            "precautions": top_prediction.get("precautions", []),
            "selected_symptoms": selected_symptoms,
            "top_3": top_3,
            "triggers": analysis_data.get("triggers", []),
            "severity_indicators": analysis_data.get("severity_indicators", []),
            "duration_information": analysis_data.get("duration_information"),
            "age_related_factors": analysis_data.get("age_related_factors"),
            "urgent_medical_attention_recommended": analysis_data.get("urgent_medical_attention_recommended", False),
            "additional_information_needed": analysis_data.get("additional_information_needed")
        })

    except Exception as e:
        logger.error(f"Error during prediction endpoint execution: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"An internal server error occurred: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
