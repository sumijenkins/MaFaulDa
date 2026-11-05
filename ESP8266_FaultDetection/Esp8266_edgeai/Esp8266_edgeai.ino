
#include <Adafruit_ADXL345_U.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085.h>
#include <Wire.h>
#include <math.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "small_fault_model.h"

// ==================== SENSORS ====================

// ADXL345 accelerometer
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

// BMP180 temperature and pressure sensor
Adafruit_BMP085 bmp;
bool bmpReady = false;

// ==================== WIFI CONFIGURATION ====================

const char* ap_ssid = "Machine-Monitor";
const char* ap_password = "makine123";

ESP8266WebServer server(80);

// ==================== SENSOR DATA ====================

// ADXL345 acceleration measurements
float sensorX = 0;
float sensorY = 0;
float sensorZ = 0;

// BMP180 measurements
float temperature = 0;
float pressure = 0;

// Latest fault prediction
int predicted_class = -1;

// Sliding window configuration
const int WINDOW_SIZE = 50;

float x_buffer[WINDOW_SIZE];
float y_buffer[WINDOW_SIZE];
float z_buffer[WINDOW_SIZE];

int buffer_index = 0;

// BMP180 reading timer
unsigned long lastEnvironmentRead = 0;

// Fault class names
const char* class_names[] = {
  "Normal",
  "Imbalance",
  "Horizontal Misalignment",
  "Vertical Misalignment"
};

// ==================== JSON DATA SERVER ====================

void handleData() {
  String json = "{";

  json += "\"x\":" + String(sensorX, 3) + ",";
  json += "\"y\":" + String(sensorY, 3) + ",";
  json += "\"z\":" + String(sensorZ, 3) + ",";

  json += "\"temperature\":" + String(temperature, 2) + ",";
  json += "\"pressure\":" + String(pressure, 2) + ",";

  json += "\"bmpReady\":";
  json += (bmpReady ? "true" : "false");
  json += ",";

  json += "\"prediction\":" + String(predicted_class) + ",";

  json += "\"fault\":\"";

  if (predicted_class >= 0 && predicted_class < 4) {
    json += class_names[predicted_class];
  } else {
    json += "Collecting data...";
  }

  json += "\"}";

  server.sendHeader("Cache-Control", "no-store");
  server.send(200, "application/json", json);
}

// ==================== SETUP ====================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("ESP8266 Edge AI Fault Detection Started");

  // Initialize I2C: SDA = D2, SCL = D1
  Wire.begin(D2, D1);

  // Initialize ADXL345
  if (!accel.begin()) {
    Serial.println("ERROR: ADXL345 sensor not found!");
    
    while (true) {
      delay(10);
    }
  }

  accel.setRange(ADXL345_RANGE_16_G);

  Serial.println("ADXL345 sensor ready.");

  // Initialize BMP180
  bmpReady = bmp.begin();

  if (bmpReady) {
    Serial.println("BMP180 sensor ready.");
  } else {
    Serial.println("WARNING: BMP180 sensor not found.");
    Serial.println("Temperature and pressure readings are unavailable.");
  }

  // Create a Wi-Fi access point
  WiFi.mode(WIFI_AP);

  bool wifiStarted = WiFi.softAP(
    ap_ssid,
    ap_password
  );

  if (wifiStarted) {
    Serial.println();
    Serial.println("Wi-Fi access point started!");

    Serial.print("Network name: ");
    Serial.println(ap_ssid);

    Serial.print("Network password: ");
    Serial.println(ap_password);

    Serial.print("IP address: ");
    Serial.println(WiFi.softAPIP());
  } else {
    Serial.println("ERROR: Failed to start Wi-Fi access point!");
  }

  // Register the JSON data endpoint
  server.on("/data", HTTP_GET, handleData);

  // Root endpoint
  server.on("/", HTTP_GET, []() {
    server.send(
      200,
      "text/plain; charset=utf-8",
      "ESP8266 Machine Monitoring API is running. Access /data for sensor readings."
    );
  });

  // Start the HTTP server
  server.begin();

  Serial.println("HTTP server started.");
  Serial.println("Data endpoint: http://192.168.4.1/data");
  Serial.println();
}

// ==================== MAIN LOOP ====================

void loop() {
  // Handle incoming HTTP requests
  server.handleClient();

  // Read ADXL345 acceleration data
  sensors_event_t event;
  accel.getEvent(&event);

  sensorX = event.acceleration.x;
  sensorY = event.acceleration.y;
  sensorZ = event.acceleration.z;

  // Store measurements in the sliding window
  x_buffer[buffer_index] = sensorX;
  y_buffer[buffer_index] = sensorY;
  z_buffer[buffer_index] = sensorZ;

  buffer_index++;

  // Read BMP180 measurements every second
  if (bmpReady &&
      millis() - lastEnvironmentRead >= 1000) {

    lastEnvironmentRead = millis();

    temperature = bmp.readTemperature();
    pressure = bmp.readPressure() / 100.0f;
  }

  // Run prediction when the window contains 50 samples
  if (buffer_index >= WINDOW_SIZE) {

    float features[18];
    int f_idx = 0;

    float* axes[] = {
      x_buffer,
      y_buffer,
      z_buffer
    };

    // Calculate six statistical features for each axis
    for (int a = 0; a < 3; a++) {

      float sum = 0;
      float sum_sq = 0;

      float min_val = axes[a][0];
      float max_val = axes[a][0];

      for (int i = 0; i < WINDOW_SIZE; i++) {

        float val = axes[a][i];

        sum += val;
        sum_sq += val * val;

        if (val < min_val) {
          min_val = val;
        }

        if (val > max_val) {
          max_val = val;
        }
      }

      float mean = sum / WINDOW_SIZE;

      float variance =
        (sum_sq / WINDOW_SIZE) - (mean * mean);

      float std_dev =
        (variance > 0) ? sqrt(variance) : 0;

      float rms =
        sqrt(sum_sq / WINDOW_SIZE);

      float p2p = max_val - min_val;

      features[f_idx++] = mean;
      features[f_idx++] = std_dev;
      features[f_idx++] = rms;
      features[f_idx++] = p2p;
      features[f_idx++] = min_val;
      features[f_idx++] = max_val;
    }

    // Run the Edge AI fault classification model
    predicted_class = predictFault(features);

    // Shift the sliding window by 25 samples
    for (int i = 0; i < 25; i++) {

      x_buffer[i] = x_buffer[i + 25];
      y_buffer[i] = y_buffer[i + 25];
      z_buffer[i] = z_buffer[i + 25];
    }

    buffer_index = 25;
  }

  delay(10);
}
