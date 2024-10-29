// Builtin LED HIGH/LOW er omvendt så LOW tænder den og HIGH slukker den... åbenbart.

void setup() {
  pinMode(16, INPUT);
  pinMode(14, INPUT);
  pinMode(12, INPUT);
  pinMode(13, INPUT);
  
  pinMode(15, OUTPUT);
  digitalWrite(15, HIGH);

  Serial.begin(9600);
}

void loop() {
  Serial.println(digitalRead(13));
  delay(100);
}