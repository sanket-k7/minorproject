import streamlit as st
import pandas as pd
import numpy as np
import csv
from sklearn.ensemble import RandomForestClassifier

# ------------------ PAGE ------------------
st.set_page_config(page_title="AI Health Assistant", layout="wide")

# ------------------ LOAD MODEL ------------------
@st.cache_resource
def load_model():
    training = pd.read_csv("Data/Training.csv")

    # Remove duplicate columns
    training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
    training = training.loc[:, ~training.columns.duplicated()]

    X = training.iloc[:, :-1]
    y = training["prognosis"]   # ✅ REAL DISEASE NAMES

    model = RandomForestClassifier(n_estimators=80, random_state=42)
    model.fit(X, y)

    return model, X.columns

model, cols = load_model()

# ------------------ LOAD METADATA ------------------
@st.cache_data
def load_metadata():
    description_list = {}
    precaution_dict = {}

    try:
        with open("MasterData/symptom_Description.csv") as f:
            for row in csv.reader(f):
                description_list[row[0]] = row[1]
    except:
        pass

    try:
        with open("MasterData/symptom_precaution.csv") as f:
            for row in csv.reader(f):
                precaution_dict[row[0]] = [row[1], row[2], row[3], row[4]]
    except:
        pass

    return description_list, precaution_dict

description_list, precaution_dict = load_metadata()

# ------------------ SYNONYMS ------------------
symptom_synonyms = {
    "fever": "high_fever",
    "cold": "chills",
    "cough": "cough",
    "headache": "headache",
    "breathing problem": "breathlessness",
    "shortness of breath": "breathlessness",
    "body pain": "muscle_pain"
}

# ------------------ FUNCTIONS ------------------
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
        disease = model.classes_[i]   # ✅ NOW RETURNS REAL NAME
        confidence = round(probs[i] * 100, 2)
        results.append((disease, confidence))

    return results

# ------------------ UI ------------------
st.title("💊 AI Health Assistant")

# Sidebar
st.sidebar.header("👤 User Details")
name = st.sidebar.text_input("Enter your name")
age = st.sidebar.number_input("Enter your age", 1, 120)

st.markdown("### Enter your symptoms 👇")

user_input = st.text_input("Type symptoms (e.g., fever, headache)")

if st.button("Predict"):

    if user_input.strip() == "":
        st.error("⚠️ Please enter symptoms")

    else:
        symptoms = extract_symptoms(user_input)

        if not symptoms:
            st.error("❌ No symptoms detected")
        else:
            results = predict_disease(symptoms)

            top_disease = results[0][0]

            description = description_list.get(top_disease, "No description available")
            precautions = precaution_dict.get(top_disease, [])

            # OUTPUT
            st.success(f"🦠 Top Disease: {top_disease}")

            st.subheader("📊 Other Possibilities")
            for d, c in results:
                st.write(f"➡️ {d} ({c}%)")

            st.info(description)

            st.subheader("🛡️ Precautions")
            for p in precautions:
                st.write(f"✔️ {p}")

st.markdown("---")
st.caption("⚡ Powered by Sanket's AI Health Assistant")
