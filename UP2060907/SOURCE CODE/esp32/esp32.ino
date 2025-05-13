#include <MFRC522v2.h>
#include <MFRC522DriverSPI.h>
#include <MFRC522DriverPinSimple.h>
#include <WiFi.h>
#include <PubSubClient.h>

// RC522 initialisation
MFRC522DriverPinSimple ss_pin(5);
MFRC522DriverSPI driver{ ss_pin };
MFRC522 mfrc522{ driver };

// MQTT & WiFi initialisation
WiFiClient espClient;
PubSubClient client(espClient);

// Using mobile hotspot here for consistency
// wifi connectivity
const char* ssid = "";
const char* password = "";

IPAddress mqtt_server();  // MQTT Broker IP here
const int mqtt_port = 1883;
const char* mqtt_topic = "attendance/request";
const char* mqtt_topic_sub = "attendance/response";

// LED pins
const int greenLedPin = 27;
const int redLedPin = 26;

void connectWifi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);

  int connectionAttempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("............");
    
    // This is for debugging
    // Serial.print("\nStatus: "); 
    // Serial.println(WiFi.status());

    connectionAttempts++;

    if (connectionAttempts >= 100) {
      break;
    }
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected.");
  } else {
    Serial.print("Failed to connect after 20 attempts. Restarting ESP32");
    delay(2000);
    ESP.restart();
  }
}

void connectMQTT() {
  client.setServer(mqtt_server, mqtt_port);

  while (!client.connected()) {
    Serial.print("Connecting to MQTT ");
    if (client.connect("ESP32Client")) {
      Serial.println("connected.");
      client.subscribe(mqtt_topic_sub);
    } else {
      Serial.print("failed. State=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void response(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  //Debugging and testing
  // Serial.print("Message: ");
  // Serial.println(message);

  if (message == "success") {
    Serial.println("Face verification succeeded");
    for (int i = 0; i < 10; i++) {
      digitalWrite (greenLedPin, HIGH);
      delay(500);
      digitalWrite (greenLedPin, LOW);
    }
  } else if (message == "fail") {
    Serial.println("Face verification failed");
    for (int i = 0; i < 10; i++) {
      digitalWrite (redLedPin, HIGH);
      delay(500);
      digitalWrite (redLedPin, LOW);
    }
  }
}

void setup() {
  pinMode (greenLedPin, OUTPUT);
  pinMode (redLedPin, OUTPUT);
  
  // Make sure baud rate is 115200
  Serial.begin(115200);
  mfrc522.PCD_Init();

  connectWifi();
  delay(500);
  connectMQTT();

  client.setCallback(response);
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  client.loop(); // Prevents timeout from lack of transmissions

  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) return;

  String uidString = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      uidString += "0";
    }
    uidString += String(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println(uidString);

  client.publish(mqtt_topic, uidString.c_str());
  delay(1000);
}