
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi Credentials
const char* ssid = "Dhanu";
const char* password = "Dhanu...";
const char* serverUrl = "https://smart-footwear-api.onrender.com/log";

// Variables for averaging
int sampleCount = 0;
float sumFSR1 = 0, sumFSR2 = 0, sumFSR3 = 0, sumFSR4 = 0, sumTemp1 = 0;
unsigned long startTime = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi Connected");
  startTime = millis();
}

void loop() {
  // 1. Read sensors every ~100ms and add to sum
  sumFSR1 += analogRead(34); // Change pin as needed
  sumFSR2 += analogRead(36);
  sumFSR3 += analogRead(32);
  sumFSR4 += analogRead(33);
  sumTemp1 += 29.25; // Replace with your actual sensor read function
  sampleCount++;

  // 2. Every 10 seconds, calculate average and send
  if (millis() - startTime >= 10000) {
    float avgFSR1 = sumFSR1 / sampleCount;
    float avgFSR2 = sumFSR2 / sampleCount;
    float avgFSR3 = sumFSR3 / sampleCount;
    float avgFSR4 = sumFSR4 / sampleCount;
    float avgTemp1 = sumTemp1 / sampleCount;

    // Print values to Serial Monitor as requested
    Serial.println("--- Data Updated Successfully ---");
    Serial.printf("Avg FSR1: %.2f | Avg FSR2: %.2f | Avg FSR3: %.2f | Avg FSR4: %.2f | Avg Temp: %.2f\n", 
                  avgFSR1, avgFSR2, avgFSR3, avgFSR4, avgTemp1);

    // Send to server
    sendData(avgFSR1, avgFSR2, avgFSR3, avgFSR4, avgTemp1);

    // Reset for next 10s cycle
    sumFSR1 = sumFSR2 = sumFSR3 = sumFSR4 = sumTemp1 = 0;
    sampleCount = 0;
    startTime = millis();
  }
  delay(100); 
}

void sendData(float f1, float f2, float f3, float f4, float t1) {
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["fsr1"] = f1;
  doc["fsr2"] = f2;
  doc["fsr3"] = f3;
  doc["fsr4"] = f4;
  doc["temp1"] = t1;

  String json;
  serializeJson(doc, json);
  int httpResponseCode = http.POST(json);
  
  if (httpResponseCode > 0) Serial.println("Server Response: " + String(httpResponseCode));
  http.end();
}

