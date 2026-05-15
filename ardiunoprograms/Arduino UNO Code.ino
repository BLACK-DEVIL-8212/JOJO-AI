#include <Servo.h>
Servo motors[5]; // Array for 5 motors
int motorPins[5] = {3, 5, 6, 9, 10}; // PWM pins for ESCs

// Variables for motor speeds
float motorSpeed[5] = {1000, 1000, 1000, 1000, 1000}; // Initial speed for all motors

void setup() {
  Serial.begin(115200);

  // Attach motors to PWM pins
  for (int i = 0; i < 5; i++) {
    motors[i].attach(motorPins[i]);
    motors[i].writeMicroseconds(motorSpeed[i]);
  }
}

void loop() {
  // Check for incoming query from ESP32-CAM
  if (Serial.available() > 0) {
    String query = Serial.readStringUntil('\n');
    query.trim(); // Remove extra spaces or newlines

    // Adjust motor speeds based on the query
    if (query == "UP") {
      moveUp();
    } else if (query == "DOWN") {
      moveDown();
    } else if (query == "LEFT") {
      moveLeft();
    } else if (query == "RIGHT") {
      moveRight();
    } else if (query == "HOVER") {
      hover();
    }
  }
}

void moveUp() {
  motorSpeed[0] += 100; // Increase speed for all motors
  motorSpeed[1] += 100;
  motorSpeed[2] += 100;
  motorSpeed[3] += 100;
  motorSpeed[4] += 100;
  applyMotorSpeeds();
}

void moveDown() {
  motorSpeed[0] -= 100; // Decrease speed for all motors
  motorSpeed[1] -= 100;
  motorSpeed[2] -= 100;
  motorSpeed[3] -= 100;
  motorSpeed[4] -= 100;
  applyMotorSpeeds();
}

void moveLeft() {
  motorSpeed[0] -= 50; // Adjust specific motors for left movement
  motorSpeed[1] += 50;
  applyMotorSpeeds();
}

void moveRight() {
  motorSpeed[0] += 50; // Adjust specific motors for right movement
  motorSpeed[1] -= 50;
  applyMotorSpeeds();
}

void hover() {
  for (int i = 0; i < 5; i++) {
    motorSpeed[i] = 1000; // Reset all motors to base hover speed
  }
  applyMotorSpeeds();
}

void applyMotorSpeeds() {
  for (int i = 0; i < 5; i++) {
    motorSpeed[i] = constrain(motorSpeed[i], 1000, 2000); // Ensure within valid range
    motors[i].writeMicroseconds(motorSpeed[i]);
  }
}
