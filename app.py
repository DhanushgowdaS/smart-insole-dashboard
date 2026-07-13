import streamlit as st
import pandas as pd
import requests
import time

API_URL = "https://smart-footwear-api.onrender.com/data"

# Set wide layout
st.set_page_config(page_title="Smart Footwear Dashboard", layout="wide")

# Use a clean header with a divider
st.title("🥾 Smart Footwear Dashboard")
st.markdown("---")

placeholder = st.empty()

while True:
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                
                with placeholder.container():
                    # Create two main rows
                    row1 = st.columns(2)
                    
                    with row1[0]:
                        st.subheader("Pressure Analysis")
                        st.line_chart(df[['fsr1', 'fsr2', 'fsr3', 'fsr4']])
                    
                    with row1[1]:
                        st.subheader("Temperature")
                        st.line_chart(df[['temp1']])
                    
                    st.markdown("### Recent Sensor Readings")
                    # Display the dataframe with a cleaner, striped look
                    st.dataframe(df.tail(10), use_container_width=True)
            else:
                st.info("No data yet. Waiting for ESP32...")
        else:
            st.error("Backend unreachable.")
    except Exception as e:
        st.error(f"Connection error: {e}")
    
    # 10-second refresh delay
    time.sleep(10)
    st.rerun()
