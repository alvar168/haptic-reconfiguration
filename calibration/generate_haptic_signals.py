import pickle

# Example haptic signals (replace with real values)
haptic_signals = [
    {"direction": [1, 0, 0], "magnitude": 0.5},
    {"direction": [0, 1, 0], "magnitude": 0.8},
    {"direction": [-1, 0, 0], "magnitude": 0.3},
    {"direction": [0, -1, 0], "magnitude": 0.7}
]

# Save to a pickle file
with open('haptic_signals.pkl', 'wb') as f:
    pickle.dump(haptic_signals, f)

print("[*] Haptic signals saved successfully!")
