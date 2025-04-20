import time
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import serial
import random
import pickle
import os

# Initialize serial communication with Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
print('[*] Connecting to Arduino')
time.sleep(2)  # Wait for Arduino to initialize
print('[*] Arduino connected')


# For pkl files
# def loadHapticSignals() -> list:
#     """Load haptic signal parameters for each trial and shuffle order."""
#     with open('calibration_signals.pkl', 'rb') as f:
#         signals = pickle.load(f)
#     random.shuffle(signals)  # Shuffle the trials for random order
#     print(signals)
#     return signals
    
# def send_haptic_signal(haptic_signal):
#     """Send haptic signal to Arduino via serial."""
#     signal_str = ",".join(map(str, haptic_signal))  # Convert list to comma-separated string
#     arduino.write((signal_str + "\n").encode())  # Send to Arduino
#     print(f"[*] Sending haptic signal: {signal_str}")

# For JSON files
def loadHapticSignals() -> list:
    """Load haptic signal parameters and ensure calibration signals come first."""
    with open('calibration_signals.json', 'r') as f:
        data = json.load(f)
    
    signals = data["calibration_signals"]  # Extract list of signals

    # Separate calibration and experimental signals
    calibration_signals = signals[0:3]

    # Shuffle only the experimental trials
    random.shuffle(signals)

    # print(f"Loaded {len(ordered_signals)} signals (Calibration: {len(calibration_signals)}, Trials: {len(remaining_signals)})")
    return calibration_signals, signals

def send_haptic_signal(haptic_signal):
    """Send haptic signal to Arduino via serial."""
    signal_str = ",".join(map(str, haptic_signal["solenoids"]))  # Extract solenoid numbers
    arduino.write((signal_str + "\n").encode())  # Send to Arduino
    print(f"[*] Sending haptic signal: {signal_str} ({haptic_signal['direction']})")

def send_end_signal():
    """Send '0' to Arduino to close all solenoids."""
    arduino.write(b"0\n")
    print("[*] Sending deflate signal: 0")


# ------- ASK FOR USER METADATA ---------
user_id = input("Enter participant ID: ")
hand = input("Enter hand used (L/R): ").upper()  # Standardize to uppercase
device_type = input("Enter display type (Ring, Bracelet, etc.): ")
display_id = input("Enter display ID (Index-D4, Middle-D1, Ring-D3, Pinky-D2, Bracelet D2, etc.): ")  # Specific location

# ------- FORMAT FILENAME WITH METADATA ---------
file_name = f"F_{user_id}_{device_type}_{hand}.json"

# ------- GET HAPTIC SIGNAL LIST ---------
calibration_signals, haptic_signals = loadHapticSignals()
TOTAL_TRIALS = len(haptic_signals)
FREQ_LEVELS = ["L", "M", "H"]

# ------- DATA STORAGE ---------
responses = np.zeros(TOTAL_TRIALS, dtype=int)
response_times = np.zeros(TOTAL_TRIALS)


# ------- SOLENOID MAPPING (D4 FREQ LEVELS) ---------
signal_to_label = {
    (6, 10): 1,  # D4_L → L = 1
    (7, 10): 2,  # D4_M → M = 2
    (8, 10): 3   # D4_H → H = 3
}

# Reverse mapping for numeric responses to labels
label_to_signal = {1: "D4_L",
                   2: "D4_M", 
                   3: "D4_H"}


# ------- CALIBRATION PHASE ---------
print("\nCalibration Phase: Familiarizing with Pressure Levels")

for signal in calibration_signals:
    
    print(f"Applying Freq Level: {signal}")
    send_haptic_signal(signal)
    input('Press ENTER to continue')
    send_end_signal()
    time.sleep(2)

input("\nTesting Phase: Press Enter to Start\n")

# ------- EXPERIMENT LOOP ---------
for i, haptic_signal in enumerate(haptic_signals):
        # print(f"\nTrial {i + 1}/{TOTAL_TRIALS}: Applying Frequency Level...")
    # print(f"Trial {i + 1}/{TOTAL_TRIALS}: Applied {FREQ_LEVELS[i % len(FREQ_LEVELS)]}")
    print(f"Trial {i + 1}/{TOTAL_TRIALS}: Applied {haptic_signal['direction']}")

    # Activate Solenoid
    send_haptic_signal(haptic_signal)
    
    # Start Response Timer
    start_time = time.time()

    # Collect User Response
    while True:
        try:
            user_response = int(input("Identify the Frequency Level (L=1, M=2, H=3): "))
            if user_response in [1, 2, 3]:
                break
            else:
                print("Invalid input. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Enter a number.")

    # Record Response Time
    response_times[i] = time.time() - start_time
    responses[i] = user_response

    # Turn off Solenoid
    send_end_signal()
    time.sleep(2)  # Allow for deflation

