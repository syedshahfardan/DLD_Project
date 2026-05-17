#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

LiquidCrystal_I2C lcd(0x27, 16, 2); 
Servo gateServo;

const int greenLed = 8;
const int redLed = 7;
const int buzzer = 6;
const int servoPin = 9;

void setup() {
  Serial.begin(9600);
  gateServo.attach(servoPin);
  
  pinMode(greenLed, OUTPUT);
  pinMode(redLed, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  lcd.init();
  lcd.backlight();
  displayIdleMessage();
  
  gateServo.write(0);
  digitalWrite(greenLed, LOW);
  digitalWrite(redLed, LOW);
  
  digitalWrite(buzzer, HIGH); delay(150); digitalWrite(buzzer, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    // Pura message read karo jab tak new line '\n' na mil jaye
    String input = Serial.readStringUntil('\n');
    input.trim(); // Faltu spaces khatam karne ke liye

    if (input.startsWith("W")) {          
      // 'W' ke baad jo bhi hai wo Name hai
      String userName = input.substring(1); 
      handleAccessGranted(userName);
    } 
    else if (input == "0") {     
      handleAccessDenied();
    }
  }
}

void handleAccessGranted(String name) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ACCESS GRANTED");
  lcd.setCursor(0, 1);
  lcd.print("Welcome " + name + "!"); // Dynamic Welcome!

  digitalWrite(greenLed, HIGH);
  digitalWrite(buzzer, HIGH); delay(100); digitalWrite(buzzer, LOW);
  
  gateServo.write(90);         
  delay(5000);                 
  
  gateServo.write(0);          
  digitalWrite(greenLed, LOW);
  displayIdleMessage();
}

void handleAccessDenied() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ACCESS DENIED");
  lcd.setCursor(0, 1);
  lcd.print("Unauthorized!");

  digitalWrite(redLed, HIGH);
  digitalWrite(buzzer, HIGH); delay(1000); digitalWrite(buzzer, LOW);
  
  delay(2000);
  digitalWrite(redLed, LOW);
  displayIdleMessage();
}

void displayIdleMessage() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("  SMART PARKING ");
  lcd.setCursor(0, 1);
  lcd.print(" READY TO SCAN  ");
}