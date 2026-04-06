from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)

# ------------------ LOAD DATA ------------------
try:
    training = pd.read_csv('Data/Training.csv')
except:
    training = pd.read_csv('Data/training.csv')  # fallback

# Clean duplicate columns
training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
training = training.loc[:, ~training.columns.duplicated()]

cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']

# Encode labels
le = LabelEncoder()
y = le.fit_transform(y)

# Train model ONCE (fast)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(x, y)

# Symptom index mapping
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

# ------------------ API ROUTE ------------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")

        if not message.strip():
            return jsonify({"response": "⚠️ Please enter symptoms"})

        symptoms = extract_symptoms(message)

        if not symptoms:
            return jsonify({"response": "❌ No symptoms detected. Try again."})

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

# ------------------ HEALTH CHECK ------------------
@app.route('/')
def home():
    return "✅ Backend running successfully"

# ------------------ RUN ------------------
if __name__ == '__main__':
    app.run(debug=True)
