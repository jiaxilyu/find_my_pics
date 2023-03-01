import requests
from statistics import mean
import time

class AutoScalar:
    def __init__(self, cloudwatch, manager_port=5002):
        self.cloudwatch = cloudwatch
        self.manager_port = manager_port
        self.min_miss = None
        self.max_miss = None
        self.reset_threshold()
    
    # get min_miss, max_miss from manager endpoint
    def reset_threshold(self):
        url = "http://localhost:%s/api/getThreshold"%self.manager_port
        while True:
            # while manager endpoint is shut down
            try:
                response = requests.get(url)
                break
            except requests.exceptions.ConnectionError as e:
                print("cant find manager, please make sure manager is alive!!!")
                time.sleep(3)
        response = response.json()
        self.min_miss = response["min_miss"]
        self.max_miss = response["max_miss"]
    
    def get_miss_rate(self):
        statistics = self.cloudwatch.get_metrics_data()
        if len(statistics["Miss_Rate"]) == 0:
            return 0
        else:
            return mean(statistics["Miss_Rate"])
    
    def get_new_scalar(self):
        miss_rate = self.get_miss_rate()
        # shrink
        if miss_rate <= self.min_miss:
            return "shrink"
        elif miss_rate >= self.max_miss:
            return "expand"
        else:
            return None
# a = AutoScalar(cloudwatch=1)