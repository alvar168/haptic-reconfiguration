import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json
from argparse import ArgumentParser
from glob import glob

"""
The plates:
Circle 1: x = 0.399 m, y = 0.080 m
Circle 2: x = 0.579 m, y = 0.080 m
Circle 3: x = 0.759 m, y = 0.080 m
The ingredient bowls:
----Circle 0: x=0.449, y=-0.195
Circle 1: x = 0.579 m, y = -0.195 m
Circle 2: x = 0.709 m, y = -0.195 m
Circle 3: x = 0.389 m, y = -0.320 m
Circle 4: x = 0.519 m, y = -0.320 m
Circle 5: x = 0.649 m, y = -0.320 m
Circle 6: x = 0.779 m, y = -0.320 m
"""


def objid_helper(d):
    """
    given a dict with keys trial number, conf, time, joint_states, xyz_euler,
    finds the start, middle, and end positions of the trajectory.
    these correspond to plates and bowls, which are also returned
    """
    PLATES = np.array(
        [
            [0.399, 0.080],
            [0.579, 0.080],
            [0.759, 0.080],
        ]
    )
    BOWLS = np.array(
        [
            [0.449, -0.195],
            [0.579, -0.195],
            [0.709, -0.195],
            [0.389, -0.320],
            [0.519, -0.320],
            [0.649, -0.320],
            [0.779, -0.320],
        ]
    )
    points = np.array(d["xyz_euler"])

    window = 100
    vels = []
    for i in range(0, len(points) - window, window):
        curr = points[i + window][1]
        past = points[i][1]
        vels.append(curr - past)
    vels = np.array(vels)
    idx = np.argmin(vels)
    candidate = np.argmax(vels[idx:] > 0.0)
    bowl_candidate = points[window * (idx + candidate)][0:2]
    bowl_idx = np.argmin(np.linalg.norm(bowl_candidate - BOWLS, axis=1))
    plate_idx = np.argmin(np.linalg.norm(points[-1][0:2] - PLATES, axis=1))
    return bowl_idx, plate_idx


