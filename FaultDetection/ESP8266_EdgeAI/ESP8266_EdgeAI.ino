
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include "small_fault_model.h"

#define SDA_PIN D2
#define SCL_PIN D1

const int SAMPLE_COUNT = 500;
const int FEATURE_COUNT = 18;

Adafruit_ADXL345_Unified adxl = Adafruit_ADXL345_Unified(12345);
Eloquent::ML::Port::DecisionTree model;

const char* className(int prediction) {
  switch (prediction) {
    case 0: return "Normal";
    case 1: return "Imbalance";
    case 2: return "Horizontal_Misalignment";
    case 3: return "Vertical_Misalignment";
    default: return "Unknown";
  }
}

void calculateFeatures(float data[], float features[], int offset) {
  float sum = 0.0;
  float sumSquares = 0.0;
  float minVal = data[0];
  float maxVal = data[0];

  for (int i = 0; i < SAMPLE_COUNT; i++) {
    float v = data[i];
    sum += v;
    sumSquares += v * v;
    if (v < minVal) minVal = v;
    if (v > maxVal) maxVal = v;
  }

  float mean = sum / SAMPLE_COUNT;
  float variance = 0.0;

  for (int i = 0; i < SAMPLE_COUNT; i++) {
    float diff = data[i] - mean;
    variance += diff * diff;
  }

  float stdDev = sqrt(variance / SAMPLE_COUNT);
  float rms = sqrt(sumSquares / SAMPLE_COUNT);

  features[offset]     = mean;
  features[offset + 1] = stdDev;
  features[offset + 2] = rms;
  features[offset + 3] = minVal;
  features[offset + 4] = maxVal;
  features[offset + 5] = maxVal - minVal;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);

  if (!adxl.begin()) {
    Serial.println("HATA: ADXL345 bulunamadi.");
    while (true) delay(1000);
  }

  adxl.setRange(ADXL345_RANGE_4_G);
  adxl.setDataRate(ADXL345_DATARATE_100_HZ);

  Serial.println();
  Serial.println("ESP8266 Edge AI baslatildi.");
  Serial.println("Her 5 saniyede bir tahmin yapilacak.");
}

void loop() {
  static float xData[SAMPLE_COUNT];
  static float yData[SAMPLE_COUNT];
  static float zData[SAMPLE_COUNT];
  float features[FEATURE_COUNT];

  for (int i = 0; i < SAMPLE_COUNT; i++) {
    sensors_event_t event;
    adxl.getEvent(&event);

    xData[i] = event.acceleration.x;
    yData[i] = event.acceleration.y;
    zData[i] = event.acceleration.z;

    delay(10);
  }

  calculateFeatures(xData, features, 0);
  calculateFeatures(yData, features, 6);
  calculateFeatures(zData, features, 12);

  int prediction = model.predict(features);

  Serial.print("Tahmin: ");
  Serial.println(className(prediction));

  Serial.println("Ozellikler:");
  for (int i = 0; i < FEATURE_COUNT; i++) {
    Serial.print(features[i], 4);
    if (i < FEATURE_COUNT - 1) Serial.print(", ");
  }
  Serial.println();
  Serial.println("--------------------");
}
