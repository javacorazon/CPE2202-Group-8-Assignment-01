#include <Arduino.h>

// ==================== DATA STRUCTURE ====================

struct SensorData {
  float temperature;
  float humidity;
  int light;
};

// =======================================================
// ================= STEP 1 VERSION ======================
// (Dynamic allocation version - leak fixed)
// =======================================================

// TODO: Step 1 - Identify and fix the memory leak in this function.
// This function dynamically allocates memory for SensorData.
SensorData* readSensorsDynamic() {

  // Allocate memory on heap
  SensorData* data = new SensorData;

  data->temperature = random(200, 300) / 10.0;
  data->humidity    = random(300, 600) / 10.0;
  data->light       = random(0, 1024);

  return data;  // Returned pointer must later be deleted
}

// =======================================================
// ================= STEP 3 VERSION ======================
// (Redesigned efficient version using reference)
// =======================================================

// TODO: Step 3 - Modify this function to accept an existing
// SensorData struct by reference instead of allocating memory.
void readSensors(SensorData& data) {

  // Fill existing struct (no heap allocation)
  data.temperature = random(200, 300) / 10.0;
  data.humidity    = random(300, 600) / 10.0;
  data.light       = random(0, 1024);
}

// =======================================================
// ========================= SETUP ========================
// =======================================================

void setup() {
  Serial.begin(115200);
  while (!Serial);
}

// =======================================================
// ========================= LOOP =========================
// =======================================================

void loop() {

  // ================= STEP 1 TEST =================
  Serial.println("=== Dynamic Allocation Version ===");

  // Allocate memory dynamically
  SensorData* sensorPtr = readSensorsDynamic();

  Serial.print("Free Heap: ");
  Serial.print(ESP.getFreeHeap());
  Serial.print(" | Temp: ");
  Serial.print(sensorPtr->temperature);
  Serial.print(" Hum: ");
  Serial.print(sensorPtr->humidity);
  Serial.print(" Light: ");
  Serial.println(sensorPtr->light);

  // TODO: Step 1 - Add missing code to prevent memory leak.
  // Free the dynamically allocated memory after use.
  delete sensorPtr;

  delay(1000);

  // ================= STEP 3 TEST =================
  Serial.println("\n=== Stack Allocation Version ===");

  // Stack allocation (automatic memory management)
  SensorData sensor;

  readSensors(sensor);

  Serial.print("Free Heap: ");
  Serial.print(ESP.getFreeHeap());
  Serial.print(" | Temp: ");
  Serial.print(sensor.temperature);
  Serial.print(" Hum: ");
  Serial.print(sensor.humidity);
  Serial.print(" Light: ");
  Serial.println(sensor.light);

  delay(2000);
}
/*
ANALYSIS:
Original design used dynamic allocation causing memory leak.
This redesign uses stack allocation.
Advantages:
- No heap fragmentation
- Deterministic timing
- No memory leak risk
This is best practice in embedded systems.
*/
