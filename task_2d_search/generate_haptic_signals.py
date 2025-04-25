import json
import os

# Configuration map
CONFIGS = {
    1: "overload_signals.json",
    2: "pressure_area_signals.json",
    3: "pressure_frequency_signals.json",
    4: "area_frequency_signals.json"
}

# 4x4 grid (X and Y values from 1 to 4)
GRID_POINTS = [(x, y) for x in range(1, 5) for y in range(1, 5)]

# Create signal sets
def generate_signals_for_config(config_id):
    signals = []
    for x, y in GRID_POINTS:
        signal = {
            "signal": [config_id, x, y]
        }
        signals.append(signal)
    return signals

# Save JSON files
def save_all_config_signals(output_dir="signals"):
    os.makedirs(output_dir, exist_ok=True)
    for config_id, filename in CONFIGS.items():
        signals = generate_signals_for_config(config_id)
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            json.dump({"haptic_signals": signals}, f, indent=4)
    print(f"All signal files saved to: {output_dir}")

# Run it
if __name__ == "__main__":
    save_all_config_signals()
