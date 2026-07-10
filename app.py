import streamlit as st
import requests
import pandas as pd
import joblib
import sklearn  # Add this line!

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Smart Insole AI Dashboard", page_icon="🦶", layout="wide")

st.title("🦶 Smart Insole Foot Ulcer Detection System")
st.subheader("Real-Time AI Diagnostic Pipeline")
st.markdown("---")

# --- CONFIGURATION ---
THINGSPEAK_CHANNEL_ID = "3424735"
THINGSPEAK_READ_API_KEY = "YGGYV98NS88V19EY" # Make sure this is your READ API Key, not your Write API Key

# --- 1. FETCH LATEST DATA FROM THINGSPEAK ---
@st.cache_data(ttl=5) # Auto-refresh cache every 5 seconds if page is reloaded
def fetch_latest_iot_data():
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds/last.json?api_key={THINGSPEAK_READ_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error connecting to ThingSpeak: {e}")
    return None

data = fetch_latest_iot_data()

if data:
    # Extract fields (mapping to your 15-second averages sent by ESP32)
    timestamp = data.get("created_at", "N/A")
    fsr1 = float(data.get("field1", 0) or 0)
    fsr2 = float(data.get("field2", 0) or 0)
    fsr3 = float(data.get("field3", 0) or 0)
    fsr4 = float(data.get("field4", 0) or 0)
    temp = float(data.get("field5", 0) or 0)

    # --- 2. DISPLAY LIVE SENSOR METRICS ---
    st.markdown(f"**Last Sync Time (UTC):** `{timestamp}`")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("AVG FSR 1", f"{int(fsr1)}")
    col2.metric("AVG FSR 2", f"{int(fsr2)}")
    col3.metric("AVG FSR 3", f"{int(fsr3)}")
    col4.metric("AVG FSR 4", f"{int(fsr4)}")
    col5.metric("AVG TEMP", f"{temp} °C")

    st.markdown("---")

    # --- 3. RUN AI MODEL INFERENCE ---
    st.write("### 🤖 AI Diagnostic Classification Engine")
    
    # Structure features exactly how your model expects them
    features = pd.DataFrame([[fsr1, fsr2, fsr3, fsr4, temp]], 
                            columns=['fsr1', 'fsr2', 'fsr3', 'fsr4', 'temp'])
    
    try:
        # Load your trained model (make sure this file is placed in this folder)
        model = joblib.load("smart_insole_model.pkl") 
        prediction = model.predict(features)[0]   
        
        if prediction == "CRITICAL" or prediction == 1: 
            st.error("🚨 DIAGNOSIS STATUS: CRITICAL PRESSURE DETECTED")
            st.warning("Warning: Sustained high-pressure load profile pattern. Risk of tissue degradation.")
        else:
            st.success("✅ DIAGNOSIS STATUS: NORMAL BEHAVIOR")
            st.info("Patient gait pattern and thermal data are currently within a safe physiological range.")
            
    except FileNotFoundError:
        st.info("💡 (Simulation Mode: Place your trained `smart_insole_model.pkl` file in this folder to run live AI inference.)")
        if (fsr1 + fsr2 + fsr3 + fsr4) > 8000 or temp > 35:
            st.error("🚨 DIAGNOSIS STATUS: CRITICAL PRESSURE DETECTED (Simulated)")
        else:
            st.success("✅ DIAGNOSIS STATUS: NORMAL BEHAVIOR (Simulated)")

else:
    st.warning("Waiting for data stream from ThingSpeak...")

# Add a manual refresh button for the presentation
if st.button("🔄 Refresh Data & Re-Run AI"):
    st.rerun()
