import numpy as np
import pandas as pd
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
import os
import time

# Email dispatch libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64

# =====================================================================
# CONFIGURATION AND SECURITY CREDENTIALS
# =====================================================================
CHANNEL_ID = "3424735" 
READ_API_KEY = "EFTRI7PYIX0XY9GQ"  
url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=50" if READ_API_KEY else f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results=50"
excel_log = r"c:\Users\DhanushGowda\OneDrive\Desktop\Smart_Insole_AI_Report.xlsx"

# 📧 UPDATED SECURITY CREDENTIALS:
SENDER_EMAIL = "arduinotech444@gmail.com"
SENDER_PASSWORD = "dhanu dhanu dhanu"  
RECEIVER_DOCTOR_EMAIL = "dhanushgowdas@gmail.com"

# =====================================================================
# MEDICAL REPORT EMAIL DISPATCH SYSTEM
# =====================================================================
def send_medical_alert_report(file_path, subject_text, body_text):
    if SENDER_EMAIL == "your_email@gmail.com":
        return "Email skipped (Credentials missing)"

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_DOCTOR_EMAIL
        msg['Subject'] = subject_text
        
        msg.attach(MIMEText(body_text, 'plain'))
        
        if os.path.exists(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(file_path)}",
                )
                msg.attach(part)
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_DOCTOR_EMAIL, msg.as_string())
        server.quit()
        return "Email Sent 📧"
    except Exception as email_error:
        return f"Email Failed ❌ ({email_error})"

# =====================================================================
# PHASE 1 & 2: TRAIN THE RANDOM FOREST BRAIN
# =====================================================================
print("Generating clinical training dataset...")
np.random.seed(42)
num_samples = 20000
X_fsr = np.random.randint(0, 4096, size=(num_samples, 4))
X_temp = np.random.uniform(26.0, 36.0, size=(num_samples, 1))
X = np.hstack((X_fsr, X_temp))

y = np.zeros(num_samples)
for i in range(num_samples):
    if np.max(X_fsr[i]) >= 2200 or X_temp[i][0] >= 32.2:
        y[i] = 1
    else:
        y[i] = 0

dataset = pd.DataFrame(X, columns=['FSR1', 'FSR2', 'FSR3', 'FSR4', 'Temp'])
dataset['Risk_Label'] = y.astype(int)

print("Training Random Forest Classifier model...")
X_train, X_test, y_train, y_test = train_test_split(
    dataset[['FSR1', 'FSR2', 'FSR3', 'FSR4', 'Temp']], dataset['Risk_Label'], test_size=0.2, random_state=42
)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
print(f"Model Training Complete! Validation Accuracy: {accuracy_score(y_test, rf_model.predict(X_test)) * 100:.2f}%\n")

current_tracking_date = datetime.now().date()

print("🚀 AUTOMATION SERVICE STARTED: Tracking active plantar metrics 24/7...")
print("Press Ctrl+C in the terminal to stop manually.\n")

