// #include <Arduino.h>
// #include <Adafruit_MPU6050.h>
// #include <Adafruit_Sensor.h>
// #include <Wire.h>

// Adafruit_MPU6050 mpu;
// unsigned long lastTime = 0;
// const unsigned long sampleRate = 23; // 43Hz sampling rate (23ms interval)
// bool dataCollection = false;

// void setup() {
//   Serial.begin(115200);
//   while (!Serial)
//     delay(10);

//   if (!mpu.begin()) {
//     Serial.println("ERROR: Failed to find MPU6050 chip");
//     while (1) {
//       delay(10);
//     }
//   }

//   mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
//   mpu.setGyroRange(MPU6050_RANGE_500_DEG);
//   mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

//   Serial.println("READY: Data collection mode initialized");
//   Serial.println("Send 'START' to begin data collection");
//   Serial.println("Send 'STOP' to end data collection");
// }

// void loop() {
//   if (Serial.available() > 0) {
//     String command = Serial.readStringUntil('\n');
//     command.trim();
    
//     if (command == "START") {
//       dataCollection = true;
//       Serial.println("DATA_COLLECTION_STARTED");
//     } else if (command == "STOP") {
//       dataCollection = false;
//       Serial.println("DATA_COLLECTION_STOPPED");
//     }
//   }

//   if (dataCollection && (millis() - lastTime >= sampleRate)) {
//     sensors_event_t a, g, temp;
//     mpu.getEvent(&a, &g, &temp);

//     Serial.print(millis());
//     Serial.print(",");
//     Serial.print(a.acceleration.x, 4);
//     Serial.print(",");
//     Serial.print(a.acceleration.y, 4);
//     Serial.print(",");
//     Serial.print(a.acceleration.z, 4);
//     Serial.print(",");
//     Serial.print(g.gyro.x, 4);
//     Serial.print(",");
//     Serial.print(g.gyro.y, 4);
//     Serial.print(",");
//     Serial.println(g.gyro.z, 4);

//     lastTime = millis();
//   }
  
//   delay(1);
// }