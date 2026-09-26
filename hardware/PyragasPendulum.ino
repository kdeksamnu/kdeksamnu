/*
 * Cathedral Engine: Pyragas Pendulum Stabilizer
 * Target: Arduino Mega 2560 / Teensy 4.0
 * Purpose: Model-free chaos control via time-delayed feedback.
 */

#include <Arduino.h>

// --- Configuration ---
const float K_GAIN = 0.20f;           // Stable corridor: 0.10 <= K <= 0.35
const float DELAY_MS = 11.2f;         // Exact delay matching geopolymer resonance
const int CONTROL_HZ = 1000;          // 1000 Hz control loop (1ms per tick)
const int BUFFER_SIZE = 32;           // Must be > (DELAY_MS / (1000.0 / CONTROL_HZ))

// --- Hardware Pins (Mock/Default) ---
const int ENCODER_SDA = 20;
const int ENCODER_SCL = 21;
const int STEP_PIN = 2;
const int DIR_PIN = 3;
const int ENABLE_PIN = 4;

// --- State Variables ---
struct HistoryFrame {
    unsigned long timestamp_ms;
    float omega; // Angular velocity (rad/s)
};

HistoryFrame omegaHistory[BUFFER_SIZE];
int writeIndex = 0;
int historyCount = 0;

float lastAngle = 0.0f;
unsigned long lastTime = 0;
bool isActuating = false;

void setup() {
    Serial.begin(115200);
    while (!Serial) { ; } // Wait for serial port
    
    pinMode(STEP_PIN, OUTPUT);
    pinMode(DIR_PIN, OUTPUT);
    pinMode(ENABLE_PIN, OUTPUT);
    digitalWrite(ENABLE_PIN, LOW); // Enable driver
    
    // Initialize ring buffer
    for (int i = 0; i < BUFFER_SIZE; i++) {
        omegaHistory[i] = {0, 0.0f};
    }
    lastTime = micros();
    
    Serial.println("[M8 ACTUATOR] Pyragas Pendulum Initialized. Awaiting Cathedral commands.");
}

void loop() {
    // 1. Check for high-level commands from Raspberry Pi
    if (Serial.available() > 0) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd == "ACTUATE") {
            isActuating = true;
            Serial.println("[M8] Pyragas Loop ENGAGED.");
        } else if (cmd == "HALT") {
            isActuating = false;
            Serial.println("[M8] Pyragas Loop DISENGAGED.");
        }
    }

    unsigned long currentTime_us = micros();
    unsigned long currentTime_ms = currentTime_us / 1000;
    float dt = (currentTime_us - lastTime) / 1000000.0f; // seconds
    
    // Enforce ~1000 Hz loop
    if (dt >= 0.001f) {
        lastTime = currentTime_us;
        
        // 2. Measure current state (Mock encoder read for standalone compilation)
        // In production: float currentAngle = readAS5600Angle();
        float currentAngle = lastAngle + (isActuating ? 0.01f : 0.0f); // Mock rotation
        float currentOmega = (currentAngle - lastAngle) / dt;
        lastAngle = currentAngle;
        
        // 3. Compute Pyragas Damping Torque
        float pyragasTorque = computePyragasTorque(currentOmega, currentTime_ms);
        
        // 4. Apply torque to stepper motor
        applyMotorTorque(pyragasTorque);
        
        // 5. Telemetry (throttled to 10 Hz to avoid serial bottleneck)
        static unsigned long lastTelemetry = 0;
        if (currentTime_ms - lastTelemetry >= 100) {
            lastTelemetry = currentTime_ms;
            Serial.print("TELEMETRY|Omega:"); Serial.print(currentOmega, 4);
            Serial.print("|Torque:"); Serial.println(pyragasTorque, 4);
        }
    }
}

float computePyragasTorque(float currentOmega, unsigned long currentTime_ms) {
    if (!isActuating) return 0.0f;

    // 1. Store current state in ring buffer
    omegaHistory[writeIndex] = {currentTime_ms, currentOmega};
    writeIndex = (writeIndex + 1) % BUFFER_SIZE;
    if (historyCount < BUFFER_SIZE) historyCount++;
    
    // 2. Find target historical time
    float targetTime_ms = (float)currentTime_ms - DELAY_MS;
    
    // 3. Locate bracketing indices for linear interpolation
    int lowerIdx = -1, upperIdx = -1;
    float lowerTime = 0, upperTime = 0;
    
    for (int i = 0; i < historyCount; i++) {
        int idx = (writeIndex - i + BUFFER_SIZE) % BUFFER_SIZE;
        if (omegaHistory[idx].timestamp_ms <= targetTime_ms) {
            lowerIdx = idx;
            lowerTime = omegaHistory[idx].timestamp_ms;
            
            int nextIdx = (writeIndex - i + 1 + BUFFER_SIZE) % BUFFER_SIZE;
            if (i + 1 < historyCount) {
                upperIdx = nextIdx;
                upperTime = omegaHistory[nextIdx].timestamp_ms;
            }
            break;
        }
    }
    
    // 4. Interpolate delayed omega: ω(t - τ_d)
    float delayedOmega = 0.0f;
    if (lowerIdx != -1 && upperIdx != -1 && (upperTime - lowerTime) > 0.001f) {
        float t = (targetTime_ms - lowerTime) / (upperTime - lowerTime);
        t = constrain(t, 0.0f, 1.0f);
        delayedOmega = omegaHistory[lowerIdx].omega + t * (omegaHistory[upperIdx].omega - omegaHistory[lowerIdx].omega);
    } else if (lowerIdx != -1) {
        delayedOmega = omegaHistory[lowerIdx].omega; // Fallback
    }
    
    // 5. Pyragas Equation: τ(t) = K * [ω(t - τ_d) - ω(t)]
    return K_GAIN * (delayedOmega - currentOmega);
}

void applyMotorTorque(float torque) {
    // Map torque to stepper driver step pulse frequency and direction.
    // Positive torque = Clockwise, Negative = Counter-Clockwise.
    int stepRate = abs(torque) * 500; // Scaling factor for demo
    bool direction = (torque >= 0);
    
    digitalWrite(DIR_PIN, direction ? HIGH : LOW);
    
    // Simplified step generation (use hardware timers in production)
    if (stepRate > 10) {
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(2);
        digitalWrite(STEP_PIN, LOW);
        delayMicroseconds(max(10000 / stepRate, 2)); // Crude rate limiting
    }
}
