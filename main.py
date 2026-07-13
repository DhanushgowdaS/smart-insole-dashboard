from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import joblib
import os

app = FastAPI()

DB_NAME = "sensor_data.db"
# Use absolute path to ensure the model is found regardless of the working directory
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Safely load the ML model
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        model = None
        print(f"Warning: Model file not found at {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    fsr1 REAL, fsr2 REAL, fsr3 REAL, fsr4 REAL, temp1 REAL, status TEXT)""")
    conn.commit()
    conn.close()

init_db()

class SensorData(BaseModel):
    fsr1: float
    fsr2: float
    fsr3: float
    fsr4: float
    temp1: float

@app.post("/log")
def log_data(data: SensorData):
    # ML Prediction with fallback
    status = "Unknown"
    if model:
        try:
            features = [[data.fsr1, data.fsr2, data.fsr3, data.fsr4, data.temp1]]
            prediction = model.predict(features)[0]
            status_map = {0: "Good", 1: "Normal", 2: "Critical"}
            status = status_map.get(prediction, "Unknown")
        except Exception as e:
            print(f"ML Prediction error: {e}")
            status = "Normal" # Default fallback
    else:
        status = "Normal" # Default if no model loaded

    # Save to Database
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO readings (fsr1, fsr2, fsr3, fsr4, temp1, status) VALUES (?,?,?,?,?,?)",
                       (data.fsr1, data.fsr2, data.fsr3, data.fsr4, data.temp1, status))
        
        # Keep only the last 1000 entries
        cursor.execute("DELETE FROM readings WHERE id <= (SELECT MAX(id) - 1000 FROM readings)")
        
        conn.commit()
        conn.close()
        return {"status": "success", "ml_result": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data")
def get_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.execute("SELECT fsr1, fsr2, fsr3, fsr4, temp1, status FROM readings ORDER BY id DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()
    return [{"fsr1": r[0], "fsr2": r[1], "fsr3": r[2], "fsr4": r[3], "temp1": r[4], "status": r[5]} for r in rows]
