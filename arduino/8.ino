#include <Servo.h>
int pos =0;
int sw1=2;
int sw2=3;
Servo servo_9;
void setup() {
    servo_9.attach(9, 500, 2500);
    pinMode(sw1, INPUT_PULLUP);
    pinMode(sw2, INPUT_PULLUP);
    Serial.begin(9500);
    }
void loop()
{
    int vall1 = digitalRead(sw1);
    int vall2 = digitalRead(sw2);
    if(vall1 == LOW){
        pos--;
        if (pos <0) pos=0;
        servo_9.write(pos);
        delay(15);
        }
        else if(vall2 == LOW){
        pos++;
        if (pos >180) pos=180;
        servo_9.write(pos);
        delay(15);
        }
}