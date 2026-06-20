#include <Adafruit_LiquidCrystal.h>
Adafruit_LiquidCrystal lcd1(0);
void setup() {
    lcd1.begin(16, 2);
    lcd1.setCursor(0, 0);
    lcd1.print("Hello, World!");
 	lcd1.setCursor(0, 1);
    lcd1.print("BCSP4C AM");
    delay(1000);
}
void loop() {
    for (int i = 1; i <= 4; i++) {
        lcd1.clear();
        lcd1.setCursor(0, 0);
        lcd1.print("BCSP");
        lcd1.print(i);
        lcd1.print("C AM");
        delay(1000);
    }
}