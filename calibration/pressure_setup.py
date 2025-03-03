import time
import json
import serial

# Initialize serial communication
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
print("[*] Connecting to Arduino...")
time.sleep(2)  # Allow Arduino to initialize
print("[*] Arduino connected.")

# Load calibration signals
with open("calibration_signals.json", "r") as f:
    data = json.load(f)

calibration_signals = data["solenoid_map"]

# Pressure level mapping
P_LEVELS = ["L", "M", "H"]

solenoid_map = data["solenoid_map"]  # Extract solenoid mappings

def send_haptic_signal(solenoids):
    """Send solenoid activation command to Arduino."""
    signal_str = ",".join(map(str, solenoids))  # Convert list to comma-separated string
    arduino.write((signal_str + "\n").encode())  # Send command
    print(f"[*] Actuating solenoids: {solenoids}")

def send_end_signal():
    """Send '0' to Arduino to turn off all solenoids."""
    arduino.write(b"0\n")
    print("[*] Turning off all solenoids.")

while True:
    # Ask user which pressure level to adjust
    pressure_level = input("\nSelect pressure level to adjust (L/M/H) or press 'E' to exit: ").upper()
    
    if pressure_level == "E":
        print("Exiting calibration.")
        break

    if pressure_level not in P_LEVELS:
        print("Invalid input. Please enter L, M, H, or E.")
        continue

    print(f"\nAdjusting pressure level: {pressure_level}\n")

    # **Fix: Build the correct signals dynamically from solenoid_map**
    filtered_signals = {key: solenoid_map[key] for key in solenoid_map if key.endswith(f"_{pressure_level}")}

    if not filtered_signals:
        print(f"No signals found for pressure level {pressure_level}. Check calibration_signals.json.")
        continue

    for direction, solenoids in filtered_signals.items():
        print(f"Actuating {direction} ({solenoids})")
        send_haptic_signal(solenoids)
        input("Press ENTER to continue to next display...")
        send_end_signal()
        time.sleep(2)  # Allow time for deflation

    print("\nCompleted calibration for this level. Returning to selection menu.")
