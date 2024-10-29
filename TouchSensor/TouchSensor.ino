// Builtin LED HIGH/LOW er omvendt så LOW tænder den og HIGH slukker den... åbenbart.

void setup() {
  pinMode(14, INPUT);
  pinMode(13, INPUT);

  Serial.begin(9600);
}

void loop() {
  Serial.print(digitalRead(13));
  Serial.print(",");
  Serial.println(digitalRead(14));
  delay(100);
}