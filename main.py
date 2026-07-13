from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Database setup
DB_NAME = "sensor_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY, fsr1 REAL, fsr2 REAL, fsr3 REAL, fsr4 REAL, temp1 REAL)")
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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 1. Insert new data
    cursor.execute("INSERT INTO readings (fsr1, fsr2, fsr3, fsr4, temp1) VALUES (?,?,?,?,?)",
                   (data.fsr1, data.fsr2, data.fsr3, data.fsr4, data.temp1))
    
    # 2. Circular Buffer: Delete oldest records if we exceed 1000 total entries
    cursor.execute("DELETE FROM readings WHERE id <= (SELECT MAX(id) - 1000 FROM readings)")
    
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/data")
def get_data():
    conn = sqlite3.connect(DB_NAME)
    # Only return the last 100 entries for the dashboard
    cursor = conn.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    data = [{"fsr1": r[1], "fsr2": r[2], "fsr3": r[3], "fsr4": r[4], "temp1": r[5]} for r in rows]
    return data
