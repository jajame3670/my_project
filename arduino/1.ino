char x;
void setup()
{
  Serial.begin(9600);
}
void loop()
{
  if(Serial.available() > 0)
  {
    x = Serial.read();
    if(x == 'U'){
      Serial.println("U");
    }else{
      Serial.println("error");
    }
  }
}