/*
  Train Control Handle Interface (Tichi)

  Reads two pots and outputs values on serial at ~100Hz
*/

const int pin1 = A6;
const int pin2 = A7;

const int rateHz = 100;  // Hz
const int waitTimeMs = 1000 / rateHz;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

// the loop routine runs over and over again forever:
void loop() {
  int pot1 = analogRead(A6);
  int pot2 = analogRead(A7);
  Serial.print(pot1);
  Serial.print(",");
  Serial.println(pot2);

  delay(waitTimeMs);
}
