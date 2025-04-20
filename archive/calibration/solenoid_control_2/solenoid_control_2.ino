const int numSolenoids = 12;
const int solenoidPins[numSolenoids] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};

// Predefined solenoid groups (1-based index)
int group1[] = {1, 2, 3};  // D1: solenoids 1, 2, 3
int group2[] = {4, 5, 6};  // D2: solenoids 4, 5, 6
int group3[] = {7, 8, 9};  // D3: solenoids 7, 8, 9
int group4[] = {10, 11, 12}; // D4: solenoids 10, 11, 12

void setup() {
    Serial.begin(9600);
    Serial.println("Enter solenoid numbers (comma-separated, e.g., 1,3,5)");

    // Set all solenoid pins as OUTPUT and turn them OFF initially
    for (int i = 0; i < numSolenoids; i++) {
        pinMode(solenoidPins[i], OUTPUT);
        digitalWrite(solenoidPins[i], LOW);  // Start with all solenoids OFF
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

        // Parse input solenoids
        int solenoids[12];
        int solenoidCount = 0;
        int index = 0;

        // Parse the solenoids from the input
        while (index < input.length()) {
            int nextComma = input.indexOf(',', index);
            if (nextComma == -1) nextComma = input.length();

            String solenoidNumStr = input.substring(index, nextComma);
            solenoidNumStr.trim();

            if (solenoidNumStr.length() > 0) {
                int solenoidNum = solenoidNumStr.toInt();
                if (solenoidNum >= 1 && solenoidNum <= numSolenoids) {
                    solenoids[solenoidCount++] = solenoidNum;
                }
            }
            index = nextComma + 1;
        }

        // Now, let's process solenoids by their "level"
        // Solenoids 1, 2, 3, etc., correspond to levels across multiple displays
        for (int i = 0; i < solenoidCount; i++) {
            int solenoid = solenoids[i];

            // Check if the solenoid is part of D1 and pair it with D4 solenoids
            if (solenoid == 1 || solenoid == 2 || solenoid == 3) {
                int pairD4 = solenoid + 9; // Solenoids 1-3 map to 10-12
                activateSolenoidPair(solenoid, pairD4);
            }
        }
    }
}

// Function to activate a pair of solenoids with cascading pattern
void activateSolenoidPair(int solenoid1, int solenoid2) {
    // Activate the solenoids in the cascading order
    digitalWrite(solenoidPins[solenoid1 - 1], HIGH);  // Turn solenoid1 on
    digitalWrite(solenoidPins[solenoid2 - 1], HIGH);  // Turn solenoid2 on

    Serial.print("Turned on solenoid: ");
    Serial.println(solenoid1);
    Serial.print("Turned on solenoid: ");
    Serial.println(solenoid2);

    delay(500);  // 0.5 second delay between activations

    // Activate next solenoids in the sequence
    digitalWrite(solenoidPins[solenoid1 - 1], HIGH);  // Turn solenoid1 + solenoid2 on
    digitalWrite(solenoidPins[solenoid2 - 1], HIGH);

    Serial.print("Turned on solenoid: ");
    Serial.println(solenoid1);
    Serial.print("Turned on solenoid: ");
    Serial.println(solenoid2);

    delay(500);  // Wait again before turning on final solenoid
    digitalWrite(solenoidPins[solenoid1 - 1], HIGH);  // Turn solenoid1+solenoid2 on
    digitalWrite(solenoidPins[solenoid2 - 1], HIGH);  // Final sequence here

    delay(500);  // Final waiting
}

