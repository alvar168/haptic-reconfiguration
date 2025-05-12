import numpy as np
import matplotlib.pyplot as plt


def proc(data, user_id, idx):
    x = []
    for i in range(5):
        x.append(
            0.5 * (data[user_id][idx + 2 * i] + (8 - data[user_id][idx + (2 * i + 1)]))
        )
    return x


subjective_data = np.loadtxt(
    "subjective.csv",
    delimiter=",",
    usecols=list(range(5, 65)),
    skiprows=2,
)

trial_orders = [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
conf_orders = [
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
2: pressure area (AB)
3: pressure freq (AC)
4: area freq (BC)
"""

preferences = [
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

data4x4 = [[] for _ in range(3)]  # for each configuration preference (1, 2, 3)
data7x3 = [[] for _ in range(3)]  # for each configuration preference (1, 2, 3)

for user_idx, conf in enumerate(conf_orders):
    """for each configuration order of each user"""
    if trial_orders[user_idx] == 1:  # 4x4 then 7x3
        for conf_idx, c in enumerate(conf[:3]):
            z = proc(subjective_data, user_idx, conf_idx * 10)
            data4x4[c - 2].append(z)
        for conf_idx, c in enumerate(conf[3:]):
            z = proc(subjective_data, user_idx, 30 + conf_idx * 10)
            data7x3[c - 2].append(z)
    elif trial_orders[user_idx] == 2:
        for conf_idx, c in enumerate(conf[:3]):
            z = proc(subjective_data, user_idx, 30 + conf_idx * 10)
            data7x3[c - 2].append(z)
        for conf_idx, c in enumerate(conf[3:]):
            z = proc(subjective_data, user_idx, conf_idx * 10)
            data4x4[c - 2].append(z)

"""data is now reformatted to be in correct ordering"""

data4 = [np.zeros(5) for _ in range(3)]  # 1, 2, 3
data7 = [np.zeros(5) for _ in range(3)]  # 1, 2, 3


for conf_idx in range(len(data4x4)):
    """
    conf_idx == 0: PA
    conf_idx == 1: PF
    conf_idx == 2: AF
    """
    interface = conf_idx + 2
    for user_idx, user_data in enumerate(data4x4[conf_idx]):
        if interface == preferences[user_idx][0][0]:
            data4[0] += np.array(data4x4[conf_idx][user_idx])
        elif interface == preferences[user_idx][0][1]:
            data4[1] += np.array(data4x4[conf_idx][user_idx])
        elif interface == preferences[user_idx][0][2]:
            data4[2] += np.array(data4x4[conf_idx][user_idx])
        else:
            print("lkajsdlkfjaslkdjfa")

for conf_idx in range(len(data7x3)):
    """
    conf_idx == 0: PA
    conf_idx == 1: PF
    conf_idx == 2: AF
    """
    interface = conf_idx + 2
    for user_idx, user_data in enumerate(data7x3[conf_idx]):
        if interface == preferences[user_idx][1][0]:
            data7[0] += np.array(data7x3[conf_idx][user_idx])
        elif interface == preferences[user_idx][1][1]:
            data7[1] += np.array(data7x3[conf_idx][user_idx])
        elif interface == preferences[user_idx][1][2]:
            data7[2] += np.array(data7x3[conf_idx][user_idx])
        else:
            print("lkajsdlkfjaslkdjfa")

data4 = [p / len(conf_orders) for p in data4]
data7 = [p / len(conf_orders) for p in data7]

for i, d in enumerate(data4):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"pre4_{i}")
    plt.savefig(f"figures/pre4_{i}.svg")
    plt.close()

for i, d in enumerate(data7):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"pre7_{i}")
    plt.savefig(f"figures/pre7_{i}.svg")
    plt.close()


"""we also consider the case where preferred interface != 2"""

data4 = [p / len(conf_orders) for p in data4]
data7 = [p / len(conf_orders) for p in data7]

count4 = 0

for conf_idx in range(len(data4x4)):
    """
    conf_idx == 0: PA
    conf_idx == 1: PF
    conf_idx == 2: AF
    """
    interface = conf_idx + 2
    for user_idx, user_data in enumerate(data4x4[conf_idx]):
        if preferences[user_idx][0][0] == 2:
            continue
        count4 += 1
        if interface == preferences[user_idx][0][0]:
            data4[0] += np.array(data4x4[conf_idx][user_idx])
        elif interface == preferences[user_idx][0][1]:
            data4[1] += np.array(data4x4[conf_idx][user_idx])
        elif interface == preferences[user_idx][0][2]:
            data4[2] += np.array(data4x4[conf_idx][user_idx])
        else:
            print("lkajsdlkfjaslkdjfa")

count7 = 0

for conf_idx in range(len(data7x3)):
    """
    conf_idx == 0: PA
    conf_idx == 1: PF
    conf_idx == 2: AF
    """
    interface = conf_idx + 2
    for user_idx, user_data in enumerate(data7x3[conf_idx]):
        if preferences[user_idx][1][0] == 2:
            continue
        count7 += 1
        if interface == preferences[user_idx][1][0]:
            data7[0] += np.array(data7x3[conf_idx][user_idx])
        elif interface == preferences[user_idx][1][1]:
            data7[1] += np.array(data7x3[conf_idx][user_idx])
        elif interface == preferences[user_idx][1][2]:
            data7[2] += np.array(data7x3[conf_idx][user_idx])
        else:
            print("lkajsdlkfjaslkdjfa")

data4 = [p / (count4 / 3) for p in data4]
data7 = [p / (count7 / 3) for p in data7]
print(count4, count7)
for i, d in enumerate(data4):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"pre4_{i}")
    plt.savefig(f"figures/filtered_pre4_{i}.svg")
    plt.close()

for i, d in enumerate(data7):
    plt.bar(0.5 + np.arange(5), d)
    plt.ylim([1, 7])
    plt.xticks([])
    plt.title(f"pre7_{i}")
    plt.savefig(f"figures/filtered_pre7_{i}.svg")
    plt.close()


"""easier plot to manipulate"""

d4 = [[] for _ in range(5)]
for i, d in enumerate(data4):
    for j in range(5):
        d4[j].append(d4[j])

d7 = [[] for _ in range(5)]
for i, d in enumerate(data7):
    for j in range(5):
        d7[j].append(d7[j])

plt.bar(
    [0.5, 1.5, 2.5, 4.5, 5.5, 6.5, 8.5, 9.5, 10.5, 12.5, 13.5, 14.5, 16.5, 17.5, 18.5],
    d4,
)
plt.savefig("figures/d4.svg")
plt.close()

plt.bar(
    [0.5, 1.5, 2.5, 4.5, 5.5, 6.5, 8.5, 9.5, 10.5, 12.5, 13.5, 14.5, 16.5, 17.5, 18.5],
    d7,
)

plt.savefig("figures/d7.svg")
plt.close()