# Map raw haptic signal values to frequency levels
haptic_labels = []
for s in haptic_signals:  # Skip calibration signals
    sol_tuple = tuple(s["solenoids"])
    if sol_tuple in signal_to_label:
        haptic_labels.append(signal_to_label[sol_tuple])
    else:
        print(f"Warning: No mapping found for {sol_tuple}, skipping.")
        haptic_labels.append(None)

# Convert responses to direction labels
responses_labels = [label_to_signal[r] for r in responses]

# ------- CREATING FOLDER TO SAVE DATA ---------
base_dir = "task_A_data"
participant_dir = f"{base_dir}/P{user_id}"

# Create directories if they don't exist
os.makedirs(participant_dir, exist_ok=True)

# ------- CONFUSION MATRIX COMPUTATION ---------
print(f"\nDEBUG: haptic_labels = {haptic_labels}")
print(f"DEBUG: responses = {responses.tolist()}")

# Ensure valid labels exist
if any(label is None for label in haptic_labels):
    print("Error: Some trials have missing labels. Check signal-to-label mapping.")
    exit()

conf_matrix = confusion_matrix(haptic_labels, responses, labels=[1, 2, 3])
conf_matrix_norm = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis] * 100

# ------- PLOTTING CONFUSION MATRIX ---------
plt.figure(figsize=(6, 5))
sns.heatmap(conf_matrix_norm, annot=True, cmap="Blues", xticklabels=FREQ_LEVELS, yticklabels=FREQ_LEVELS, fmt=".1f")
plt.xlabel("Reported Frequency Level")
plt.ylabel("Actual Frequency Level")
plt.title("Confusion Matrix for Frequency Identification")

# Save in the same directory as the JSON file
conf_matrix_plot_filename = os.path.join(participant_dir, f"F_{user_id}_{device_type}_{display_id}_{hand}_conf_matrix.png")
plt.savefig(conf_matrix_plot_filename, bbox_inches="tight", dpi=300)
plt.show()
plt.close()

print(f"Saved confusion matrix plot: {conf_matrix_plot_filename}")


# ------- COMPUTE RESPONSE TIME METRICS ---------
correct_trials = np.array(haptic_labels) == responses
incorrect_trials = np.array(haptic_labels) != responses

# Store all response times separately
correct_response_times = response_times[correct_trials].tolist()
incorrect_response_times = response_times[incorrect_trials].tolist()

avg_response_time_correct = np.mean(correct_response_times) if correct_response_times else None
avg_response_time_incorrect = np.mean(incorrect_response_times) if incorrect_response_times else None

if avg_response_time_correct is not None:
    print(f"\nAverage Response Time for Correct Trials: {avg_response_time_correct:.2f} seconds")
else:
    print("\nNo correct trials recorded.")

if avg_response_time_incorrect is not None:
    print(f"Average Response Time for Incorrect Trials: {avg_response_time_incorrect:.2f} seconds")
else:
    print("No incorrect trials recorded.")


# ------- PLOTTING RESPONSE TIMES ---------
plt.figure(figsize=(6, 4))
plt.bar(["Correct", "Incorrect"], [avg_response_time_correct or 0, avg_response_time_incorrect or 0], color=['blue', 'red'])
plt.ylabel("Average Response Time (s)")
plt.title("Average Response Time for Correct vs Incorrect Trials")

# Save response time plot in the same directory
response_time_plot_filename = os.path.join(participant_dir, f"F_{user_id}_{device_type}_{display_id}_{hand}_response_times.png")
plt.savefig(response_time_plot_filename, bbox_inches="tight", dpi=300)
plt.show()
plt.close()

print(f"Saved response time plot: {response_time_plot_filename}")

# ------- SAVE DATA AS JSON ---------
data = {
    "user_id": user_id,
    "hand": hand,
    "device_type": device_type,
    "display_id": display_id, 
    "trial_order": [s["direction"] for s in haptic_signals],  # Save directions instead of solenoids
    "responses": responses_labels,
    "response_times": response_times.tolist(),
    "correct_response_times": correct_response_times,
    "incorrect_response_times": incorrect_response_times,
    "confusion_matrix_percentages": conf_matrix_norm.tolist(),
    "avg_response_time_correct": avg_response_time_correct,
    "avg_response_time_incorrect": avg_response_time_incorrect
}

# ------- FORMAT FILENAME WITH METADATA ---------
# Define filename with full path
file_name = f"{participant_dir}/F_{user_id}_{device_type}_{display_id}_{hand}.json"

# Save JSON
with open(file_name, "w") as f:
    json.dump(data, f, indent=4)

print(f"\nExperiment Complete. Data saved as {file_name}")

