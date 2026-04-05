from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import csv
import re
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from difflib import get_close_matches
import warnings
import os

warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)

# ------------------ LOAD DATA ------------------
training = pd.read_csv("Training.csv")
testing = pd.read_csv("Testing.csv")

training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
testing.columns = testing.columns.str.replace(r"\.\d+$", "", regex=True)

training = training.loc[:, ~training.columns.duplicated()]
testing = testing.loc[:, ~testing.columns.duplicated()]

cols = training.columns[:-1]
x = training[cols]
y = training["prognosis"]

le = preprocessing.LabelEncoder()
y = le.fit_transform(y)

x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.33, random_state=42
)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(x_train, y_train)

# ------------------ DICTIONARIES ------------------
severityDictionary = {}
description_list = {}
precautionDictionary = {}
symptoms_dict = {symptom: idx for idx, symptom in enumerate(x)}

def getDescription():
    try:
        with open("symptom_Description.csv") as csv_file:
            for row in csv.reader(csv_file):
                description_list[row[0]] = row[1]
    except:
        pass

def getSeverityDict():
    try:
        with open("Symptom_severity.csv") as csv_file:
            for row in csv.reader(csv_file):
                try:
                    severityDictionary[row[0]] = int(row[1])
                except:
                    pass
    except:
        pass

def getprecautionDict():
    try:
        with open("symptom_precaution.csv") as csv_file:
            for row in csv.reader(csv_file):
                precautionDictionary[row[0]] = [row[1], row[2], row[3], row[4]]
    except:
        pass

getDescription()
getSeverityDict()
getprecautionDict()

# ------------------ SYMPTOM EXTRACT ------------------
def extract_symptoms(user_input, all_symptoms):
    extracted = []
    text = user_input.lower()

    for symptom in all_symptoms:
        if symptom.replace("_", " ") in text:
            extracted.append(symptom)

    words = re.findall(r"\w+", text)
    for word in words:
        close = get_close_matches(word, [s.replace("_", " ") for s in all_symptoms], n=1, cutoff=0.8)
        if close:
            for sym in all_symptoms:
                if sym.replace("_", " ") == close[0]:
                    extracted.append(sym)

    return list(set(extracted))

# ------------------ PREDICTION ------------------
def predict_disease(symptoms_list):
    input_vector = np.zeros(len(symptoms_dict))

    for symptom in symptoms_list:
        if symptom in symptoms_dict:
            input_vector[symptoms_dict[symptom]] = 1

    pred_proba = model.predict_proba([input_vector])[0]
    pred_class = np.argmax(pred_proba)

    disease = le.inverse_transform([pred_class])[0]
    confidence = round(pred_proba[pred_class] * 100, 2)

    return disease, confidence

# ------------------ API ROUTE ------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    symptoms_list = extract_symptoms(user_input, cols)

    if not symptoms_list:
        return jsonify({"response": "❌ Please describe symptoms clearly."})

    disease, confidence = predict_disease(symptoms_list)

    description = description_list.get(disease, "No description available.")
    precautions = precautionDictionary.get(disease, [])

    response = f"""
🩺 Disease: {disease}
📊 Confidence: {confidence}%

📖 {description}

🛡️ Precautions:
{', '.join(precautions)}
"""

    return jsonify({"response": response})

# ------------------ RUN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
