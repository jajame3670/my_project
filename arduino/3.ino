void setup()
{
    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);
    pinMode(5, OUTPUT);
    pinMode(6, OUTPUT);
    pinMode(7, OUTPUT);
 	pinMode(8, OUTPUT);
  	pinMode(9, OUTPUT);
}
void loop()
{
	ZERO();
    ONE();
    TWO();
    THREE();
    FOUR();
    FIVE();
 
}
void ZERO()
{
  digitalWrite(9, LOW);
    digitalWrite(2, HIGH);
    digitalWrite(3, HIGH);
    digitalWrite(4, HIGH);
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
	digitalWrite(7, HIGH);
    digitalWrite(8, HIGH);
    delay(1000);
}
void ONE()
{
  digitalWrite(9, LOW);
    digitalWrite(2, HIGH);
    digitalWrite(3, LOW);
    digitalWrite(4, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
	digitalWrite(7, HIGH);
    digitalWrite(8, HIGH);
  	delay(1000);
}
void TWO()
{
    digitalWrite(9, LOW);
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    digitalWrite(4, HIGH);
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
	digitalWrite(7, HIGH);
    digitalWrite(8, LOW);
    delay(1000);
}
void THREE()
{
    digitalWrite(9, LOW);
    digitalWrite(2, LOW);
    digitalWrite(3, LOW);
    digitalWrite(4, LOW);
    digitalWrite(5, LOW);
    digitalWrite(6, HIGH);
	digitalWrite(7, HIGH);
    digitalWrite(8, LOW);
    delay(1000);
}
void FOUR()
{
    digitalWrite(9, LOW);
    digitalWrite(2, HIGH);
    digitalWrite(3, LOW);
    digitalWrite(4, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
	digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    delay(1000);
}
void FIVE()
{
    digitalWrite(9, LOW);
    digitalWrite(2, LOW);
    digitalWrite(3, HIGH);
    digitalWrite(4, LOW);
    digitalWrite(5, LOW);
    digitalWrite(6, HIGH);
	digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    delay(1000);
}