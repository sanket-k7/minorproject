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

# ------------------ FUNCTIONS ------------------
def extract_symptoms(text):
    text = text.lower()
    found = []

    for symptom in cols:
        if symptom.replace("_", " ") in text:
            found.append(symptom)

    return list(set(found))


def predict_disease(symptoms):
    input_vector = np.zeros(len(symptoms_dict))

    for s in symptoms:
        if s in symptoms_dict:
            input_vector[symptoms_dict[s]] = 1

    pred = model.predict([input_vector])[0]
    disease = le.inverse_transform([pred])[0]

    return disease

# ------------------ UI DESIGN ------------------

st.set_page_config(page_title="AI Health Assistant", page_icon="💊")

# Sidebar (User Info)
st.sidebar.title("👤 User Details")
name = st.sidebar.text_input("Enter your name")
age = st.sidebar.number_input("Enter your age", min_value=1, max_value=120)

st.title("💊 AI Health Assistant")
st.write("Enter your symptoms below 👇")

# Input box
user_input = st.text_input("Type symptoms (e.g., fever, headache)")

if st.button("Predict"):
    if not user_input:
        st.warning("⚠️ Please enter symptoms")
    else:
        with st.spinner("🤖 Thinking..."):

            symptoms = extract_symptoms(user_input)

            if not symptoms:
                st.error("❌ No symptoms detected")
            else:
                disease = predict_disease(symptoms)

                description = description_list.get(disease, "No description available.")
                precautions = precaution_dict.get(disease, [])

                st.success(f"🦠 Disease: {disease}")

                st.info(f"📖 {description}")

                st.subheader("🛡️ Precautions:")
                if precautions:
                    for p in precautions:
                        st.write("✔️", p)
                else:
                    st.write("No precautions found")

# Footer
st.markdown("---")
st.caption("⚡ Powered by Sanket's AI Health Assistant")
