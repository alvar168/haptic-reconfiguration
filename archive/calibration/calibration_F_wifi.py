import time
import requests
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# ------- CONFIGURATION ---------
# ARDUINO_IP = "192.168.0.113"  #  Arduino's IP
ARDUINO_IP = "127.0.0.1:8080"
SOLENOID_COMMANDS = {1: "S1", 2: "S2", 3: "S3"}  # HTTP routes for solenoid activation
SOLENOID_OFF = "OFF"
FREQ_LEVELS = ["L", "M", "H"]
NUM_LEVELS = len(FREQ_LEVELS)
NUM_REPEATS = 5
TOTAL_TRIALS = NUM_LEVELS * NUM_REPEATS

# ------- ASK FOR USER METADATA ---------
user_id = input("Enter participant ID: ")
hand = input("Enter hand used (L/R): ").upper()  # Standardize to uppercase
device_type = input("Enter display type (Ring, Bracelet, etc.): ")
display_id = input("Enter display ID (Index, Thumb, Wrist, etc.): ")  # Specific location

# ------- FORMAT FILENAME WITH METADATA ---------
file_name = f"experiment_{user_id}_{device_type}_{hand}_F.json"

# ------- RANDOMIZE TRIAL ORDER ---------
trial_order = np.tile(np.arange(1, NUM_LEVELS + 1), NUM_REPEATS)
np.random.shuffle(trial_order)

# ------- DATA STORAGE ---------
responses = np.zeros(TOTAL_TRIALS, dtype=int)
response_times = np.zeros(TOTAL_TRIALS)

# ------- CALIBRATION PHASE ---------
print("\nCalibration Phase: Familiarizing with Frequency Levels")
for level in range(1, NUM_LEVELS + 1):
    print(f"Applying Frequency Level: {FREQ_LEVELS[level - 1]}")
    requests.get(f"http://{ARDUINO_IP}/{SOLENOID_COMMANDS[level]}")
    time.sleep(5)  # Show for 5 seconds
    requests.get(f"http://{ARDUINO_IP}/{SOLENOID_OFF}")  # Turn off
    time.sleep(1)

input("\nTesting Phase: Press Enter to Start\n")

# ------- EXPERIMENT LOOP ---------
for i in range(TOTAL_TRIALS):
    level_idx = trial_order[i]
    # print(f"\nTrial {i + 1}/{TOTAL_TRIALS}: Applying Frequency Level...")
    print(f"Trial {i + 1}/{TOTAL_TRIALS}: Applied {FREQ_LEVELS[level_idx - 1]}")


    # Activate Solenoid
    requests.get(f"http://{ARDUINO_IP}/{SOLENOID_COMMANDS[level_idx]}")
    
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
    requests.get(f"http://{ARDUINO_IP}/{SOLENOID_OFF}")
    time.sleep(2)  # Allow for deflation

# ------- CONFUSION MATRIX COMPUTATION ---------
conf_matrix = confusion_matrix(trial_order, responses, labels=[1, 2, 3])
conf_matrix_norm = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis] * 100

# ------- PLOTTING CONFUSION MATRIX ---------
plt.figure(figsize=(6, 5))
sns.heatmap(conf_matrix_norm, annot=True, cmap="Blues", xticklabels=FREQ_LEVELS, yticklabels=FREQ_LEVELS, fmt=".1f")
plt.xlabel("Reported Frequency Level")
plt.ylabel("Actual Frequency Level")
plt.title("Confusion Matrix for Frequency Identification")
plt.show()

# ------- COMPUTE RESPONSE TIME METRICS ---------
correct_trials = trial_order == responses
incorrect_trials = trial_order != responses

# Store all response times separately
correct_response_times = response_times[correct_trials].tolist()
incorrect_response_times = response_times[incorrect_trials].tolist()

avg_response_time_correct = np.mean(correct_response_times) if correct_response_times else None
avg_response_time_incorrect = np.mean(incorrect_response_times) if incorrect_response_times else None

print(f"\nAverage Response Time for Correct Trials: {avg_response_time_correct:.2f} seconds")
print(f"Average Response Time for Incorrect Trials: {avg_response_time_incorrect:.2f} seconds")

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
    "trial_order": trial_order.tolist(),
    "responses": responses.tolist(),
    "response_times": response_times.tolist(),
    "correct_response_times": response_times[trial_order == responses].tolist(),
    "incorrect_response_times": response_times[trial_order != responses].tolist(),
    "confusion_matrix_percentages": conf_matrix_norm.tolist(),
    "avg_response_time_correct": avg_response_time_correct,
    "avg_response_time_incorrect": avg_response_time_incorrect
}

# ------- FORMAT FILENAME WITH METADATA ---------
file_name = f"experiment_{user_id}_{device_type}_{display_id}_{hand}_F.json"  # or _P.json for Pressure
with open(file_name, "w") as f:
    json.dump(data, f, indent=4)

print(f"\nExperiment Complete. Data saved as {file_name}")

