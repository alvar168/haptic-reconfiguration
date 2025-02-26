import itertools
import pickle

# Define solenoid activation mapping based on new logic
solenoid_map = {
    "D1_L": [1, 4], "D1_M": [2, 4], "D1_H": [3, 4],
    "D2_L": [1, 5], "D2_M": [2, 5], "D2_H": [3, 5],
    "D3_L": [6, 9], "D3_M": [7, 9], "D3_H": [8, 9],
    "D4_L": [6, 10], "D4_M": [7, 10], "D4_H": [8, 10]
}

# --- Single-display signals (4 displays × 3 levels = 12) ---
single_signals = [solenoid_map[f"D{i}_{level}"] for i in range(1, 5) for level in ["L", "M", "H"]]

# --- Two-display signals (Valid pairs × all pressure level combinations = 36) ---
valid_pairs = [("D1", "D3"), ("D1", "D4"), ("D2", "D3"), ("D2", "D4")]

two_display_signals = [
    solenoid_map[f"{d1}_{level1}"] + solenoid_map[f"{d2}_{level2}"]
    for (d1, d2) in valid_pairs
    for level1 in ["L", "M", "H"]
    for level2 in ["L", "M", "H"]
]

# --- Combine signals ---
haptic_signals = single_signals + two_display_signals

# --- Save to file ---
with open("haptic_signals.pkl", "wb") as f:
    pickle.dump(haptic_signals, f)

# --- Print signals for verification ---
for i, signal in enumerate(haptic_signals):
    print(f"Signal {i+1}: {signal}")

print(f"Total signals generated: {len(haptic_signals)}")  # Should be 48
