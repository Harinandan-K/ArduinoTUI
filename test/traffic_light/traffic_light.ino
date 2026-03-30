int STANDARD_DELAY;
int LOW_DELAY = 2000;

void setup() {
  pinMode(3, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(11, OUTPUT);
}

void loop() {
  digitalWrite(3, HIGH);
  delay(STANDARD_DELAY);
  digitalWrite(3, LOW);
  digitalWrite(7, HIGH);
  delay(LOW_DELAY);
  digitalWrite(7, LOW);
  digitalWrite(11, HIGH);
  delay(STANDARD_DELAY);
  digitalWrite(11, LOW);
}
