"""
fixes a bug for a small set of users where
preferences were shown as Pressure Frequency Area
instead of Pressure Area Frequency
"""

import numpy as np
from slider import user_study_h_mapping
from information_gain import ig_optimal, construct_saliency

BETA = 5.0
N_INTERFACES = 3
XDIM = 4
YDIM = 4
N_AXIS = 2

filename = "broken_log.log"

with open(filename, "r") as fh:
    data = fh.read()


case = ""
idx = 0
new_data = []
for line in data.split("\n"):
    try:
        first_word = line[0 : line.index(" ")]
    except ValueError:
        first_word = line[0:-1]
    try:
        if first_word == "(4x4):":
            case = "4x4"
            new_data.append(line)
        elif first_word == "(7x3):":
            case = "7x3"
            new_data.append(line)
        elif first_word[0] == "=":
            new_data.append(line)
    except:
        break
    if case == "4x4":
        if first_word == "Preferences:":
            words = line.split(" ")
            # note that in the original, the preferences are passed incorrectl
            p1 = float(words[1])
            p2 = float(words[3])
            p3 = float(words[2])
            P = np.diag([p1, p2, p3])
            W = construct_saliency(P, gamma=0.25)
            igs, perms, idxs = ig_optimal(
                W,
                xdim=4,
                ydim=4,
                beta=BETA,
                n_interfaces=N_INTERFACES,
                n_axis=N_AXIS,
                h_func=user_study_h_mapping,
            )
            new_data.append(f"Preferences: {P[0, 0]} {P[1, 1]} {P[2, 2]}")
            new_data.append(f"Saliency: {W[0, 0]} {W[1, 1]} {W[2, 2]}")

            for i in range(len(igs)):
                new_data.append(
                    f"info gain: {np.round(igs[idxs[i]], 2):1.2f} config: {perms[idxs[i]]}"
                )
        else:
            continue
    elif case == "7x3":
        if first_word == "Preferences:":
            words = line.split(" ")
            # note that in the original, the preferences are passed incorrectl
            p1 = float(words[1])
            p2 = float(words[3])
            p3 = float(words[2])
            P = np.diag([p1, p2, p3])
            W = construct_saliency(P, gamma=0.25)
            igs, perms, idxs = ig_optimal(
                W,
                xdim=7,
                ydim=3,
                beta=BETA,
                n_interfaces=N_INTERFACES,
                n_axis=N_AXIS,
                h_func=user_study_h_mapping,
            )
            new_data.append(f"Preferences: {P[0, 0]} {P[1, 1]} {P[2, 2]}")
            new_data.append(f"Saliency: {W[0, 0]} {W[1, 1]} {W[2, 2]}")

            for i in range(len(igs)):
                new_data.append(
                    f"info gain: {np.round(igs[idxs[i]], 2):1.2f} config: {perms[idxs[i]]}"
                )
        else:
            continue

with open("logfile_fixed.log", "w") as fh:
    fh.writelines([d + "\n" for d in new_data])
