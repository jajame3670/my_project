int sw=9;
int ledGreen=4;
int ledRed=13;
void setup() {
  pinMode(sw, INPUT_PULLUP);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledRed, OUTPUT);
    serial.begin(9600);
}
void void loop()
{
    int vall = digitalRead(sw);
    if(vall==0){
        digitalWrite(ledRed, HIGH);
        digitalWrite(ledGreen, LOW);
        Serial.println(vall);
        delay(500);
    }else{
        digitalWrite(ledRed, LOW);
        digitalWrite(ledGreen, HIGH);
        Serial.println(vall);
    }    
}
