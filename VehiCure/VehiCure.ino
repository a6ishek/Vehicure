#include <ESP8266WiFi.h>
#include "ThingSpeak.h" // always include thingspeak header file after other header files and custom macros
#include "SparkFun_SGP30_Arduino_Library.h" // Click here to get the library: http://librarymanager/All#SparkFun_SGP30
#include <Wire.h>

SGP30 mySensor; //create an object of the SGP30 class

char ssid[] = "OnePlus Nord";   // your network SSID (name) 
char pass[] = "abishek1";   // your network password
int keyIndex = 0;            // your network key Index number (needed only for WEP)
WiFiClient  client;

unsigned long myChannelNumber = 2237374;
const char * myWriteAPIKey = "PBE3QW3O1X8OSVYU";

unsigned long previousMillis = 0;  // will store last time LED was updated
const long interval = 20000;  // interval at which to blink (milliseconds)

int co2,tvoc;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);  // Initialize serial
  Wire.begin();

  WiFi.mode(WIFI_STA); 
  ThingSpeak.begin(client);  // Initialize ThingSpeak

  if (mySensor.begin() == false) {
    Serial.println("No SGP30 Detected. Check connections.");
    while (1);
  }
  mySensor.initAirQuality();

}

void loop() {


  // put your main code here, to run repeatedly:
  if(WiFi.status() != WL_CONNECTED){
    Serial.print("Attempting to connect to SSID: ");
    Serial.println("EMCOG_LAB");
    while(WiFi.status() != WL_CONNECTED){
      WiFi.begin(ssid, pass);  // Connect to WPA/WPA2 network. Change this line if using open or WEP network
      Serial.print(".");
      delay(10000);     
    } 
    Serial.println("\nConnected.");
  }
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
      // save the last time you blinked the LED
    previousMillis = currentMillis;

    co2 = mySensor.CO2;
    tvoc = mySensor.TVOC; 
    mySensor.measureAirQuality();
    Serial.print("CO2: ");
    Serial.print(co2);
    Serial.print(" ppm\tTVOC: ");
    Serial.print(tvoc);
    Serial.println(" ppb");

    ThingSpeak.setField(1, co2);
    ThingSpeak.setField(2, tvoc);

    int x = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
    if(x == 200){
      Serial.println("Channel update successful.");
    }
    else{
      Serial.println("Problem updating channel. HTTP error code " + String(x));
    }
  }

}
