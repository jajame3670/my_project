#include <Adafruit_LiquidCrystal.h>
const int trig = 14; 
const int echo = 15; 
Adafruit_LiquidCrystal lcd1(0); 
long duration;
float distanceCm;
float distanceinch;
char bufferCm[10];
char bufferInch[10];

void setup() {
    lcd1.begin(16, 2); 
    pinMode(trig, OUTPUT); 
    pinMode(echo, INPUT); 
    }
void loop() {
    digitalWrite(trig, LOW);
    delayMicroseconds(2);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);
    duration = pulseIn(echo, HIGH);
    distanceCm = duration * 0.034 / 2;
    distanceinch = duration * 0.0133 / 2;
    dtostrf(distanceCm, 3, 0, bufferCm);
    dtostrf(distanceinch, 2, 0, bufferInch);
    lcd1.setCursor(0, 0);
    lcd1.print("Distance:");
    lcd1.print(bufferCm);
    lcd1.print(" cm");
    lcd1.setCursor(0, 1);
    lcd1.print("Distance:");
    lcd1.print(bufferInch);
    lcd1.print(" inch");

}

