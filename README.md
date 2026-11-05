# ESP8266-Based Machine Fault Detection | Edge AI

An Edge AI-based machine monitoring prototype that uses an ADXL345 accelerometer to collect X, Y, and Z-axis vibration data and classify machine conditions using lightweight Decision Tree models running on the ESP8266.

The ESP8266 provides sensor measurements and fault predictions through an HTTP JSON API, while a Python Flask dashboard retrieves and visualizes this data.

## Detected Fault Classes

- Normal
- Imbalance
- Horizontal Misalignment
- Vertical Misalignment

## Hardware Components and Connections

- **ESP8266** development board
- **ADXL345** accelerometer
  - SDA → D2
  - SCL → D1
- **BMP180** temperature and pressure sensor (optional, connected to the same I2C bus)

Both sensors communicate with the ESP8266 over I2C. The system can continue making accelerometer-based predictions even when the BMP180 sensor is not connected.

## Firmware Setup

The ESP8266 firmware is located at:

```text
ESP8266_FaultDetection/Esp8266_edgeai/Esp8266_edgeai.ino
```

To upload the firmware:

1. Install Arduino IDE.
2. Install ESP8266 board support.
3. Install the following libraries:
   - Adafruit ADXL345
   - Adafruit Unified Sensor
   - Adafruit BMP085
4. Open the firmware sketch in Arduino IDE.
5. Select the appropriate ESP8266 board and port.
6. Upload the sketch to the board.

The ESP8266 creates a Wi-Fi access point named `Machine-Monitor` and serves sensor data at:

```text
http://192.168.4.1/data
```

**Important:** Change the default Wi-Fi password in the source code before using the device. The password is also printed to the firmware's serial output, so avoid sharing sensitive serial logs.

## Python Dashboard

The project includes a Flask-based dashboard for visualizing sensor measurements and fault classification results.

### Requirements

- Python 3
- Flask and other dependencies listed in `requirements.txt`

### Installation and Execution

Navigate to the dashboard directory:

```bash
cd ESP8266_FaultDetection/python-dashboard
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the dashboard:

```bash
python app.py
```

Connect your computer to the ESP8266 Wi-Fi network named `Machine-Monitor`, then open:

```text
http://127.0.0.1:5000
```

The dashboard retrieves sensor data from the ESP8266 API at `http://192.168.4.1/data`.

If the ESP8266 uses a different IP address, update the `ESP_URL` value in `app.py`.

## Dataset and Model Training

The repository contains scripts for feature extraction, dataset preparation, model training, and model export.

### 1. MaFaulDa Dataset

The `01_MaFaulDa_Dataset/` directory contains scripts for:

- Feature extraction from the MaFaulDa dataset
- Model training and comparison
- Model export

The raw MaFaulDa dataset is not included in this repository.

Before running the feature extraction script, update the `DATASET_DIR` variable in `02_extract_features.py` to point to your local dataset directory. The script generates a `features.csv` file.

### 2. Synthetic Data

The `02_Synthetic_Data/` directory contains scripts for generating synthetic ADXL345 sensor data and training Decision Tree models.

The synthetic dataset and related model files are also included in this directory.

The synthetic data workflow can be executed using:

```bash
python generate_dataset.py
python 08_train_synthetic_model.py
```

Run these scripts from the appropriate directory.

### 3. Recorded Sensor Data

The `03_Recorded_Sensor_Data/` directory contains scripts for:

- Recording sensor measurements through a serial port
- Comparing recorded datasets
- Training models using recorded sensor data

Before running `record_data.py`, configure the correct serial port in the `PORT` variable.

### 4. Firmware and Model Integration

The `ESP8266_FaultDetection/` directory contains:

- ESP8266 firmware
- Model header files
- Flask-based monitoring dashboard

The repository also includes additional firmware and model variants in the `FaultDetection/` and `SyntheticFaultDetection/` directories.

Install the Python dependencies required by the relevant scripts before running the training workflows.

## HTTP JSON API

The ESP8266 exposes sensor measurements and classification results through the following endpoint:

```http
GET /data
```

Example JSON response:

```json
{
  "x": 0.12,
  "y": 0.34,
  "z": 9.81,
  "temperature": 24.5,
  "pressure": 100812,
  "bmpReady": true,
  "prediction": 0,
  "fault": "Normal"
}
```

The response includes:

| Field | Description |
|---|---|
| `x`, `y`, `z` | Accelerometer measurements |
| `temperature` | Temperature reading from BMP180 |
| `pressure` | Pressure reading from BMP180 |
| `bmpReady` | Indicates whether BMP180 is available |
| `prediction` | Numeric classification result |
| `fault` | Predicted machine condition |

## Security and Limitations

- Change the default Wi-Fi access point password before using the device.
- Avoid exposing sensitive credentials in source code or shared logs.
- The project is intended for educational and prototyping purposes.
- It is not designed to replace industrial safety systems or safety-critical machine protection mechanisms.

## Technologies Used

- **Embedded:** ESP8266, ADXL345, BMP180, I2C
- **Firmware:** Arduino IDE, C++
- **Backend / Dashboard:** Python, Flask
- **Machine Learning:** Decision Tree Classification
- **Communication:** HTTP, JSON, Wi-Fi

