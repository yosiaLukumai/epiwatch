### Epileptic Motion Detection Using ESP32 + Edge Impulse

A motion-based epilepsy detection prototype designed to support student safety and real-time monitoring in school environments. The system uses an ESP32-DOIT microcontroller and an MPU-6050 6-axis accelerometer/gyroscope to capture motion data. Using Edge Impulse, the device runs a lightweight machine-learning model directly on the ESP32 (“on-device inference”) to classify seizure-like movement patterns.

This project focuses on detecting abnormal or repetitive motion events, which can be associated with seizure activity. While not a medical diagnostic tool, it provides an affordable and accessible approach for early alerting, research, or assistance in environments where continuous monitoring is needed.

### 🚀 Features

- Real-time accelerometer & gyroscope streaming
- Edge Impulse-trained ML model running on ESP32
- Detection of seizure-like motion patterns
- Low-power, wearable-friendly hardware
- Alert output (buzzer, LED, Wi-Fi message, etc.)
- Simple, low-cost hardware setup