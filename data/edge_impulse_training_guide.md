# Edge Impulse Training Guide for EpiWatch

## Step 1: Prepare Your Data

First, convert your CSV data to Edge Impulse format:

```bash
cd data
python3 prepare_for_edge_impulse.py -i ../dataset -o edge_impulse_data
```

This creates:
- `training_data.json` - 80% of data for training
- `testing_data.json` - 20% of data for validation

## Step 2: Create Edge Impulse Project

1. **Sign up/Login** at [edgeimpulse.com](https://edgeimpulse.com)
2. **Create new project**: "EpiWatch Motion Detection"
3. **Choose project type**: "Accelerometer data"

## Step 3: Upload Data

### Option A: Web Interface
1. Go to **Data acquisition** tab
2. Click **Upload data**
3. Upload `training_data.json` → Select "Training"
4. Upload `testing_data.json` → Select "Testing"

### Option B: CLI (Recommended)
```bash
# Install Edge Impulse CLI
npm install -g edge-impulse-cli

# Login
edge-impulse-login

# Connect to your project
edge-impulse-uploader edge_impulse_data/training_data.json --category training
edge-impulse-uploader edge_impulse_data/testing_data.json --category testing
```

## Step 4: Create Impulse (Model Architecture)

1. Go to **Impulse design** tab
2. **Input block**: 
   - Window size: `2000ms`
   - Window increase: `1000ms` (50% overlap)
   - Frequency: `50Hz`

3. **Processing block**: Add "Spectral Analysis"
   - Good for motion/vibration patterns
   - Extracts frequency domain features

4. **Learning block**: Add "Neural Network (Keras)"
   - Classification model for normal vs seizure

## Step 5: Configure Spectral Features

1. Go to **Spectral features** tab
2. Click **Save parameters** (use defaults)
3. Click **Generate features**
4. Review the feature explorer - should show clear separation between classes

## Step 6: Train Neural Network

1. Go to **NN Classifier** tab
2. **Network architecture**:
   ```
   Input layer: Auto (based on spectral features)
   Hidden layers: 20 neurons, ReLU activation
   Output layer: 2 classes (normal, seizure)
   ```

3. **Training settings**:
   - Training cycles: `100`
   - Learning rate: `0.0005`
   - Validation set size: `20%`

4. Click **Start training**

## Step 7: Test Model Performance

1. Go to **Model testing** tab
2. Click **Classify all**
3. **Target accuracy**: >85% for seizure detection
4. Review confusion matrix - minimize false negatives

## Step 8: Deploy to ESP32

1. Go to **Deployment** tab
2. Select **Arduino library**
3. **Optimization**: `EON Compiler` (for ESP32)
4. Click **Build**
5. Download the `.zip` file

## Step 9: Integrate with ESP32 Code

```bash
# Extract library to your project
cd /home/yosia/Documents/PlatformIO/Projects/epiwatch
unzip ~/Downloads/ei-epiwatch-arduino-1.0.0.zip -d lib/

# Update platformio.ini
echo "lib_deps = https://github.com/edgeimpulse/inferencing-sdk-arduino" >> platformio.ini
```

## Step 10: Update ESP32 Code

Modify `src/main.cpp` to include:
```cpp
#include <epiwatch_inferencing.h>

// In loop(), replace CSV output with:
if (ei_classifier_classify_continuous(&inference) == EI_IMPULSE_OK) {
    if (inference.classification[1].value > 0.7) { // seizure threshold
        // Trigger alert (buzzer, LED, WiFi)
        digitalWrite(ALERT_PIN, HIGH);
    }
}
```

## Troubleshooting

**Low accuracy?**
- Collect more diverse data (different people, scenarios)
- Increase window size to 3-4 seconds
- Try different processing blocks (Raw data + NN)

**Model too large?**
- Reduce neural network size
- Use EON compiler optimization
- Consider Anomaly Detection instead of Classification

**False alarms?**
- Adjust confidence threshold (0.7 → 0.8+)
- Add more "normal" activity data
- Implement temporal smoothing (3+ consecutive detections)

## Performance Targets

- **Accuracy**: >90%
- **Model size**: <100KB (for ESP32)
- **Inference time**: <50ms
- **Power consumption**: <10mA average