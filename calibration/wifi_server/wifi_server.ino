#include "WiFiS3.h"

/////// Wi-Fi Credentials //////
char ssid[] = "raad_wifi";        
char pass[] = "raad2046";    

/////// Pin Assignments //////
const int solenoids[] = {10, 11, 12};  // Solenoid pins
const int controlSolenoid = 13;        // Control solenoid for volume
const int pressureSensor = A0;         // Analog pressure sensor

WiFiServer server(80);

void setup() {
    Serial.begin(115200);
    
    // Set Solenoid Pins as Output
    for (int i = 0; i < 3; i++) {
        pinMode(solenoids[i], OUTPUT);
        digitalWrite(solenoids[i], LOW);
    }
    pinMode(controlSolenoid, OUTPUT);
    digitalWrite(controlSolenoid, LOW);
  
    // Connect to Wi-Fi
    Serial.print("Connecting to Wi-Fi...");
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    
    Serial.println("\nConnected to Wi-Fi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    server.begin();  // Start the web server
}

void loop() {
    WiFiClient client = server.available();
    if (client) {
        Serial.println("New Client Connected");
        String request = "";

        while (client.connected()) {
            if (client.available()) {
                char c = client.read();
                request += c;
                Serial.write(c);

                if (c == '\n') {
                    if (request.indexOf("GET /S1") != -1) {
                        activateSolenoid(0);
                    } else if (request.indexOf("GET /S2") != -1) {
                        activateSolenoid(1);
                    } else if (request.indexOf("GET /S3") != -1) {
                        activateSolenoid(2);
                    } else if (request.indexOf("GET /OFF") != -1) {
                        deactivateSolenoids();
                    } else if (request.indexOf("GET /PRESSURE") != -1) {
                        float pressureValue = readPressure();
                        client.print("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n");
                        client.print(pressureValue);
                        break;
                    }

                    // Send HTML Response for Browser Control
                    client.println("HTTP/1.1 200 OK");
                    client.println("Content-Type: text/html");
                    client.println();
                    client.println("<html><body>");
                    client.println("<h2>Solenoid Control</h2>");
                    client.println("<a href='/S1'>Activate Solenoid 1</a><br>");
                    client.println("<a href='/S2'>Activate Solenoid 2</a><br>");
                    client.println("<a href='/S3'>Activate Solenoid 3</a><br>");
                    client.println("<a href='/OFF'>Deactivate All</a><br>");
                    client.println("<a href='/PRESSURE'>Read Pressure</a>");
                    client.println("</body></html>");
                    break;
                }
            }
        }
        delay(10);
        client.stop();
        Serial.println("Client Disconnected");
    }
}

// Activate a Specific Solenoid
void activateSolenoid(int index) {
    for (int i = 0; i < 3; i++) {
        digitalWrite(solenoids[i], LOW);
    }
    digitalWrite(solenoids[index], HIGH);
    digitalWrite(controlSolenoid, HIGH);
}

// Deactivate All Solenoids
void deactivateSolenoids() {
    for (int i = 0; i < 3; i++) {
        digitalWrite(solenoids[i], LOW);
    }
    digitalWrite(controlSolenoid, LOW);
}

// Read Pressure Sensor
float readPressure() {
    int rawValue = analogRead(pressureSensor);
    float voltage = rawValue * (5.0 / 1023.0); // Convert ADC to voltage
    return voltage;
}
