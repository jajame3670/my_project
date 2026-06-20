int in1 = 2;
int in2 = 3;
int in3 = 4;
int in4 = 5;
int speecha = 120;
int speechb = 120;
int Ena = 11;
int Enb = 10;
void setup() {
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(Ena, OUTPUT);
  pinMode(Enb, OUTPUT);
    delay(2000);
  //forward
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite (Ena, speecha);

  delay(5000);

  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(Enb, speechb);

  delay(5000);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  analogWrite(Ena, 0);
  analogWrite(Enb, 0);
  //left
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite (Ena, speecha);

  delay(5000);

  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(Enb, speechb);

  delay(5000);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  analogWrite(Ena, 0);
  analogWrite(Enb, 0);
   //forward
   digitalWrite(in1, HIGH);
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite (Ena, speecha);

  delay(5000);

  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(Enb, speechb);

  delay(5000);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  analogWrite(Ena, 0);
  analogWrite(Enb, 0);
//right
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  analogWrite (Ena, speecha);

  delay(5000);

  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(Enb, speechb);

  delay(5000);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  analogWrite(Ena, 0);
  analogWrite(Enb, 0);
//backward
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite (Ena, speecha);

  delay(5000);

  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(Enb, speechb);

  delay(5000);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  analogWrite(Ena, 0);
  analogWrite(Enb, 0);
}
void loop() {
  
}

