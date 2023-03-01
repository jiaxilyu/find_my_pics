from flask import Flask
import threading
import time
import sys
sys.path.append("..")
import requests
from autoscalar.auto_scalar import AutoScalar
from utils.cloudwatch import CloudWatch


autoscalar_app = Flask(__name__)

# Create CloudWatch resource
global cloudwatch
cloudwatch = CloudWatch()

# initialize autoscalar
global autoscalar
autoscalar = AutoScalar(cloudwatch)

def auto_scaling():
    time_step = 5
    while True:
        # To do
        # # send request to autoscalar to minitor the CloudWatch static
        response = requests.get('http://localhost:5003/api/UpdatePoolSize')
        time.sleep(time_step)

from autoscalar import endpoint

# start a thread for auto scaling manager pool size for every 60s
t = threading.Thread(target=auto_scaling)
t.start()

