import streamlit as st
import pandas as pd
import requests

API_URL = "https://smart-footwear-api.onrender.com/data"

st.set_page_config(page_title="Smart Footwear Dashboard", layout="wide")
st.title("🥾 Smart Footwear: Real-Time Monitoring")


# Manual Refresh Button
if st.button("Refresh Live Data"):
    st.rerun()

# --- STATUS CLASSIFICATION ---
            def get_status(row):
                # If any FSR reading is above 2000, mark as Critical
                if row[['fsr1', 'fsr2', 'fsr3', 'fsr4']].max() > 2000:
                    return "🔴 Critical"
                elif row[['fsr1', 'fsr2', 'fsr3', 'fsr4']].max() > 1000:
                    return "🟡 Normal"
                else:
                    return "🟢 Good"

            # Create the status column
            df['Status'] = df.apply(get_status, axis=1)

            # Display with the status
            st.subheader("Latest Entries & Status")
            st.dataframe(df.tail(10), use_container_width=True)

# --- DATA FETCHING ---
try:
    response = requests.get(API_URL, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            
            # Layout: Charts
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Pressure Analysis")
                st.line_chart(df[['fsr1', 'fsr2', 'fsr3', 'fsr4']])
            with col2:
                st.subheader("Temperature")
                st.line_chart(df[['temp1']])
            
            # Layout: Data Table
            st.subheader("Latest Entries")
            st.dataframe(df.tail(10))
        else:
            st.warning("No data yet.")
    else:
        st.error(f"Backend returned error: {response.status_code}")
except Exception as e:
    st.error(f"Connection error: {e}")
