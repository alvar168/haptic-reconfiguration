const int PINS[] = {22, 23, 24, 25, 26, 27, 28, 29, 30, 31}; // Solenoids 1–9 → Pins 22–30
const int t_s = 300; // spacing for area level patterns
const int freqDuration = 2000; // total frequency duration per trial

String input = "";
const int t_signal = 2000;

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 9; i++) {
    pinMode(PINS[i], OUTPUT);
    digitalWrite(PINS[i], LOW);
  }
  Serial.println("Ready for signals.");
}

void loop() {
  if (Serial.available()) {
    input = Serial.readStringUntil('\n');
    input.trim();  // remove trailing newline/space

    if (input == "0") {
      Serial.println("Received RESET command. Deflating all displays.");
      resetAllPins();
      return;
    }
    
    int config, x, y;
    if (sscanf(input.c_str(), "%d,%d,%d", &config, &x, &y) == 3) {
      Serial.print("Received: "); Serial.println(input);
      handleSignal(config, x, y);
      resetAllPins();
    } else {
      Serial.print("Invalid input: "); Serial.println(input);
    }
  }
}

// -------------------------- SIGNAL HANDLER ----------------------------

void handleSignal(int config, int x, int y) {
  switch (config) {
    case 1: // Overload: Pressure (X), Frequency + Area (Y)
      playPressureLevel(mapToPressure(x));
      delay(t_signal);
      resetAllPins();
      delay(500);
      playFrequencyLevel(mapToFrequency(y));
      delay(500);
      playAreaLevel(mapToArea(y));
      delay(t_signal);
      resetAllPins();
      break;
    case 2: // Pressure-Area
      if (x != 0) {
        playPressureLevel(mapToPressure(x));
        delay(t_signal);
        resetAllPins();
        delay(500);
      }
      if (y != 0) {
        playAreaLevel(mapToArea(y));
        delay(t_signal);
        resetAllPins();
      }
      break;

    case 3: // Pressure-Frequency
      if (x != 0) {
        playPressureLevel(mapToPressure(x));
        delay(t_signal);
        resetAllPins();
        delay(500);
      }
      if (y != 0) {
        playFrequencyLevel(mapToFrequency(y));
        delay(t_signal);
        resetAllPins();
      }
      break;

    case 4: // Frequency-Area ############## FIX #############3
      if (x != 0) {
        playAreaLevel(mapToArea(x));
        delay(t_signal);
        resetAllPins();
        delay(500);
      }
      if (y != 0) {
        playFrequencyLevel(mapToFrequency(y));
        delay(t_signal);
        resetAllPins();
      }
      break;

    case 5: // Overload: Pressure + Frequency (X), Area (Y)
      if (x != 0){
        playPressureLevel(mapToPressure_5(x));
        delay(t_signal);
        resetAllPins();
        playFrequencyLevel(mapToFrequency_5(x));
        // delay(t_signal);
        resetAllPins();
        delay(500);
      }
      if (y != 0) {
        Serial.println("Playing Area (Y axis)");
        playAreaLevel(mapToArea_5(y));
        delay(t_signal);
        resetAllPins();
      }
      break;
      
    default:
      Serial.println("Unknown config.");
  }
}

// ------------------------ MAPPING FUNCTIONS --------------------------

int mapToPressure(int point) {
  return constrain(point, 1, 4); // point 1–4 → level 1–4
}

int mapToFrequency(int point) {
  if (point <= 2) return 1; // level 1 → points 1, 2
  else return 2;            // level 2 → points 3, 4
}

int mapToArea(int point) {
  if (point == 1) return 1;
  else if (point <= 3) return 2;
  else return 3;
}

int mapToPressure_5(int point) {
  if (point <= 2) return 1;       // point = 1,2
  else if (point <= 4) return 2;  // point = 3,4
  else if (point <= 6) return 3;  // point = 5,6
  else return 4;                  // point = 7
}

int mapToFrequency_5(int point) {
  if (point <= 4) return 1;       // point = 1-4
  else return 2;                  // point = 5-7
}

int mapToArea_5(int point) {
  if (point == 1) return 1;         // Y = 1
  else if (point == 2) return 2;    // Y = 2
  else return 3;                    // Y = 3
}



// ------------------------- PLAYBACK FUNCTIONS ------------------------

void playPressureLevel(int level) {
  int pin_main = PINS[level - 1];  // solenoid 1–4 → pin 22–25
  int pin_common = PINS[4];        // solenoid 5 → pin 26
  Serial.print("Playing Pressure level "); Serial.println(level);
  digitalWrite(pin_main, HIGH);
  digitalWrite(pin_common, HIGH);
}

void playFrequencyLevel(int level) {
  int pin = PINS[5]; // solenoid 6 → pin 27
  int pin_2 = PINS[9]; //solenoid 10 -> pin 31
  int freqHz = (level == 1) ? 4 : 6;
  int period = 1000 / freqHz;
  int cycles = freqDuration / period;

  Serial.print("Playing Frequency level "); Serial.print(level);
  Serial.print(" ("); Serial.print(freqHz); Serial.println(" Hz)");

  for (int i = 0; i < cycles; i++) {
    digitalWrite(pin, HIGH);
    digitalWrite(pin_2, HIGH);
    delay(period / 2);
    digitalWrite(pin, LOW);
    delay(period / 2);
  }
}

void playAreaLevel(int level) {
  Serial.print("Playing Area level "); Serial.println(level);
  int pin1 = PINS[6]; // solenoid 7 → pin 28
  int pin2 = PINS[7]; // solenoid 8 → pin 29
  int pin3 = PINS[8]; // solenoid 9 → pin 30

  digitalWrite(pin1, HIGH);
  if (level >= 2) {
    delay(t_s);
    digitalWrite(pin2, HIGH);
  }
  if (level == 3) {
    delay(t_s);
    digitalWrite(pin3, HIGH);
  }
}

// ------------------------- UTILITY ------------------------

void resetAllPins() {
  for (int i = 0; i < 9; i++) {
    digitalWrite(PINS[i], LOW);
  }
}
