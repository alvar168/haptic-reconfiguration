import json

# Define solenoid mappings for a single display (D4 used as example)
solenoid_map = {
    "D1_L": [1, 4], "D1_M": [2, 4], "D1_H": [3, 4],
    "D2_L": [1, 5], "D2_M": [2, 5], "D2_H": [3, 5],
    "D3_L": [6, 9], "D3_M": [7, 9], "D3_H": [8, 9],
    "D4_L": [6, 10], "D4_M": [7, 10], "D4_H": [8, 10]  # Using D4 as the example display
}

# Reverse mapping: Convert solenoid numbers back to directional labels (keys as strings)
solenoid_to_direction = {str(v): k for k, v in solenoid_map.items()}

# Generate signals for a single display (D4) with 3 levels, repeated 5 times
calibration_signals = [
    {
        "solenoids": solenoid_map[f"D4_{level}"],
        "direction": f"D4_{level}"
    }
    for level in ["L", "M", "H"]
] * 5  # Repeat 5 times

# Save to JSON file
data_to_save = {
    "solenoid_map": solenoid_map,  # Store mapping in JSON
    "solenoid_to_direction": solenoid_to_direction,  # Reverse mapping
    "calibration_signals": calibration_signals  # List of signals
}

with open("calibration_signals.json", "w") as f:
    json.dump(data_to_save, f, indent=4)

# Print signals for verification
for i, signal in enumerate(calibration_signals):
    print(f"Signal {i+1}: {signal}")

# Print total number of signals generated
print(f"\nTotal signals generated: {len(calibration_signals)}")
