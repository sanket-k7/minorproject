from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import csv
import pickle

app = Flask(__name__)
CORS(app)

# ------------------ LOAD MODEL ------------------
model = pickle.load(open("model.pkl", "rb"))
le = pickle.load(open("label_encoder.pkl", "rb"))

# ------------------ LOAD DATA (for symptoms list only) ------------------
training = pd.read_csv('Data/Training.csv')
cols = training.columns[:-1]

symptoms_dict = {symptom: idx for idx, symptom in enumerate(cols)}

# ------------------ LOAD EXTRA FILES ------------------
description_list = {}
precaution_dict = {}

def load_metadata():
    try:
        with open('MasterData/symptom_Description.csv') as f:
            for row in csv.reader(f):
                description_list[row[0]] = row[1]
    except:
        pass

    try:
        with open('MasterData/symptom_precaution.csv') as f:
            for row in csv.reader(f):
                precaution_dict[row[0]] = [row[1], row[2], row[3], row[4]]
    except:
        pass

load_metadata()

# ------------------ EXTRACT SYMPTOMS ------------------
def extract_symptoms(text):
    text = text.lower()
    found = []

    for symptom in cols:
        if symptom.replace("_", " ") in text:
            found.append(symptom)

    return list(set(found))

# ------------------ PREDICTION ------------------
def predict_disease(symptoms):
    input_vector = np.zeros(len(symptoms_dict))

    for s in symptoms:
        if s in symptoms_dict:
            input_vector[symptoms_dict[s]] = 1

    pred = model.predict([input_vector])[0]
    disease = le.inverse_transform([pred])[0]

    return disease

# ------------------ API ------------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")

        if not message.strip():
            return jsonify({"response": "⚠️ Please enter symptoms"})

        symptoms = extract_symptoms(message)

        if not symptoms:
            return jsonify({"response": "❌ No symptoms detected"})

        disease = predict_disease(symptoms)

        description = description_list.get(disease, "No description available.")
        precautions = precaution_dict.get(disease, [])

        response = f"""
🦠 Disease: {disease}

📖 {description}

🛡️ Precautions:
{', '.join(precautions) if precautions else 'No precautions found'}
"""

        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"})

# ------------------ HOME ------------------
@app.route('/')
def home():
    return "✅ Backend running fast 🚀"

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)
