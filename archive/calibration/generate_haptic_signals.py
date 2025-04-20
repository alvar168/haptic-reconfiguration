import json

# Define solenoid activation mapping
solenoid_map = {
    "D1_L": [1, 4], "D1_M": [2, 4], "D1_H": [3, 4],  # North
    "D2_L": [1, 5], "D2_M": [2, 5], "D2_H": [3, 5],  # South
    "D3_L": [6, 9], "D3_M": [7, 9], "D3_H": [8, 9],  # East
    "D4_L": [6, 10], "D4_M": [7, 10], "D4_H": [8, 10]  # West
}

# Reverse mapping: Convert solenoid numbers back to directional labels (keys as strings)
solenoid_to_direction = {str(v): k for k, v in solenoid_map.items()}

# --- Single-display signals (4 displays × 3 levels = 12) ---
single_signals = [
    {
        "solenoids": solenoid_map[f"D{i}_{level}"],
        "direction": f"D{i}_{level}"
    }
    for i in range(2, 5) for level in ["L", "M", "H"]
]

# --- Two-display signals (Valid pairs × all pressure level combinations = 36) ---
# valid_pairs = [("D1", "D3"), ("D1", "D4"), ("D2", "D3"), ("D2", "D4")]
valid_pairs = [("D2", "D3"), ("D2", "D4")]

two_display_signals = [
    {
        "solenoids": solenoid_map[f"{d1}_{level1}"] + solenoid_map[f"{d2}_{level2}"],
        "direction": f"{d1}_{level1} + {d2}_{level2}"
    }
    for (d1, d2) in valid_pairs
    for level1 in ["L", "M", "H"]
    for level2 in ["L", "M", "H"]
]

# --- Combine signals ---
haptic_signals = single_signals + two_display_signals

# --- Save to JSON file ---
data_to_save = {
    "solenoid_map": solenoid_map,  # Store mapping in the JSON file
    "solenoid_to_direction": solenoid_to_direction,  # Reverse mapping (fixed to use strings)
    "haptic_signals": haptic_signals
}

with open("haptic_signals_2.json", "w") as f:
    json.dump(data_to_save, f, indent=4)

# --- Print signals for verification ---
for i, signal in enumerate(haptic_signals):
    print(f"Signal {i+1}: {signal}")

print(f"Total signals generated: {len(haptic_signals)}")  # Should be 48
