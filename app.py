import streamlit as st
import pandas as pd
import numpy as np
import pickle
import csv

# ------------------ LOAD MODEL ------------------
model = pickle.load(open("model.pkl", "rb"))
le = pickle.load(open("label_encoder.pkl", "rb"))

# ------------------ LOAD DATA ------------------
training = pd.read_csv('Data/Training.csv')

training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
training = training.loc[:, ~training.columns.duplicated()]

cols = training.columns[:-1]

# ------------------ LOAD METADATA ------------------
description_list = {}
precaution_dict = {}

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

# ------------------ SYNONYMS ------------------
symptom_synonyms = {
    "fever": "high_fever",
    "cold": "chills",
    "cough": "cough",
    "headache": "headache",
    "breath": "breathlessness",
    "shortness of breath": "breathlessness",
    "body pain": "muscle_pain"
}

# ------------------ EXTRACT ------------------
def extract_symptoms(text):
    text = text.lower()
    found = []

    for key, value in symptom_synonyms.items():
        if key in text:
            found.append(value)

    for symptom in cols:
        if symptom.replace("_", " ") in text:
            found.append(symptom)

    return list(set(found))

# ------------------ PREDICT ------------------
def predict_disease(symptoms):
    input_vector = pd.DataFrame(
        [np.zeros(len(cols))],
        columns=cols
    )

    for s in symptoms:
        if s in input_vector.columns:
            input_vector[s] = 1

    probs = model.predict_proba(input_vector)[0]

    top_indices = np.argsort(probs)[-3:][::-1]

    results = []
    for i in top_indices:
        disease = le.inverse_transform([i])[0]
        confidence = round(probs[i] * 100, 2)
        results.append((disease, confidence))

    return results

# ------------------ UI ------------------
st.set_page_config(page_title="AI Health Assistant", page_icon="💊")

st.sidebar.title("👤 User Details")
name = st.sidebar.text_input("Name")
age = st.sidebar.number_input("Age", 1, 120)

st.title("💊 AI Health Assistant")
st.write("Enter your symptoms 👇")

user_input = st.text_input("Example: fever, cough, headache")

if st.button("Predict"):

    if not user_input.strip():
        st.warning("Enter symptoms")
    else:
        with st.spinner("Thinking..."):

            symptoms = extract_symptoms(user_input)

            if not symptoms:
                st.error("No symptoms detected")
            else:
                results = predict_disease(symptoms)

                st.success("Possible Diseases:")

                for d, c in results:
                    st.write(f"➡️ {d} ({c}%)")

                top = results[0][0]

                st.info(description_list.get(top, "No description"))

                st.subheader("Precautions")
                for p in precaution_dict.get(top, []):
                    st.write("✔️", p)
