// # Include Libraries
#include <LiquidCrystal_I2C.h>

// # Intialize LCD
LiquidCrystal_I2C lcd(0x27, 16, 2);

// # Setup
void setup()
{
    Serial.begin(9600);
    lcd.init();
    lcd.backlight();
    lcd.clear();
    pinMode(2, OUTPUT);
    digitalWrite(2, HIGH);
    delay(1000);
    lcd.setCursor(0, 0);
    lcd.print("Fire Alert");
    lcd.setCursor(0, 1);
    lcd.print("System Enabled");
    delay(3000);
    lcd.clear();
}

// # Loop
void loop()
{
    // # Check for Serial Data
    int serial = Serial.available();
    if (serial > 0)
    {
        // # Read Serial Data
        String result = Serial.readStringUntil('\n');

        // # Clear LCD Screen
        lcd.clear();
        lcd.setCursor(0, 0);

        // # Check for 'result'
        if (result == "0")
        {
               lcd.print("Fire Alert");
    lcd.setCursor(0, 1);
    lcd.print("System Enabled");
        }
        else if (result == "1")
        {
            lcd.print("High Alert:");
            lcd.setCursor(0, 1);
            lcd.print("Human Detected");
        }
        else
        {
            lcd.print("Invalid Result");
        }
    }

    // # Add delay
    delay(500);
}