def objid():
    preferred_confs = [
        2,
        2,
        2,
        2,
        3,
        2,
    ]
    # ripped from subjective

    pa_error = []
    pf_error = []
    af_error = []
    ov_error = []

    pa_class = []
    pf_class = []
    af_class = []
    ov_class = []

    pa_time = []
    pf_time = []
    af_time = []
    ov_time = []

    pref_error = []
    unpref_error = []

    pref_class = []
    unpref_class = []

    pref_time = []
    unpref_time = []

    filenames = glob("first_six_objid/*/trial_?.json")
    filenames.sort()
    for f in filenames:
        with open(f, "r") as fh:
            data = json.load(fh)
        s = "first_six_objid/s"
        user_idx = int(f[len(s)]) - 1  # trust me bro
        bowl_idx, plate_idx = objid_helper(data)
        true_bowl_idx, true_plate_idx = [
            i - 1 for i in data["haptic_signal"]["signal"][1:]
        ]
        configuration = data["haptic_signal"]["signal"][0]
        if configuration == 2:
            """PA"""
            e = np.sqrt(
                (bowl_idx - true_bowl_idx) ** 2 + (plate_idx - true_plate_idx) ** 2
            )
            pa_error.append(e)
            c = int(bowl_idx != true_bowl_idx) + int(plate_idx != true_plate_idx)
            pa_class.append(c)
            pa_time.append(data["duration_sec"])
            if configuration == preferred_confs[user_idx]:
                pref_error.append(e)
                pref_class.append(c)
                pref_time.append(data["duration_sec"])
            else:
                unpref_error.append(e)
                unpref_class.append(c)
                unpref_time.append(data["duration_sec"])

        elif configuration == 3:
            """PF"""
            e = np.sqrt(
                (bowl_idx - true_bowl_idx) ** 2 + (plate_idx - true_plate_idx) ** 2
            )
            pf_error.append(e)
            c = int(bowl_idx != true_bowl_idx) + int(plate_idx != true_plate_idx)
            pf_class.append(c)
            pf_time.append(data["duration_sec"])
            if configuration == preferred_confs[user_idx]:
                pref_error.append(e)
                pref_class.append(c)
                pref_time.append(data["duration_sec"])
            else:
                unpref_error.append(e)
                unpref_class.append(c)
                unpref_time.append(data["duration_sec"])
        elif configuration == 4:
            """AF"""
            e = np.sqrt(
                (bowl_idx - true_bowl_idx) ** 2 + (plate_idx - true_plate_idx) ** 2
            )
            af_error.append(e)
            c = int(bowl_idx != true_bowl_idx) + int(plate_idx != true_plate_idx)
            af_class.append(c)
            af_time.append(data["duration_sec"])
            if configuration == preferred_confs[user_idx]:
                pref_error.append(e)
                pref_class.append(c)
                pref_time.append(data["duration_sec"])
            else:
                unpref_error.append(e)
                unpref_class.append(c)
                unpref_time.append(data["duration_sec"])
        elif configuration == 5:
            """OVERLOAD"""
            ov_error.append(
                np.sqrt(
                    (bowl_idx - true_bowl_idx) ** 2 + (plate_idx - true_plate_idx) ** 2
                )
            )
            c = int(bowl_idx != true_bowl_idx) + int(plate_idx != true_plate_idx)
            ov_class.append(c)
            ov_time.append(data["duration_sec"])
        else:
            raise NotImplementedError("wtf?")
    print("PA MSE", np.mean(pa_error))
    print("PF MSE", np.mean(pf_error))
    print("AF MSE", np.mean(af_error))
    print("OV MSE", np.mean(ov_error))

    print("PA CLASS", np.mean(pa_class))
    print("PF CLASS", np.mean(pf_class))
    print("AF CLASS", np.mean(af_class))
    print("OV CLASS", np.mean(ov_class))

    print("PREF MSE", np.mean(pref_error), np.std(pref_error))
    print("UNPREF MSE", np.mean(unpref_error), np.std(unpref_error))
    print("PREF CLASS", np.mean(pref_class), np.std(pref_class))
    print("UNPREF CLASS", np.mean(unpref_class), np.std(unpref_class))

    plt.bar(
        [0.5, 1.5, 2.5, 3.5, 5.0, 6.0, 7.0, 8.0],
        [
            np.mean(ov_error),
            np.mean(pa_error),
            np.mean(pf_error),
            np.mean(af_error),
            np.mean(ov_class),
            np.mean(pa_class),
            np.mean(pf_class),
            np.mean(af_class),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.mean(ov_error),
            (1.0 / np.sqrt(6.0)) * np.mean(pa_error),
            (1.0 / np.sqrt(6.0)) * np.mean(pf_error),
            (1.0 / np.sqrt(6.0)) * np.mean(af_error),
            (1.0 / np.sqrt(6.0)) * np.mean(ov_class),
            (1.0 / np.sqrt(6.0)) * np.mean(pa_class),
            (1.0 / np.sqrt(6.0)) * np.mean(pf_class),
            (1.0 / np.sqrt(6.0)) * np.mean(af_class),
        ],
        color=["g", "g", "g", "g", "b", "b", "b", "b"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5, 3.5, 5.0, 6.0, 7.0, 8.0],
        [
            "overload",
            "pa",
            "pf",
            "af",
            "overload",
            "pa",
            "pf",
            "af",
        ],
        rotation=90,
    )
    plt.title("MSE and CLASS error (7x3)")
    plt.show()

    plt.bar(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        [
            np.mean(ov_error),
            np.mean(pref_error),
            np.mean(unpref_error),
            np.mean(ov_class),
            np.mean(pref_class),
            np.mean(unpref_class),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.std(ov_error),
            (1.0 / np.sqrt(6.0)) * np.std(pref_error),
            (1.0 / np.sqrt(6.0)) * np.std(unpref_error),
            (1.0 / np.sqrt(6.0)) * np.std(ov_class),
            (1.0 / np.sqrt(6.0)) * np.std(pref_class),
            (1.0 / np.sqrt(6.0)) * np.std(unpref_class),
        ],
        color=["g", "g", "g", "b", "b", "b"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        ["overload", "pref", "unpref", "overload", "pref", "unpref"],
        rotation=90,
    )
    plt.title("MSE and CLASS error (7x3)")
    plt.show()

    plt.bar(
        [0.5, 1.5, 2.5, 3.5],
        [
            np.mean(ov_time),
            np.mean(pa_time),
            np.mean(pf_time),
            np.mean(af_time),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.mean(ov_time),
            (1.0 / np.sqrt(6.0)) * np.mean(pa_time),
            (1.0 / np.sqrt(6.0)) * np.mean(pf_time),
            (1.0 / np.sqrt(6.0)) * np.mean(af_time),
        ],
        color=["g", "g", "g", "g"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5, 3.5],
        [
            "overload",
            "pa",
            "pf",
            "af",
        ],
        rotation=90,
    )
    plt.title("Time per Configuration (7x3)")
    plt.show()

    plt.bar(
        [0.5, 1.5, 2.5],
        [
            np.mean(ov_time),
            np.mean(pref_time),
            np.mean(unpref_time),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.mean(ov_time),
            (1.0 / np.sqrt(6.0)) * np.mean(pref_time),
            (1.0 / np.sqrt(6.0)) * np.mean(unpref_time),
        ],
        color=["g", "g", "g"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5],
        [
            "overload",
            "pref",
            "unpref",
        ],
        rotation=90,
    )
    plt.title("Time per Configuration (7x3)")
    plt.show()

    return


def main():
    filenames = glob("first_six_objid/*/trial_?.json")
    filenames.sort()
    for f in filenames:
        with open(f, "r") as fh:
            data = json.load(fh)
        PLATES = np.array(
            [
                [0.399, 0.080],
                [0.579, 0.080],
                [0.759, 0.080],
            ]
        )
        BOWLS = np.array(
            [
                [0.449, -0.195],
                [0.579, -0.195],
                [0.709, -0.195],
                [0.389, -0.320],
                [0.519, -0.320],
                [0.649, -0.320],
                [0.779, -0.320],
            ]
        )
        points = np.array(data["xyz_euler"])

        window = 5
        vels = []
        for i in range(0, len(points) - window, window):
            curr = points[i + window][1]
            past = points[i][1]
            vels.append(curr - past)
        vels = np.array(vels)

        plt.plot(np.arange(len(vels)), vels, "g.")
        plt.show()


if __name__ == "__main__":
    # main()
    objid()
