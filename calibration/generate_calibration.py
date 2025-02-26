import pickle

# Define solenoid mappings for a single display (D4 used as an example)
solenoid_map = {
    "D1_L": [1, 4], "D1_M": [2, 4], "D1_H": [3, 4],
    "D2_L": [1, 5], "D2_M": [2, 5], "D2_H": [3, 5],
    "D3_L": [6, 9], "D3_M": [7, 9], "D3_H": [8, 9],
    "D4_L": [6, 10], "D4_M": [7, 10], "D4_H": [8, 10]  # Using D4 as the example display
}

# Generate signals for a single display (D4) with 3 levels, repeated 5 times
calibration_signals = [solenoid_map[f"D4_{level}"] for level in ["L", "M", "H"]] * 5

# Save to file
with open("calibration_signals.pkl", "wb") as f:
    pickle.dump(calibration_signals, f)

# Print signals for verification
for i, signal in enumerate(calibration_signals):
    print(f"Signal {i+1}: {signal}")

# Print total number of signals generated
print(f"\nTotal signals generated: {len(calibration_signals)}")
