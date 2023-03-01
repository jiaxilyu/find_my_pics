import random
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv
import numpy as np
import time
import requests
import os

IP = "http://100.26.232.128:5000/"


def update_config(size, policy):
    """
    Update cache config
    :param size: max cache capacity (str)
    :param policy: enum("RANDOM", "LRU")
    :return: None
    """
    data = {
        "size": str(size),
        "policy": policy
    }
    res = requests.post(url=IP + "api/update_cache_config", data=data)
    print(res)


def put(key):
    """
    Send a request that uploads a key/image pair. In test, it only need a key.
    :param key: key of the image
    :return: None
    """

    data = {
        "key": "test_" + key,
    }
    files = {
        "file": open("perf_test.png", "rb")
    }
    start = time.perf_counter()
    requests.post(url=IP + "api/upload", data=data, files=files)
    end = time.perf_counter()
    print(f"Put a pair cost: {end - start}")


def get(key):
    """
    Send a request that queries an image by a key
    :param key: the key of the image
    :return: None
    """
    url = IP + "api/key/" + key
    start = time.perf_counter()
    requests.post(url)
    end = time.perf_counter()
    print(f"Get an image cost: {end - start}")


def write_to_csv(x, y, path):
    """
    Write test results to csv file
    :param x: x-axis data, a list of int
    :param y: y-axis data, a list of int or float
    :param path: result file path
    :return: None
    """
    with open(path, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(x)
        writer.writerow(y)


def plot(axis, x1, y1, x2, y2, x3, y3, x_label, y_label, title):
    """
    Plot performance graph
    :param axis: axis
    :param x1: x-axis data
    :param y1: y-axis data
    :param x2: x-axis data
    :param y2: y-axis data
    :param x3: x-axis data
    :param y3: y-axis data
    :param x_label: x-axis label name
    :param y_label: y-axis label name
    :param title: graph title
    :return: None
    """
    axis.set_title(title)
    axis.set_xlabel(x_label, fontsize=10)
    axis.set_ylabel(y_label, fontsize=10)

    axis.spines["left"].set_visible(False)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    axis.grid(ls="--", lw=1, color="#4E616C")

    line1, = axis.plot(x1, y1, marker='o', mfc="white", ms=2, color="black")
    line2, = axis.plot(x2, y2, marker='o', mfc="white", ms=2, color="#00A752")
    line3, = axis.plot(x3, y3, marker='o', mfc="white", ms=2, color="#87D8F7")

    axis.xaxis.set_major_locator(ticker.MultipleLocator(10))

    axis.xaxis.set_tick_params(length=2, color="#4E616C", labelcolor="#4E616C", labelsize=10)
    axis.yaxis.set_tick_params(length=2, color="#4E616C", labelcolor="#4E616C", labelsize=10)

    axis.spines["bottom"].set_edgecolor("#4E616C")
    axis.legend(handles=[line1, line2, line3], labels=['Random', 'LRU', 'No Cache'], loc='lower right')
    # ax.fill_between(x=x, y1=y, y2=y1, alpha=0.5)


# two kinds of request used in test
requests_ = [put, get]

# three different ratio
probs = [
    np.array([0.2, 0.8]),
    np.array([0.5, 0.5]),
    np.array([0.8, 0.2])
]

# result path
latency_path = 'latency.csv'
throughput_path = 'throughput.csv'

# ============================================================
#                       INITIALIZATION

if os.path.exists(latency_path):
    os.remove(latency_path)
if os.path.exists(throughput_path):
    os.remove(throughput_path)

update_config("12", "RANDOM")
requests.post(IP + "api/delete_all")
for i in range(100):
    put(str(i))

# ============================================================
#                           START

# test will select keys randomly from this variable
keys = [str(i) for i in range(100)]

x_latency = []
y_latency = []
x_throughput = []
y_throughput = []
times = 0
latency_sum = 0

time_cost = 0
time_sum = 0
request_num = 0

# test different ratios
for i in range(3):
    if i == 1:
        update_config("12", "LRU")
    elif i == 2:
        update_config("0", "RANDOM")
    for prob in probs:
        # test latency
        for t in (1, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10):
            times += t
            x_latency.append(times)
            for _ in range(t):
                key = random.choice(keys)
                start_time = time.perf_counter()
                response = np.random.choice(requests_, p=prob.ravel())(key)
                end_time = time.perf_counter()
                latency = end_time - start_time
                latency_sum += latency
            y_latency.append(latency_sum)
        # write results to file
        write_to_csv(x_latency, y_latency, latency_path)
        x_latency = []
        y_latency = []
        times = latency_sum = 0

        # test throughput
        for t in (0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10):
            time_sum += t
            while True:
                key = random.choice(keys)
                start_time = time.perf_counter()
                response = np.random.choice(requests_, p=prob.ravel())(key)
                end_time = time.perf_counter()
                latency = end_time - start_time
                time_cost += latency
                request_num += 1
                if time_cost > time_sum:
                    x_throughput.append(time_sum)
                    y_throughput.append(request_num - 1)
                    break
        write_to_csv(x_throughput, y_throughput, throughput_path)
        x_throughput = []
        y_throughput = []
        time_sum = time_cost = request_num = 0

# ============================================================
#                        READ RESULTS
print("READ RESULTS")
xs_latency = []
ys_latency = []
xs_throughput = []
ys_throughput = []

c = 1
with open(latency_path, "r", newline='') as f:
    reader = csv.reader(f)
    for line in reader:
        if c % 2 == 0:
            ys_latency.append([round(float(i), 2) for i in line])
        else:
            xs_latency.append([int(i) for i in line])
        c += 1
    c = 1
with open(throughput_path, "r", newline='') as f:
    reader = csv.reader(f)
    for line in reader:
        if c % 2 == 0:
            ys_throughput.append([int(i) for i in line])
        else:
            xs_throughput.append([int(i) for i in line])
        c += 1

# ============================================================
#                           PLOT
fig = plt.figure(figsize=(8, 3), dpi=200, facecolor="white")

ax = plt.subplot(121, facecolor="white")
ax1 = plt.subplot(122, facecolor="white")
plot(ax, xs_latency[0], ys_latency[0], xs_latency[3], ys_latency[3], xs_latency[6], ys_latency[6], "Number of Requests",
     "Latency (s)", "Latency Graph (1:4/W:R)")
plot(ax1, xs_throughput[0], ys_throughput[0], xs_throughput[3], ys_throughput[3], xs_throughput[6], ys_throughput[6],
     "Time Unit (s)", "Number of Requests Processed", "Throughput Graph (1:4/W:R)")

plt.tight_layout()
plt.savefig('2W_8R')

plt.clf()

ax = plt.subplot(121, facecolor="white")
ax1 = plt.subplot(122, facecolor="white")
plot(ax, xs_latency[1], ys_latency[1], xs_latency[4], ys_latency[4], xs_latency[7], ys_latency[7], "Number of Requests",
     "Latency (s)", "Latency Graph (1:1/W:R)")
plot(ax1, xs_throughput[1], ys_throughput[1], xs_throughput[4], ys_throughput[4], xs_throughput[7], ys_throughput[7],
     "Time Unit (s)", "Number of Requests Processed", "Throughput Graph (1:1/W:R)")

plt.tight_layout()
plt.savefig('5W_5R')

plt.clf()

# ax = plt.subplot(121, facecolor="#EFE9E6")
ax = plt.subplot(121, facecolor="white")
ax1 = plt.subplot(122, facecolor="white")
plot(ax, xs_latency[2], ys_latency[2], xs_latency[5], ys_latency[5], xs_latency[8], ys_latency[8], "Number of Requests",
     "Latency (s)", "Latency Graph (4:1/W:R)")
plot(ax1, xs_throughput[2], ys_throughput[2], xs_throughput[5], ys_throughput[5], xs_throughput[8], ys_throughput[8],
     "Time Unit (s)", "Number of Requests Processed", "Throughput Graph (4:1/W:R)")

plt.tight_layout()
plt.savefig('8W_2R')
