from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import re
from difflib import get_close_matches
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
import csv

app = Flask(__name__)
CORS(app)

# ------------------ LOAD DATA ------------------
training = pd.read_csv('Data/Training.csv')
training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
training = training.loc[:, ~training.columns.duplicated()]

cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']

le = preprocessing.LabelEncoder()
y = le.fit_transform(y)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(x, y)

symptoms_dict = {symptom: idx for idx, symptom in enumerate(cols)}

# ------------------ EXTRA DATA ------------------
description_list = {}
precautionDictionary = {}

def load_data():
    with open('MasterData/symptom_Description.csv') as f:
        for row in csv.reader(f):
            description_list[row[0]] = row[1]

    with open('MasterData/symptom_precaution.csv') as f:
        for row in csv.reader(f):
            precautionDictionary[row[0]] = [row[1], row[2], row[3], row[4]]

load_data()

# ------------------ SYMPTOM EXTRACT ------------------
def extract_symptoms(text):
    text = text.lower()
    found = []

    for symptom in cols:
        if symptom.replace("_", " ") in text:
            found.append(symptom)

    return list(set(found))

# ------------------ PREDICT ------------------
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
    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"response": "Please enter symptoms"})

    symptoms = extract_symptoms(message)

    if not symptoms:
        return jsonify({"response": "No symptoms detected"})

    disease = predict_disease(symptoms)

    desc = description_list.get(disease, "No description available.")
    precautions = precautionDictionary.get(disease, [])

    response_text = f"""
🦠 Disease: {disease}

📖 {desc}

🛡️ Precautions:
{', '.join(precautions)}
"""

    return jsonify({"response": response_text})


@app.route('/')
def home():
    return "Backend is running 🚀"


if __name__ == "__main__":
    app.run(debug=True)
