import json

# Define the new solenoid mappings with combinations
solenoid_map = {
    "D1_L": [1],
    "D1_M": [1, 2],
    "D1_H": [1, 2, 3],
    "D2_L": [4],
    "D2_M": [4, 5],
    "D2_H": [4, 5, 6],
    "D3_L": [7],
    "D3_M": [7, 8],
    "D3_H": [7, 8, 9],
    "D4_L": [10],
    "D4_M": [10, 11],
    "D4_H": [10, 11, 12]
}

# Reverse mapping: Convert solenoid numbers back to directional labels (keys as strings)
solenoid_to_direction = {str(v): k for k, v in solenoid_map.items()}

# Generate calibration signals with combinations of solenoids
calibration_signals = [
    {
        "solenoids": solenoid_map[f"D4_{level}"],
        "direction": f"D4_{level}"
    }
    for level in ["L", "M", "H"]
] * 5

# Save to JSON file
data_to_save = {
    "solenoid_map": solenoid_map,  # Store mapping in JSON
    "solenoid_to_direction": solenoid_to_direction,  # Reverse mapping
    "calibration_signals": calibration_signals  # List of signals
}

with open("calibration_signals_patterns.json", "w") as f:
    json.dump(data_to_save, f, indent=4)

# Print signals for verification
for i, signal in enumerate(calibration_signals):
    print(f"Signal {i+1}: {signal}")

# Print total number of signals generated
print(f"\nTotal signals generated: {len(calibration_signals)}")
