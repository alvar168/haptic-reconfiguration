const int numSolenoids = 12;
const int solenoidPins[numSolenoids] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};

void setup() {
    Serial.begin(9600);
    Serial.println("Enter solenoid numbers (comma-separated, e.g., 1,3,5)");
    
    // Set all solenoid pins as OUTPUT and turn them OFF initially
    for (int i = 0; i < numSolenoids; i++) {
        pinMode(solenoidPins[i], OUTPUT);
        digitalWrite(solenoidPins[i], LOW);
    }
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');  // Read input line
        input.trim();  // Remove spaces and newlines
        Serial.println("Received: " + input);  // Debugging line

        // Turn OFF all solenoids before processing new input
        for (int i = 0; i < numSolenoids; i++) {
            digitalWrite(solenoidPins[i], LOW);
        }

        // **Check for "no solenoid" command**
        if (input.length() == 0 || input == "0" || input == "none") {
            Serial.println("All solenoids OFF.");
            return;  // Exit early
        }

        int index = 0;
        Serial.print("Parsed solenoids: ");  // New debugging line
        while (index < input.length()) {
            int nextComma = input.indexOf(',', index);
            if (nextComma == -1) nextComma = input.length();

            String solenoidNumStr = input.substring(index, nextComma);
            solenoidNumStr.trim();

            if (solenoidNumStr.length() > 0) {
                int solenoidNum = solenoidNumStr.toInt();

                if (solenoidNum >= 1 && solenoidNum <= numSolenoids) {
                    digitalWrite(solenoidPins[solenoidNum - 1], HIGH);
                    Serial.print(solenoidNum);  // Print which solenoids are being turned on
                    Serial.print(" ");
                } else {
                    Serial.print("Invalid solenoid number: ");
                    Serial.println(solenoidNumStr);
                }
            }
            index = nextComma + 1;
        }

        // Print active solenoids
        Serial.print("Active Solenoids: ");
        bool anyActive = false;
        for (int i = 0; i < numSolenoids; i++) {
            if (digitalRead(solenoidPins[i]) == HIGH) {
                Serial.print(i + 1);
                Serial.print(" ");
                anyActive = true;
            }
        }
        if (!anyActive) Serial.print("None");
        Serial.println();
    }
}

