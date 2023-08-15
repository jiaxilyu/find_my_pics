import random
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv
import numpy as np
import time
import requests
import os
import aiohttp
import asyncio
from aiohttp import FormData
import json

def report_post_view():
    response = requests.post(url='https://qp0jvpfqhb.execute-api.us-east-1.amazonaws.com/default/report-post-view-event', json = {'post_id': 'd0fb4122-97d1-4365-aaf9-f930ad7fcee4'})
    return response.json()

def explore_image():
    response = requests.get('https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/explore')
    return response.status_code

def explore_user():
    response = requests.get('https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/explore/user/haoxuan11')
    return response.status_code

def search():
    response = requests.get('https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/search?content=dog')
    return response.status_code
    
def explore_label():
    response = requests.get('https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/explore/label/Person')

def log_in():
    data = {
        "username" : "haoxuan11",
        "password" : "yesyes"
    }
    
    response = requests.post('https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/api/signin', data=data)
    return response.json()['access_token']

def like(accessToken):
    data = {
        "post_id" : "d0fb4122-97d1-4365-aaf9-f930ad7fcee4"
    }
    
    # add token to header
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + accessToken
    }
    data = {
        "post_id" : "d0fb4122-97d1-4365-aaf9-f930ad7fcee4"
    }

    response = requests.post('https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/api/like', headers=headers, data=json.dumps(data))

def upload(accessToken):
    files = {
        "image": ("perf_test.png", open("perf_test.png", "rb"), "image/png")
    }
    
    data = {
        "description": "performance test",
    }
    headers = {
        "Authorization": "Bearer " + accessToken,
    }
    response = requests.post('https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/api/upload', headers=headers, data=data, files=files)
    print(response.content)
access_token = log_in()
print(access_token)





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


def plot(axis, x1, y1, x_label, y_label, title, locator, axv=None):
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
    # plot x = 1 red line
    if axv is not None:
        axis.axvline(x=axv, ls="--", lw=1, color="red")
    axis.xaxis.set_major_locator(ticker.MultipleLocator(locator))

    axis.xaxis.set_tick_params(length=2, color="#4E616C", labelcolor="#4E616C", labelsize=5)
    axis.yaxis.set_tick_params(length=2, color="#4E616C", labelcolor="#4E616C", labelsize=10)

    axis.spines["bottom"].set_edgecolor("#4E616C")
    # axis.legend(handles=[line1], labels=['Random', ], loc='lower right')
    # ax.fill_between(x=x, y1=y, y2=y1, alpha=0.5)



# three different ratio
prob = np.array([0.18, 0.18, 0.18, 0.18, 0.18, 0.09, 0.01])

# result path
latency_path = 'latency.csv'
throughput_path = 'throughput.csv'

# ============================================================
#                       INITIALIZATION


if os.path.exists(latency_path):
    os.remove(latency_path)
if os.path.exists(throughput_path):
    os.remove(throughput_path)




# ============================================================
#                           START
access_token = log_in()


x_latency = []
y_latency = []
x_throughput = []
y_throughput = []
times = 0
latency_sum = 0

time_cost = 0
time_sum = 0
request_num = 0


async def fetch_app():
    async with aiohttp.ClientSession() as session:
        operation = np.random.choice(['explore_image', 'explore_user', 'search', 'explore_label', 'like', 'log_in', 'upload'], p=prob.ravel())
   
        if operation == 'explore_image':
            url = 'https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/explore'
            async with session.get(url=url) as response:
                await response.text()
        elif operation == 'explore_user':
            url = 'https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/explore/user/haoxuan11'
            async with session.get(url=url) as response:
                await response.text()
        elif operation == 'search':
            url = 'https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/search?content=performance'
            async with session.get(url=url) as response:
                await response.text()
        elif operation == 'explore_label':
            url = 'https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/explore/label/Person'
            async with session.get(url=url) as response:
                await response.text()
        elif operation == 'like':
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
            data = {
                "post_id" : "d0fb4122-97d1-4365-aaf9-f930ad7fcee4"
            }
            url = 'https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/api/like'
            async with session.post(url=url, headers=headers, json=data) as response:
                await response.text()
        elif operation == 'log_in':
            data = {
                'username': 'haoxuan11',
                'password': 'yesyes'
            }
            url = "https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/api/signin"
            async with session.post(url=url, json=data) as response:
                await response.text()
        elif operation == 'upload':
            formdata = FormData()
            formdata.add_field('description', 'performance test')
            formdata.add_field('image', open('perf_test.png', 'rb'))
            headers = {
                "Authorization": "Bearer " + access_token,
            }
            url = 'https://sqtwxjvg6i.execute-api.us-east-1.amazonaws.com/dev/api/upload'
            async with session.post(url=url, headers=headers, data=formdata) as response:
                await response.text()
        
        
            

