from re import I
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
    """
    2: PA
    3: PF
    4: AF
    PAF
    """
    preferred_confs = [
        [2, 4, 3],
        [2, 3, 4],
        [2, 3, 4],
        [2, 3, 4],
        [3, 2, 4],
        [2, 4, 3],
        [2, 3, 4],
        [2, 3, 4],
        [2, 3, 4],
        [4, 2, 3],
        [2, 4, 3],
        [3, 2, 4],
        [3, 2, 4],
    ]

    pa_error = []
    pf_error = []
    af_error = []

    pa_class = []
    pf_class = []
    af_class = []

    pa_time = []
    pf_time = []
    af_time = []

    error_1 = []
    error_2 = []
    error_3 = []

    class_1 = []
    class_2 = []
    class_3 = []

    time_1 = []
    time_2 = []
    time_3 = []

    error_ne_2_1 = []
    error_ne_2_2 = []
    error_ne_2_3 = []

    class_ne_2_1 = []
    class_ne_2_2 = []
    class_ne_2_3 = []

    time_ne_2_1 = []
    time_ne_2_2 = []
    time_ne_2_3 = []

    filenames = glob("new_data/obj_ID_13/*/trial_?.json")
    filenames.sort()
    for f in filenames:
        with open(f, "r") as fh:
            data = json.load(fh)
        s = "new_data/obj_ID_13/s_"
        til_next__ = f[len(s) :].find("_")
        user_idx = int(f[len(s) : len(s) + til_next__]) - 1  # trust me bro
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
            if configuration == preferred_confs[user_idx][0]:
                error_1.append(e)
                class_1.append(c)
                time_1.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_1.append(e)
                    class_ne_2_1.append(c)
                    time_ne_2_1.append(data["duration_sec"])
            elif configuration == preferred_confs[user_idx][1]:
                error_2.append(e)
                class_2.append(c)
                time_2.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_2.append(e)
                    class_ne_2_2.append(c)
                    time_ne_2_2.append(data["duration_sec"])
            elif configuration == preferred_confs[user_idx][2]:
                error_3.append(e)
                class_3.append(c)
                time_3.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_3.append(e)
                    class_ne_2_3.append(c)
                    time_ne_2_3.append(data["duration_sec"])
            else:
                raise Exception

        elif configuration == 3:
            """PF"""
            e = np.sqrt(
                (bowl_idx - true_bowl_idx) ** 2 + (plate_idx - true_plate_idx) ** 2
            )
            pf_error.append(e)
            c = int(bowl_idx != true_bowl_idx) + int(plate_idx != true_plate_idx)
            pf_class.append(c)
            pf_time.append(data["duration_sec"])
            if configuration == preferred_confs[user_idx][0]:
                error_1.append(e)
                class_1.append(c)
                time_1.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_1.append(e)
                    class_ne_2_1.append(c)
                    time_ne_2_1.append(data["duration_sec"])
            elif configuration == preferred_confs[user_idx][1]:
                error_2.append(e)
                class_2.append(c)
                time_2.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_2.append(e)
                    class_ne_2_2.append(c)
                    time_ne_2_2.append(data["duration_sec"])
            elif configuration == preferred_confs[user_idx][2]:
                error_3.append(e)
                class_3.append(c)
                time_3.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_3.append(e)
                    class_ne_2_3.append(c)
                    time_ne_2_3.append(data["duration_sec"])
            else:
                raise Exception
        elif configuration == 4:
            """AF"""
            e = np.sqrt(
                (bowl_idx - true_bowl_idx) ** 2 + (plate_idx - true_plate_idx) ** 2
            )
            af_error.append(e)
            c = int(bowl_idx != true_bowl_idx) + int(plate_idx != true_plate_idx)
            af_class.append(c)
            af_time.append(data["duration_sec"])
            if configuration == preferred_confs[user_idx][0]:
                error_1.append(e)
                class_1.append(c)
                time_1.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_1.append(e)
                    class_ne_2_1.append(c)
                    time_ne_2_1.append(data["duration_sec"])
            elif configuration == preferred_confs[user_idx][1]:
                error_2.append(e)
                class_2.append(c)
                time_2.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_2.append(e)
                    class_ne_2_2.append(c)
                    time_ne_2_2.append(data["duration_sec"])
            elif configuration == preferred_confs[user_idx][2]:
                error_3.append(e)
                class_3.append(c)
                time_3.append(data["duration_sec"])
                if preferred_confs[user_idx][0] != 2:
                    """these are unique"""
                    error_ne_2_3.append(e)
                    class_ne_2_3.append(c)
                    time_ne_2_3.append(data["duration_sec"])
            else:
                raise Exception

        else:
            raise NotImplementedError("wtf?")
    print("PA MSE", np.mean(pa_error))
    print("PF MSE", np.mean(pf_error))
    print("AF MSE", np.mean(af_error))

    print("PA CLASS", np.mean(pa_class))
    print("PF CLASS", np.mean(pf_class))
    print("AF CLASS", np.mean(af_class))

    print("1 MSE", np.mean(error_1), np.std(error_1))
    print("2 MSE", np.mean(error_2), np.std(error_2))
    print("3 MSE", np.mean(error_3), np.std(error_3))

    print("1 CLASS", np.mean(class_1), np.std(class_1))
    print("2 CLASS", np.mean(class_2), np.std(class_2))
    print("3 CLASS", np.mean(class_3), np.std(class_3))

    plt.bar(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        [
            np.mean(pa_error),
            np.mean(pf_error),
            np.mean(af_error),
            np.mean(pa_class),
            np.mean(pf_class),
            np.mean(af_class),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.mean(pa_error),
            (1.0 / np.sqrt(6.0)) * np.mean(pf_error),
            (1.0 / np.sqrt(6.0)) * np.mean(af_error),
            (1.0 / np.sqrt(6.0)) * np.mean(pa_class),
            (1.0 / np.sqrt(6.0)) * np.mean(pf_class),
            (1.0 / np.sqrt(6.0)) * np.mean(af_class),
        ],
        color=["g", "g", "g", "b", "b", "b"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        [
            "pa",
            "pf",
            "af",
            "pa",
            "pf",
            "af",
        ],
        rotation=90,
    )
    plt.title("MSE and CLASS error (7x3)")
    plt.savefig("figures/mse_class_conf.svg")
    plt.close()

    plt.bar(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        [
            np.mean(error_1),
            np.mean(error_2),
            np.mean(error_3),
            np.mean(class_1),
            np.mean(class_2),
            np.mean(class_3),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.std(error_1),
            (1.0 / np.sqrt(6.0)) * np.std(error_2),
            (1.0 / np.sqrt(6.0)) * np.std(error_3),
            (1.0 / np.sqrt(6.0)) * np.std(class_1),
            (1.0 / np.sqrt(6.0)) * np.std(class_2),
            (1.0 / np.sqrt(6.0)) * np.std(class_3),
        ],
        color=["g", "g", "g", "b", "b", "b"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        ["1", "2", "3", "1", "2", "3"],
        rotation=90,
    )
    plt.title("MSE and CLASS error (7x3)")
    plt.savefig("figures/mse_class_rank.svg")
    plt.close()

    plt.bar(
        [0.5, 1.5, 2.5],
        [
            np.mean(pa_time),
            np.mean(pf_time),
            np.mean(af_time),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.mean(pa_time),
            (1.0 / np.sqrt(6.0)) * np.mean(pf_time),
            (1.0 / np.sqrt(6.0)) * np.mean(af_time),
        ],
        color=["g", "g", "g"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5],
        [
            "pa",
            "pf",
            "af",
        ],
        rotation=90,
    )
    plt.title("Time per Configuration (7x3)")
    plt.savefig("figures/time_conf.svg")
    plt.close()

    plt.bar(
        [0.5, 1.5, 2.5],
        [
            np.mean(time_1),
            np.mean(time_2),
            np.mean(time_3),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.mean(time_1),
            (1.0 / np.sqrt(6.0)) * np.mean(time_2),
            (1.0 / np.sqrt(6.0)) * np.mean(time_3),
        ],
        color=["g", "g", "g"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5],
        ["1", "2", "3"],
        rotation=90,
    )
    plt.title("Time per Configuration (7x3)")
    plt.savefig("figures/time_rank.svg")
    plt.close()

    plt.bar(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        [
            np.mean(error_ne_2_1),
            np.mean(error_ne_2_2),
            np.mean(error_ne_2_3),
            np.mean(class_ne_2_1),
            np.mean(class_ne_2_2),
            np.mean(class_ne_2_3),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.std(error_ne_2_1),
            (1.0 / np.sqrt(6.0)) * np.std(error_ne_2_2),
            (1.0 / np.sqrt(6.0)) * np.std(error_ne_2_3),
            (1.0 / np.sqrt(6.0)) * np.std(class_ne_2_1),
            (1.0 / np.sqrt(6.0)) * np.std(class_ne_2_2),
            (1.0 / np.sqrt(6.0)) * np.std(class_ne_2_3),
        ],
        color=["g", "g", "g", "b", "b", "b"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5, 4.0, 5.0, 6.0],
        ["1", "2", "3", "1", "2", "3"],
        rotation=90,
    )
    plt.title("MSE and CLASS error (7x3)")
    plt.savefig("figures/filtered_mse_class_rank.svg")
    plt.close()

    plt.bar(
        [0.5, 1.5, 2.5],
        [
            np.mean(time_ne_2_1),
            np.mean(time_ne_2_2),
            np.mean(time_ne_2_3),
        ],
        yerr=[
            (1.0 / np.sqrt(6.0)) * np.mean(time_ne_2_1),
            (1.0 / np.sqrt(6.0)) * np.mean(time_ne_2_2),
            (1.0 / np.sqrt(6.0)) * np.mean(time_ne_2_3),
        ],
        color=["g", "g", "g"],
    )
    plt.xticks(
        [0.5, 1.5, 2.5],
        ["1", "2", "3"],
        rotation=90,
    )
    plt.title("Time per Configuration (7x3)")
    plt.savefig("figures/filtered_time_rank.svg")
    plt.close()
    
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
