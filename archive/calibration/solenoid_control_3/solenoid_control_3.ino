const int numSolenoids = 12;
const int solenoidPins[numSolenoids] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};

// Define solenoid groups based on their levels
int group1[] = {1, 4, 7, 10};  // Group 1: solenoids 1, 4, 7, 10
int group2[] = {2, 5, 8, 11};  // Group 2: solenoids 2, 5, 8, 11
int group3[] = {3, 6, 9, 12};  // Group 3: solenoids 3, 6, 9, 12

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

        // We need to act based on which solenoids are in the input
        // Group the solenoids based on their "level"
        bool group1_active = false, group2_active = false, group3_active = false;

        for (int i = 0; i < solenoidCount; i++) {
            int solenoid = solenoids[i];

            if (isInGroup(solenoid, group1, 4)) {
                group1_active = true;
            } else if (isInGroup(solenoid, group2, 4)) {
                group2_active = true;
            } else if (isInGroup(solenoid, group3, 4)) {
                group3_active = true;
            }
        }

        // Now activate only the solenoids that are present in the input
        if (group1_active) {
            activateGroup(solenoids, solenoidCount, group1, 4);  // Activate Group 1
        }
        delay(500);  // Wait between group activations

        if (group2_active) {
            activateGroup(solenoids, solenoidCount, group2, 4);  // Activate Group 2
        }
        delay(500);  // Wait between group activations

        if (group3_active) {
            activateGroup(solenoids, solenoidCount, group3, 4);  // Activate Group 3
        }
    }
}

// Helper function to check if a solenoid is in a specific group
bool isInGroup(int solenoid, int group[], int groupSize) {
    for (int i = 0; i < groupSize; i++) {
        if (group[i] == solenoid) {
            return true;
        }
    }
    return false;
}

// Function to activate a group of solenoids, based on the solenoids present in the input
void activateGroup(int solenoids[], int solenoidCount, int group[], int groupSize) {
    for (int i = 0; i < groupSize; i++) {
        for (int j = 0; j < solenoidCount; j++) {
            if (solenoids[j] == group[i]) {
                digitalWrite(solenoidPins[group[i] - 1], HIGH);  // Turn solenoid on
                Serial.print("Turned on solenoid: ");
                Serial.println(group[i]);
            }
        }
    }
}
