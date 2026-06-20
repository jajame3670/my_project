String txtMsg = "";
unsigned int lastStringLength = txtMsg.length();
void setup()
{
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
  Serial.println("\n\nString length():");
  Serial.println();
}
void loop()
{
    while (Serial.available() > 0 )
    {
        char inChar = Serial.read();
        txtMsg += inChar;
    }
    if (txtMsg.length() != lastStringLength){
        Serial.println(txtMsg);
        Serial.println(txtMsg.length());
        //if the string's longer than 140 characters, complain:
        if (txtMsg.length() < 140)
        {
            Serial.println("That's a perfectly acceptable text message.");
    } else {
        Serial.println("that's too long for txt message.");
    }
    // note the last string length for next time through the loop:
    lastStringLength = txtMsg.length();
}
}
    