async def fetch_report():
    async with aiohttp.ClientSession() as session:
        async with session.post(url='https://qp0jvpfqhb.execute-api.us-east-1.amazonaws.com/default/report-post-view-event', json = {'post_id': 'd0fb4122-97d1-4365-aaf9-f930ad7fcee4'}) as response:
            await response.text()



async def test_latency(times_, func):
    task = [asyncio.create_task(func()) for _ in range(times_)]
    await asyncio.gather(*task)


async def test_throughput(times_, timeout, func):
    task = [asyncio.create_task(func()) for _ in range(times_)]
    done, pending = await asyncio.wait(task, timeout=timeout)
    print(f"Done: {len(done)}, Pending: {len(pending)}")
    return len(done)


# test latency for app
for t in (100, 200, 200, 300, 400, 500, 600, 700, 800, 900, 1000):
    x_latency.append(t)
    start = time.perf_counter()
    asyncio.run(test_latency(t, fetch_app))
    end = time.perf_counter()
    y_latency.append(end - start)
    print(f"Processing {t} requests cost: {end - start}s")
    time.sleep(3)

# write results to file
write_to_csv(x_latency, y_latency, latency_path)
x_latency = []
y_latency = []
times = latency_sum = 0


# test throughput for app
for t in (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50):
    left_time = t
    x_throughput.append(t)
    ret = 0
    while left_time > 0:
        start = time.perf_counter()
        ret += asyncio.run(test_throughput(2000, left_time, fetch_app))
        end = time.perf_counter()
        left_time -= (end - start)
        if left_time > 0:
            print(f'left: {left_time}')
        time.sleep(3)
    print(f"Processing {ret} requests cost: {t} seconds")
    y_throughput.append(ret)

write_to_csv(x_throughput, y_throughput, throughput_path)
x_throughput = []
y_throughput = []
time_sum = time_cost = request_num = 0


# test latency for stats
for t in (100, 200, 200, 300, 400, 500, 600, 700, 800, 900, 1000):
    x_latency.append(t)
    start = time.perf_counter()
    asyncio.run(test_latency(t, fetch_report))
    end = time.perf_counter()
    y_latency.append(end - start)
    print(f"Processing {t} requests cost: {end - start}s")
    time.sleep(3)

# write results to file
write_to_csv(x_latency, y_latency, latency_path)
x_latency = []
y_latency = []
times = latency_sum = 0


# test throughput for stats
for t in (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50):
    left_time = t
    x_throughput.append(t)
    ret = 0
    while left_time > 0:
        start = time.perf_counter()
        ret += asyncio.run(test_throughput(2000, left_time, fetch_report))
        end = time.perf_counter()
        left_time -= (end - start)
        if left_time > 0:
            print(f'left: {left_time}')
        time.sleep(3)
    print(f"Processing {ret} requests cost: {t} seconds")
    y_throughput.append(ret)
write_to_csv(x_throughput, y_throughput, throughput_path)
x_throughput = []
y_throughput = []
time_sum = time_cost = request_num = 0




# ==========================================================
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
plot(ax, xs_latency[0], ys_latency[0], "Number of Requests", "Latency (s)", "Latency Graph (zappa app)", 50)

plot(ax1, xs_throughput[0], ys_throughput[0], "Time Unit (s)", "Number of Requests Processed",
     "Throughput Graph (zappa app)", 2)

plt.tight_layout()
plt.savefig('app')

plt.clf()


ax = plt.subplot(121, facecolor="white")
ax1 = plt.subplot(122, facecolor="white")
plot(ax, xs_latency[1], ys_latency[1], "Number of Requests", "Latency (s)", "Latency Graph (stats lambda)", 50,
    )
plot(ax1, xs_throughput[1], ys_throughput[1], "Time Unit (s)", "Number of Requests Processed",
     "Throughput Graph (stats lambda)", 2, )

plt.tight_layout()
plt.savefig('stats')
