import streamlit as st
import pandas as pd
import requests
import os

# --- Configuration ---
# Replace this with the URL of your deployed FastAPI service on Render
API_URL = "https://your-fastapi-service.onrender.com/predict" 

st.title("Smart Footwear: Ulcer Risk Analysis")

# --- UI Controls ---
# We keep these for demo purposes to test the API directly from the UI
st.sidebar.header("Manual Testing")
p_input = st.sidebar.slider('Pressure', 0, 1000, 500)
t_input = st.sidebar.slider('Temperature', 20.0, 50.0, 32.5)

# --- Analysis Logic ---
if st.button("Check Current Status"):
    try:
        # Sending data to your FastAPI backend
        payload = {"pressure": float(p_input), "temp": float(t_input)}
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            prediction = response.json().get("prediction")
            st.write(f"### Analysis Result: {prediction}")
        else:
            st.error("Could not connect to the API service.")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

# --- Data Visualization ---
if st.button("Generate Daily Report"):
    if os.path.exists("daily_log.csv"):
        # Note: In a production setup, you would fetch this from a database 
        # instead of a local CSV file.
        df = pd.read_csv("daily_log.csv", names=["timestamp", "pressure", "temp"])
        st.line_chart(df[["pressure", "temp"]])
    else:
        st.warning("Daily log file not found. Ensure your data logging script is active.")
