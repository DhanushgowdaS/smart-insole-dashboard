import streamlit as st
import pandas as pd
import requests
import time

API_URL = "https://YOUR_BACKEND_URL.onrender.com/data" 

st.set_page_config(page_title="Smart Footwear Dashboard", layout="wide")
st.title("🥾 Smart Footwear: Real-Time Monitoring")

placeholder = st.empty()

while True:
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            
            if not df.empty:
                with placeholder.container():
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Pressure Trend (FSRs)")
                        st.line_chart(df[['fsr1', 'fsr2', 'fsr3', 'fsr4']])
                    with col2:
                        st.subheader("Temperature Trend")
                        st.line_chart(df[['temp1']])
                    
                    st.subheader("Latest Entries")
                    st.dataframe(df.head(10))
            else:
                st.warning("No data yet.")
        else:
            st.error("Backend error.")
    except Exception as e:
        st.error(f"Connection error: {e}")
    
    time.sleep(5)
    st.rerun()