# =====================================================================
# CONTINUOUS TRACKING LOOP (RUNS 24/7 IN BACKGROUND)
# =====================================================================
while True:
    try:
        now = datetime.now()
        today_date = now.date()
        
        # ⏰ MIDNIGHT COMPRESSION AND DOCTOR EMAIL TRIGGER
        if today_date > current_tracking_date:
            print(f"\n📅 Midnight Rollover Detected! Compressing data for yesterday: {current_tracking_date}")
            
            if os.path.exists(excel_log):
                try:
                    master_sheet = pd.read_excel(excel_log)
                    yesterday_str = current_tracking_date.strftime("%Y-%m-%d")
                    raw_yesterday_data = master_sheet[master_sheet['Timestamp'].str.contains(yesterday_str, na=False)].copy()
                    raw_yesterday_data = raw_yesterday_data[pd.to_numeric(raw_yesterday_data['FSR1'], errors='coerce').notna()]
                    
                    if not raw_yesterday_data.empty:
                        avg_fsr1 = round(raw_yesterday_data['FSR1'].astype(float).mean(), 1)
                        avg_fsr2 = round(raw_yesterday_data['FSR2'].astype(float).mean(), 1)
                        avg_fsr3 = round(raw_yesterday_data['FSR3'].astype(float).mean(), 1)
                        avg_fsr4 = round(raw_yesterday_data['FSR4'].astype(float).mean(), 1)
                        avg_temp = round(raw_yesterday_data['Temp'].astype(float).mean(), 2)
                        
                        total_logs = len(raw_yesterday_data)
                        anomaly_logs = raw_yesterday_data['Evaluation'].str.contains("PROBLEM", na=False).sum()
                        anomaly_percentage = round((anomaly_logs / total_logs) * 100, 1) if total_logs > 0 else 0
                        
                        summary_eval = f"DAILY AVERAGE SUMMARY: HEALTHY TRENDS"
                        is_critical_day = False
                        
                        if anomaly_percentage > 15.0:
                            summary_eval = f"DAILY AVERAGE SUMMARY: HIGH PRE-ULCER RISK ({anomaly_percentage}% Anomaly)"
                            is_critical_day = True
                        
                        daily_summary_row = pd.DataFrame([{
                            'Timestamp': f"=== COMPRESSED SUMMARY FOR {yesterday_str} ===",
                            'FSR1': avg_fsr1, 'FSR2': avg_fsr2, 'FSR3': avg_fsr3, 'FSR4': avg_fsr4, 'Temp': avg_temp,
                            'Evaluation': summary_eval,
                            'Confidence_%': f"{100 - anomaly_percentage}% Safe"
                        }])
                        
                        historical_cleaned = master_sheet[~master_sheet['Timestamp'].str.contains(yesterday_str, na=False)]
                        compressed_sheet = pd.concat([historical_cleaned, daily_summary_row], ignore_index=True)
                        compressed_sheet.to_excel(excel_log, index=False)
                        print(f"✅ Memory Saved! Compressed {yesterday_str} records into a single row summary.")
                        
                        if is_critical_day:
                            subject = f"⚠️ CLINICAL ALERT: Diabetic Pre-Ulcer Risk Threshold Exceeded ({yesterday_str})"
                            body = (f"Respected Medical Practitioner,\n\n"
                                    f"This is an automated diagnostic telemetry alert generated by the Smart Insole AI system.\n\n"
                                    f"Patient Record Analysis for Date: {yesterday_str}\n"
                                    f"Plantar Stress Metric: Patient spent {anomaly_percentage}% of active walking cycles in high-risk zones.\n"
                                    f"Mean Core Temperature Profile: {avg_temp}°C\n\n"
                                    f"The complete diagnostic matrix spreadsheet is attached below.\n\n"
                                    f"Regards,\nSmart Insole Analytics Platform")
                            send_medical_alert_report(excel_log, subject, body)
                
                except Exception as compression_error:
                    print(f"⚠️ Data compression / automated email routing failed: {compression_error}")
            
            current_tracking_date = today_date
        
        # 📥 LIVE TELEMETRY ACQUISITION BLOCK
        response_data = requests.get(url).json()
        if isinstance(response_data, dict) and 'feeds' in response_data:
            feeds = response_data['feeds']
            cloud_rows = []
            timestamps = []
            
            for f in feeds:
                try:
                    cloud_rows.append([
                        float(f['field1'] if f['field1'] is not None else 0), 
                        float(f['field2'] if f['field2'] is not None else 0), 
                        float(f['field3'] if f['field3'] is not None else 0), 
                        float(f['field4'] if f['field4'] is not None else 0), 
                        float(f['field5'] if f['field5'] is not None else 0)  
                    ])
                    dt = datetime.strptime(f['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    local_time = dt + timedelta(hours=5, minutes=30)
                    timestamps.append(local_time.strftime("%Y-%m-%d %H:%M:%S"))
                except (TypeError, ValueError, KeyError):
                    continue 
            
            if len(cloud_rows) > 0:
                df_live = pd.DataFrame(cloud_rows, columns=['FSR1', 'FSR2', 'FSR3', 'FSR4', 'Temp'])
                df_live.insert(0, 'Timestamp', timestamps)
                
                active_rows = df_live[(df_live[['FSR1', 'FSR2', 'FSR3', 'FSR4']].sum(axis=1) > 0)].copy()
                
                if active_rows.empty: 
                    print(f"[{now.strftime('%H:%M:%S')}] Appended 0 new active readings to sheet. Status: SHOE IS NOT WORN")
                    data_to_save = pd.DataFrame([{
                        'Timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                        'FSR1': '-', 'FSR2': '-', 'FSR3': '-', 'FSR4': '-', 'Temp': '-',
                        'Evaluation': 'SHOE IS NOT WORN',
                        'Confidence_%': '-'
                    }])
                    contains_anomaly = False
                else:
                    live_predictions = rf_model.predict(active_rows[['FSR1', 'FSR2', 'FSR3', 'FSR4', 'Temp']])
                    live_probabilities = rf_model.predict_proba(active_rows[['FSR1', 'FSR2', 'FSR3', 'FSR4', 'Temp']])
                    
                    evaluations = []
                    confidence_scores = []
                    contains_anomaly = False
                    
                    for idx, pred in enumerate(live_predictions):
                        if pred == 1:
                            evaluations.append("PROBLEM DETECTED")
                            confidence_scores.append(round(live_probabilities[idx][1] * 100, 2))
                            contains_anomaly = True 
                        else:
                            evaluations.append("HEALTHY")
                            confidence_scores.append(round(live_probabilities[idx][0] * 100, 2))
                    
                    active_rows['Evaluation'] = evaluations
                    active_rows['Confidence_%'] = confidence_scores
                    data_to_save = active_rows
                    
                    # 🚀 THIS LINE GUARANTEES THE PRINT PATTERN OUT:
                    if contains_anomaly:
                        status_text = "PROBLEM DETECTED ⚠️"
                        test_subject = f"🧪 LIVE TEST DEMO: Critical Pre-Ulcer Risk Flagged Live!"
                        test_body = ("Hello Dhanush,\n\n"
                                     "The AI model evaluated an active row from ThingSpeak and flagged a PROBLEM DETECTED status.\n\n"
                                     "The spreadsheet report has been packaged and attached below automatically.\n\n"
                                     "Smart Insole AI Platform.")
                        email_status = send_medical_alert_report(excel_log, test_subject, test_body)
                        status_text += f" | Status: {email_status}"
                    else:
                        status_text = "HEALTHY ✅"
                    
                    print(f"[{now.strftime('%H:%M:%S')}] Appended {len(active_rows)} new active readings to sheet. Status: {status_text}")
                
                try:
                    existing_records = pd.read_excel(excel_log)
                    compiled_report = pd.concat([existing_records, data_to_save], ignore_index=True)
                    compiled_report.drop_duplicates(subset=['Timestamp'], keep='first', inplace=True)
                except FileNotFoundError:
                    compiled_report = data_to_save
                
                compiled_report.to_excel(excel_log, index=False)
                
                if contains_anomaly:
                    time.sleep(15)
        
        time.sleep(30)
        
    except Exception as loop_error:
        print(f"Network cycle refresh hiccup: {loop_error}")
        time.sleep(10)