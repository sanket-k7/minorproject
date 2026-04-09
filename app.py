import streamlit as st
import pandas as pd
import numpy as np
import csv
import pickle

# ------------------ LOAD MODEL ------------------
model = pickle.load(open("model.pkl", "rb"))
le = pickle.load(open("label_encoder.pkl", "rb"))

# ------------------ LOAD DATA ------------------
training = pd.read_csv('Data/Training.csv')

training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
training = training.loc[:, ~training.columns.duplicated()]

cols = training.columns[:-1]
symptoms_dict = {symptom: idx for idx, symptom in enumerate(cols)}

# ------------------ LOAD METADATA ------------------
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

# ------------------ SYNONYMS ------------------
symptom_synonyms = {
    "fever": "high_fever",
    "cold": "chills",
    "cough": "cough",
    "headache": "headache",
    "stomach pain": "stomach_pain",
    "breathing problem": "breathlessness",
    "shortness of breath": "breathlessness",
    "body pain": "muscle_pain"
}

# ------------------ EXTRACT SYMPTOMS ------------------
def extract_symptoms(text):
    text = text.lower()
    found = []

    # synonyms
    for key, value in symptom_synonyms.items():
        if key in text:
            found.append(value)

    # dataset match
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

    probs = model.predict_proba([input_vector])[0]

    top_indices = np.argsort(probs)[-3:][::-1]

    results = []
    for i in top_indices:
        disease = le.inverse_transform([i])[0]
        confidence = round(probs[i] * 100, 2)
        results.append((disease, confidence))

    return results

# ------------------ UI ------------------
st.set_page_config(page_title="AI Health Assistant", page_icon="💊")

# Sidebar
st.sidebar.title("👤 User Profile")
name = st.sidebar.text_input("Enter your name")
age = st.sidebar.number_input("Enter your age", 1, 120)

# Main
st.title("💊 AI Health Assistant")
st.markdown("### Describe your symptoms 👇")

user_input = st.text_input("Example: fever, headache, cough")

if st.button("🔍 Predict Disease"):

    if not user_input.strip():
        st.warning("⚠️ Please enter symptoms")
    else:
        with st.spinner("🤖 Analyzing..."):

            symptoms = extract_symptoms(user_input)

            if not symptoms:
                st.error("❌ No symptoms detected. Try simpler words.")
            else:
                results = predict_disease(symptoms)

                st.success("🧠 Possible Diseases:")

                for disease, confidence in results:
                    st.write(f"➡️ **{disease}** ({confidence}%)")

                # Low confidence warning
                if results[0][1] < 30:
                    st.warning("⚠️ Low confidence prediction. Consult a doctor.")

                # Show details for top result
                top_disease = results[0][0]

                description = description_list.get(top_disease, "No description available.")
                precautions = precaution_dict.get(top_disease, [])

                st.info(f"📖 {description}")

                st.subheader("🛡️ Precautions")
                if precautions:
                    for p in precautions:
                        st.write("✔️", p)
                else:
                    st.write("No precautions available")

# Footer
st.markdown("---")
st.caption("🚀 Built by Sanket | AI Health Assistant")
