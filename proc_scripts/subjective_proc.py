import numpy as np

subjective_data = np.loadtxt(
    "subjective2.csv",
    delimiter=",",
    usecols=list(range(5, 65)),
    skiprows=2,
)

orders = [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
confs = [
    [2, 4, 3, 4, 3, 2],
    [3, 2, 4, 2, 3, 4],
    [3, 4, 2, 4, 2, 3],
    [2, 3, 4, 3, 2, 4],
    [3, 4, 2, 4, 2, 3],
    [3, 4, 2, 4, 2, 3],
    [4, 2, 3, 2, 4, 3],
    [4, 3, 2, 3, 4, 2],
    [2, 4, 3, 3, 4, 2],
    [2, 3, 4, 3, 2, 4],
    [4, 3, 2, 2, 4, 3],
    [4, 2, 3, 2, 3, 4],
    [2, 4, 3, 4, 3, 2],
]
"""
1: overload (ABC) ################# THIS IS UNUSED
2: pressure area (AB)
3: pressure freq (AC)
4: area freq (BC)
"""
# preferred_confs = [
#     [2, 2],
#     [2, 2],
#     [2, 2],
#     [2, 2],
#     [3, 3],
#     [2, 2],  # I DON"T HAVE THIS DATA YET, ASSUMING BEST CASE SCENARIO
# ]
preferred_confs = [
    [[2, 4, 3], [2, 4, 3]],
    [[2, 3, 4], [2, 3, 4]],
    [[2, 3, 4], [2, 3, 4]],
    [[2, 3, 4], [2, 3, 4]],
    [[3, 2, 4], [3, 2, 4]],
    [[2, 4, 3], [2, 4, 3]],
    [[2, 3, 4], [2, 3, 4]],
    [[2, 3, 4], [2, 3, 4]],
    [[2, 3, 4], [2, 3, 4]],
    [[4, 2, 3], [4, 2, 3]],
    [[2, 4, 3], [2, 4, 3]],
    [[3, 2, 4], [3, 2, 4]],
    [[3, 2, 4], [3, 2, 4]],
]


def proc(data, user_id, idx):
    x = []
    for i in range(5):
        x.append(
            0.5 * (data[user_id][idx + 2 * i] + (8 - data[user_id][idx + (2 * i + 1)]))
        )
    return x


data4x4 = [[] for _ in range(4)]  # preferences for each configuration, for each user
data7x3 = [[] for _ in range(4)]

for user_idx, conf in enumerate(confs):
    """for each configuration order of each user"""
    if orders[user_idx] == 1:  # they did 4x4 then 7x3
        for conf_idx, c in enumerate(conf[:3]):
            """this is the order that the user received the configurations in"""
            z = proc(subjective_data, user_idx, conf_idx * 10)
            data4x4[c - 1].append(z)
        for conf_idx, c in enumerate(conf[3:]):
            z = proc(subjective_data, user_idx, 30 + conf_idx * 10)
            data7x3[c - 1].append(z)
    elif orders[user_idx] == 2:
        for conf_idx, c in enumerate(conf[3:]):
            z = proc(subjective_data, user_idx, conf_idx * 10)
            data7x3[c - 1].append(z)
        for conf_idx, c in enumerate(conf[:3]):
            """this is the order that the user received the configurations in"""
            z = proc(subjective_data, user_idx, 30 + conf_idx * 10)
            data4x4[c - 1].append(z)


# we've now reformatted the data to be in the correct ordering.
# now, we average across users using OVERLOAD, PREF, UNPREF
pre_data4 = [np.zeros(5) for _ in range(3)]
pre_data7 = [np.zeros(5) for _ in range(3)]
# we also consider the values after their preferences change
post_data4 = [np.zeros(5) for _ in range(3)]
post_data7 = [np.zeros(5) for _ in range(3)]

for conf_idx in range(len(data4x4)):
    """for each configuration"""
    if conf_idx == 0:
        """overload"""
        for user_idx, user_data in enumerate(data4x4[conf_idx]):
            pre_data4[0] += np.array(data4x4[conf_idx][user_idx])
            post_data4[0] += np.array(data4x4[conf_idx][user_idx])
    else:
        for user_idx, user_data in enumerate(data4x4[conf_idx]):
            if conf_idx + 1 == preferred_confs[user_idx][0][0]:
                pre_data4[1] += np.array(data4x4[conf_idx][user_idx])
            elif conf_idx + 1 == preferred_confs[user_idx][0][1]:
                pre_data4[1] += np.array(data4x4[conf_idx][user_idx])
            else:
                pre_data4[2] += 0.5 * np.array(data4x4[conf_idx][user_idx])

for conf_idx in range(len(data7x3)):
    """for each configuration"""
    if conf_idx == 0:
        """overload"""
        for user_idx, user_data in enumerate(data7x3[conf_idx]):
            pre_data7[0] += np.array(data7x3[conf_idx][user_idx])
            post_data7[0] += np.array(data7x3[conf_idx][user_idx])
    else:
        for user_idx, user_data in enumerate(data7x3[conf_idx]):
            if conf_idx + 1 == preferred_confs[user_idx][1]:
                pre_data7[1] += np.array(data7x3[conf_idx][user_idx])
            else:
                pre_data7[2] += 0.5 * np.array(data7x3[conf_idx][user_idx])

post_data4 = [p / len(confs) for p in post_data4]
pre_data4 = [p / len(confs) for p in pre_data4]
post_data7 = [p / len(confs) for p in post_data7]
pre_data7 = [p / len(confs) for p in pre_data7]

import matplotlib.pyplot as plt

# pre_data 4
for i, d in enumerate(pre_data4):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"pret4_{i}")
    plt.savefig(f"figures/pre4_{i}.svg")
    plt.close()
for i, d in enumerate(post_data4):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"post4_{i}")
    plt.savefig(f"figures/post4_{i}.svg")
    plt.close()
for i, d in enumerate(pre_data7):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"pre7_{i}")
    plt.savefig(f"figures/pre7_{i}.svg")
    plt.close()
for i, d in enumerate(post_data7):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"post7_{i}")
    plt.savefig(f"figures/post7_{i}.svg")
    plt.close()
