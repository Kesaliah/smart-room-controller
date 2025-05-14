#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "HONOR X6b";
const char* password = "Friday@12";
const char* serverBaseURL = "http://172.16.57.231:5000";

// Pin definitions
#define BUTTON_PIN 36
#define LED_PIN 38
#define ANALOG_INPUT_PIN 3
#define ANALOG_OUTPUT_PIN 40

// Timer variables
unsigned long previousMillis = 0;
const long interval = 500;

void setup() {
  Serial.begin(115200);

  // Setup pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  pinMode(ANALOG_OUTPUT_PIN, OUTPUT);

  // Connect to WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis > interval) {
    previousMillis = currentMillis;

    // Read sensor data and button state
    int analogValue = analogRead(ANALOG_INPUT_PIN);
    bool buttonState = !digitalRead(BUTTON_PIN); // Active LOW
    int new_val = map(analogValue, 0, 4095, 0, 10); // ESP32 ADC is 12-bit (0-4095)

    Serial.print("Analog Input: ");
    Serial.println(analogValue);
    Serial.print("Button State: ");
    Serial.println(buttonState ? "Pressed" : "Released");

    // POST sensor data to the Flask backend
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      String postURL = String(serverBaseURL) + "/esp/update";
      http.begin(postURL);
      http.addHeader("Content-Type", "application/json");

      // Prepare JSON payload
      StaticJsonDocument<200> postDoc;
      postDoc["ldr"] = new_val;
      postDoc["pir"] = buttonState;

      String jsonPayload;
      serializeJson(postDoc, jsonPayload);

      int postResponseCode = http.POST(jsonPayload);
      if (postResponseCode > 0) {
        String response = http.getString();
        Serial.print("POST response code: ");
        Serial.println(postResponseCode);
        Serial.print("Response: ");
        Serial.println(response);
      } else {
        Serial.print("Error on POST: ");
        Serial.println(http.errorToString(postResponseCode));
      }
      http.end();

      // GET control commands from the Flask backend
      HTTPClient http2;
      String getURL = String(serverBaseURL) + "/esp/control";
      http2.begin(getURL);

      int getResponseCode = http2.GET();
      if (getResponseCode > 0) {
        String response2 = http2.getString();

        Serial.print("GET response code: ");
        Serial.println(getResponseCode);
        Serial.print("Response: ");
        Serial.println(response2);

        // Parse JSON control response
        StaticJsonDocument<200> getDoc;
        DeserializationError error = deserializeJson(getDoc, response2);
        if (!error) {
          bool ledControl = getDoc["led"];
          int analogOutputValue = getDoc["analog_output"];

          // Set LED
          digitalWrite(LED_PIN, ledControl ? HIGH : LOW);

          // Set analog output (ESP32 uses DAC only on GPIO25 & GPIO26)
          analogWrite(ANALOG_OUTPUT_PIN, analogOutputValue);

          Serial.print("Set LED to: ");
          Serial.println(ledControl ? "ON" : "OFF");
          Serial.print("Set Analog Output (DAC) to: ");
          Serial.println(analogOutputValue);
        } else {
          Serial.print("JSON parse error: ");
          Serial.println(error.c_str());
        }
      } else {
        Serial.print("Error on GET: ");
        Serial.println(http2.errorToString(getResponseCode));
      }
      http2.end();
    } else {
      Serial.println("WiFi not connected");
    }
  }
}

