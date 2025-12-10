#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <epiwatch_inferencing.h>

Adafruit_MPU6050 mpu;
unsigned long lastTime = 0;
const unsigned long sampleRate = 23; // 43Hz sampling rate (23ms interval)

static bool debug_nn = false;
static float features[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
static int feature_ix = 0;

#define ALERT_PIN 2      
#define BUZZER_PIN 23     
bool alert_active = false;
float seizure_threshold = 0.7;

#define CONFIDENCE_SAMPLES 5
float confidence_history[CONFIDENCE_SAMPLES] = {0};
int confidence_index = 0;
bool confidence_buffer_full = false;

void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10);

  pinMode(ALERT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(ALERT_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  if (!mpu.begin()) {
    Serial.println("ERROR: Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  ei_printf("EpiWatch - Epileptic Motion Detection\n");
  ei_printf("Model: %s\n", EI_CLASSIFIER_PROJECT_NAME);
  ei_printf("Compiled: %s %s\n", __DATE__, __TIME__);
  ei_printf("Seizure threshold: %.2f\n", seizure_threshold);
  ei_printf("Confidence samples for averaging: %d\n", CONFIDENCE_SAMPLES);
  
  Serial.println("READY: System initialized in continuous inference mode");
}


void trigger_alert() {
  alert_active = true;
  digitalWrite(ALERT_PIN, HIGH);
  digitalWrite(BUZZER_PIN, HIGH);
  ei_printf("🚨 SEIZURE DETECTED! Alert activated.\n");
}

void stop_alert() {
  alert_active = false;
  digitalWrite(ALERT_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  ei_printf("✅ Normal activity detected. Alert stopped.\n");
}


int get_feature_data(size_t offset, size_t length, float *out_ptr) {
  memcpy(out_ptr, features + offset, length * sizeof(float));
  return 0;
}


float calculate_average_confidence() {
  if (!confidence_buffer_full && confidence_index < CONFIDENCE_SAMPLES) {
    return 0.0;
  }
  
  float sum = 0.0;
  int samples_to_use = confidence_buffer_full ? CONFIDENCE_SAMPLES : confidence_index;
  
  for (int i = 0; i < samples_to_use; i++) {
    sum += confidence_history[i];
  }
  
  return sum / samples_to_use;
}

void run_inference() {
  ei_impulse_result_t result = {0};

  signal_t features_signal;
  features_signal.total_length = EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE;
  features_signal.get_data = &get_feature_data;

  EI_IMPULSE_ERROR res = run_classifier(&features_signal, &result, debug_nn);
  if (res != EI_IMPULSE_OK) {
    ei_printf("ERROR: Failed to run classifier (%d)\n", res);
    return;
  }

  ei_printf("Predictions (DSP: %d ms, NN: %d ms): ",
            result.timing.dsp, result.timing.classification);
  
  float seizure_confidence = 0.0;
  for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
    ei_printf("  %s: %.5f", result.classification[ix].label, result.classification[ix].value);
    
    if (strcmp(result.classification[ix].label, "seizure") == 0) {
      seizure_confidence = result.classification[ix].value;
    }
  }
  ei_printf("\n");

  confidence_history[confidence_index] = seizure_confidence;
  confidence_index = (confidence_index + 1) % CONFIDENCE_SAMPLES;
  
  if (confidence_index == 0) {
    confidence_buffer_full = true;
  }

  float avg_confidence = calculate_average_confidence();
  ei_printf("Average confidence over %d samples: %.5f\n", 
            confidence_buffer_full ? CONFIDENCE_SAMPLES : confidence_index, avg_confidence);

  if (avg_confidence > seizure_threshold && !alert_active) {
    trigger_alert();
  } else if (avg_confidence <= seizure_threshold && alert_active) {
    stop_alert();
  }
}






void ei_printf(const char *format, ...) {
    static char print_buf[1024] = { 0 };

    va_list args;
    va_start(args, format);
    int r = vsnprintf(print_buf, sizeof(print_buf), format, args);
    va_end(args);

    if (r > 0) {
        Serial.write(print_buf);
    }
}





void loop() {
  if (millis() - lastTime >= sampleRate) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    if (feature_ix < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE) {
      features[feature_ix++] = a.acceleration.x;
      features[feature_ix++] = a.acceleration.y;
      features[feature_ix++] = a.acceleration.z;
      features[feature_ix++] = g.gyro.x;
      features[feature_ix++] = g.gyro.y;
      features[feature_ix++] = g.gyro.z;
    }

    if (feature_ix >= EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE) {
      run_inference();
      feature_ix = 0;
    }

    lastTime = millis();
  }
  
  delay(1);
}

