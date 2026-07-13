from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

# Initialize FastAPI
app = FastAPI()

# 1. Define the data structure to match the ESP32 JSON
class SensorData(BaseModel):
    fsr1: int
    fsr2: int
    fsr3: int
    fsr4: int
    temp1: float
    temp2: float

# 2. Load your pre-trained ML model (ensure 'model.pkl' is in your repo)
# model = joblib.load('model.pkl') 

@app.get("/")
def read_root():
    return {"message": "Smart Footwear API is running!"}

# 3. Endpoint for ESP32 to send data
@app.post("/log")
async def log_data(data: SensorData):
    # Here you can process the data
    print(f"Received FSR Data: {data.fsr1}, {data.fsr2}, {data.fsr3}, {data.fsr4}")
    print(f"Received Temp Data: {data.temp1}, {data.temp2}")
    
    # Example: If you have your ML model ready:
    # input_features = [[data.fsr1, data.fsr2, data.fsr3, data.fsr4, data.temp1, data.temp2]]
    # prediction = model.predict(input_features)
    
    # For now, returning a sample prediction
    return {"status": "success", "prediction": 0}
