# EpiWatch - Epileptic Motion Detection Project

## Project Overview
This is a motion-based epilepsy detection prototype using ESP32 and Edge Impulse for real-time monitoring in educational environments. The system uses an MPU-6050 sensor and on-device machine learning to detect seizure-like movement patterns.

## Hardware Components
- ESP32-DOIT microcontroller
- MPU-6050 6-axis accelerometer/gyroscope
- Buzzer, LED, and Wi-Fi capabilities for alerts

## Development Environment
- Platform: PlatformIO
- Target: ESP32
- ML Framework: Edge Impulse

## Key Features
- Real-time sensor data streaming
- On-device ML inference
- Low-power wearable design
- Multi-modal alert system
- Affordable hardware setup

## Purpose
This is a defensive safety tool designed to assist with student monitoring and early alert systems. It's not intended as a medical diagnostic device but rather as an assistive technology for educational environments.

## Build Commands
To build this project:
```bash
pio run
```

To upload to device:
```bash
pio run --target upload
```

To monitor serial output:
```bash
pio device monitor
```

## Data Collection & Training

### Collect Sensor Data
```bash
cd data
python3 script_collector.py -p /dev/ttyUSB0 -l "normal" -o ../dataset/normal.csv -d 60
python3 script_collector.py -p /dev/ttyUSB0 -l "seizure" -o ../dataset/seizure.csv -d 60
```

### Prepare Data for Edge Impulse
```bash
python3 prepare_for_edge_impulse.py -i ../dataset -o edge_impulse_data
```

### Train Model
Follow the comprehensive guide in `data/edge_impulse_training_guide.md`

### Required Dependencies
```bash
pip install pandas numpy pyserial
npm install -g edge-impulse-cli
```