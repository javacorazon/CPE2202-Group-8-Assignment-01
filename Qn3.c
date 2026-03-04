#include <Arduino.h>

#define BUFFER_SIZE 64

// =======================================================
// TODO: Implement templated CircularBuffer class
// =======================================================

template <typename T>
class CircularBuffer {

private:
  T buffer[BUFFER_SIZE];
  int head;   // Next position to read
  int tail;   // Next position to write
  int count;  // Number of elements currently stored

public:

  CircularBuffer() : head(0), tail(0), count(0) {}

  // TODO: Add an item to the buffer. Return true if successful.
  bool enqueue(T item) {

    // Check if buffer is full
    if (isFull()) {
      return false;
    }

    // Store item at tail position
    buffer[tail] = item;

    // Move tail circularly
    tail = (tail + 1) % BUFFER_SIZE;

    // Increase element count
    count++;

    return true;
  }

  // TODO: Remove an item and store it in 'item'. Return true if successful.
  bool dequeue(T& item) {

    // Check if buffer is empty
    if (isEmpty()) {
      return false;
    }

    // Retrieve value from head
    item = buffer[head];

    // Move head circularly
    head = (head + 1) % BUFFER_SIZE;

    // Decrease count
    count--;

    return true;
  }

  bool isEmpty() {
    return count == 0;
  }

  bool isFull() {
    return count == BUFFER_SIZE;
  }
};

// =======================================================
// Producer–Consumer Simulation
// =======================================================

CircularBuffer<int> sensorDataBuffer;

unsigned long lastProducerTime = 0;
unsigned long lastConsumerTime = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Starting Circular Buffer Demo...");
}

void loop() {

  unsigned long currentMillis = millis();

  // ================= PRODUCER =================
  // Simulate high-speed sensor (1000 Hz -> every 1ms)
  if (currentMillis - lastProducerTime >= 1) {

    lastProducerTime = currentMillis;

    int simulatedSensorValue = random(0, 1000);

    // TODO: Try to add value to buffer.
    // If full, print overflow warning.
    if (!sensorDataBuffer.enqueue(simulatedSensorValue)) {
      Serial.println("Buffer Overflow!");
    }
  }

  // ================= CONSUMER =================
  // Simulate slow processor (10 Hz -> every 100ms)
  if (currentMillis - lastConsumerTime >= 100) {

    lastConsumerTime = currentMillis;

    int processedValue = 0;
    int itemsProcessedThisCycle = 0;

    // TODO: Process all available data
    while (!sensorDataBuffer.isEmpty()) {

      if (sensorDataBuffer.dequeue(processedValue)) {

        Serial.print("Processed: ");
        Serial.println(processedValue);

        itemsProcessedThisCycle++;
      }
    }

    Serial.print("--- Processed ");
    Serial.print(itemsProcessedThisCycle);
    Serial.println(" items this cycle ---");
  }
}

/*
ANALYSIS:
Circular buffer supports FIFO behavior.
Enqueue and dequeue are O(1).
No dynamic allocation used.
Suitable for real-time embedded systems.
*/
