import time
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import serial
import random
import pickle

# Initialize serial communication with Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
print('[*] Connecting to Arduino')
time.sleep(2)  # Wait for Arduino to initialize
print('[*] Arduino connected')

def loadHapticSignals() -> list:
    """Load haptic signal parameters for each trial and shuffle order."""
    with open('calibration_signals.pkl', 'rb') as f:
        signals = pickle.load(f)
    random.shuffle(signals)  # Shuffle the trials for random order
    print(signals)
    return signals

# def send_haptic_signal(haptic_signal):
#     """Send haptic signal to Arduino via serial."""
#     if isinstance(haptic_signal, list) and len(haptic_signal) == 1:
#         signal_str = str(haptic_signal[0])  # Convert single-element lists directly
#     else:
#         signal_str = ",".join(map(str, haptic_signal))  # Keep list conversion for multiple signals
    
#     arduino.write((signal_str + "\n").encode())  # Send to Arduino
#     print(f"[*] Sending haptic signal: {signal_str}")
    
def send_haptic_signal(haptic_signal):
    """Send haptic signal to Arduino via serial."""
    signal_str = ",".join(map(str, haptic_signal))  # Convert list to comma-separated string
    arduino.write((signal_str + "\n").encode())  # Send to Arduino
    print(f"[*] Sending haptic signal: {signal_str}")

def send_end_signal():
    """Send '0' to Arduino to deflate all solenoids."""
    arduino.write(b"0\n")
    print("[*] Sending deflate signal: 0")

# ------- ASK FOR USER METADATA ---------
user_id = input("Enter participant ID: ")
hand = input("Enter hand used (L/R): ").upper()  # Standardize to uppercase
device_type = input("Enter display type (Ring, Bracelet, etc.): ")
display_id = input("Enter display ID (Index, Thumb, Wrist, etc.): ")  # Specific location

# ------- FORMAT FILENAME WITH METADATA ---------
file_name = f"experiment_{user_id}_{device_type}_{hand}_P.json"

# ------- GET HAPTIC SIGNAL LIST ---------
haptic_signals = loadHapticSignals()
TOTAL_TRIALS = len(haptic_signals)
P_LEVELS = ["L", "M", "H"]

# ------- DATA STORAGE ---------
responses = np.zeros(TOTAL_TRIALS, dtype=int)
response_times = np.zeros(TOTAL_TRIALS)


# ------- SOLENOID MAPPING (D4 PRESSURE LEVELS) ---------
signal_to_label = {
    (6, 10): 1,  # D4_L → L = 1
    (7, 10): 2,  # D4_M → M = 2
    (8, 10): 3   # D4_H → H = 3
}

# ------- CALIBRATION PHASE ---------
print("\nCalibration Phase: Familiarizing with Pressure Levels")

for level, solenoid_signal in signal_to_label.items():
    print(f"Applying Pressure Level: {P_LEVELS[solenoid_signal - 1]}")
    send_haptic_signal(list(level))  # Convert tuple to list for Arduino
    input('Press ENTER to continue')
    send_haptic_signal(["0"])
    time.sleep(5)

input("\nTesting Phase: Press Enter to Start\n")

# ------- EXPERIMENT LOOP ---------
for i in range(TOTAL_TRIALS):
        # print(f"\nTrial {i + 1}/{TOTAL_TRIALS}: Applying Pressure Level...")
    print(f"Trial {i + 1}/{TOTAL_TRIALS}: Applied {P_LEVELS[i % len(P_LEVELS)]}")

    # Activate Solenoid
    send_haptic_signal(haptic_signals[i])
    
    # Start Response Timer
    start_time = time.time()

    # Collect User Response
    while True:
        try:
            user_response = int(input("Identify the Pressure Level (L=1, M=2, H=3): "))
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
    send_haptic_signal("0")
    time.sleep(2)  # Allow for deflation

# Map raw haptic signal values to pressure levels
haptic_labels = [signal_to_label[tuple(s)] for s in haptic_signals]  # Convert list of lists to tuple for mapping

# ------- CONFUSION MATRIX COMPUTATION ---------
conf_matrix = confusion_matrix(haptic_labels, responses, labels=[1, 2, 3])
conf_matrix_norm = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis] * 100

# ------- PLOTTING CONFUSION MATRIX ---------
plt.figure(figsize=(6, 5))
sns.heatmap(conf_matrix_norm, annot=True, cmap="Blues", xticklabels=P_LEVELS, yticklabels=P_LEVELS, fmt=".1f")
plt.xlabel("Reported Pressure Level")
plt.ylabel("Actual Pressure Level")
plt.title("Confusion Matrix for Pressure Identification")
plt.show()

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
plt.show()

# ------- SAVE DATA AS JSON ---------
data = {
    "user_id": user_id,
    "hand": hand,
    "device_type": device_type,
    "display_id": display_id,  # New field to track location
    "trial_order": [signal_to_label[tuple(s)] for s in haptic_signals],
    "response_times": response_times.tolist(),
    "correct_response_times": response_times[haptic_labels == responses].tolist(),
    "incorrect_response_times": response_times[haptic_labels != responses].tolist(),
    "confusion_matrix_percentages": conf_matrix_norm.tolist(),
    "avg_response_time_correct": avg_response_time_correct,
    "avg_response_time_incorrect": avg_response_time_incorrect
}

# ------- FORMAT FILENAME WITH METADATA ---------
file_name = f"experiment_{user_id}_{device_type}_{display_id}_{hand}_P.json" 
with open(file_name, "w") as f:
    json.dump(data, f, indent=4)

print(f"\nExperiment Complete. Data saved as {file_name}")

