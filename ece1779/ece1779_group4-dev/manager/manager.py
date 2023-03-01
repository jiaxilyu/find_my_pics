import hashlib
import requests

from manager.logging_config import logger
from collections import deque


class Node:
    def __init__(self, node_id, ip, port, is_active):
        self.node_id = node_id
        self.ip = ip
        self.port = port
        self.is_active = is_active


class Manager:
    def __init__(self):
        # the dictionary of memcache nodes in the pool
        self.key_node_cache = {'node' + str(i + 1): set() for i in range(8)}
        self.memcache_nodes = {
            "node1": Node("node1", "100.26.232.128", 5000, True),
            "node2": Node("node2", "127.0.0.1", 5012, False),
            "node3": Node("node3", "127.0.0.1", 5013, False),
            "node4": Node("node4", "127.0.0.1", 5014, False),
            "node5": Node("node5", "127.0.0.1", 5015, False),
            "node6": Node("node6", "127.0.0.1", 5016, False),
            "node7": Node("node7", "127.0.0.1", 5017, False),
            "node8": Node("node8", "127.0.0.1", 5018, False),
        }
        # cache parameters
        self.mode = 'auto'
        self.num_nodes = len(list(filter(lambda x: x.is_active, self.memcache_nodes.values())))
        self.cache_size = 0
        self.policy = 'LRU'
        self.max_miss = 0.5
        self.min_miss = 0.1
        self.exp_ratio = 2
        self.shrink_ratio = 0.5
        # a deque that holds the statistics data over the past 30 minutes - each element is a subarray with [
        # num_nodes: int, hit_rate: float, miss_rate: float, num_cached_items: int, cache_size: float, num_requests:
        # int]
        self.stat_history = deque([[0, 0.0, 0.0, 0, 0.0, 0]] * 30, maxlen=30)

    def get_cached_node(self, key) -> Node:
        for node in self.key_node_cache:
            if key in self.key_node_cache[node]:
                return self.memcache_nodes[node]
        return None

    @staticmethod
    def get_md5(key_: str):
        return hashlib.md5(key_.encode('utf-8')).hexdigest()

    def get_assigned_node(self, key_) -> Node:
        # check if key has already in any node
        node = self.get_cached_node(key_)
        if node:
            return node
        active_nodes = list(filter(lambda x: x.is_active, self.memcache_nodes.values()))
        if not active_nodes:
            return None

        md5 = self.get_md5(key_)
        index = int(md5, 16) >> 124
        return active_nodes[index % len(active_nodes)]

    def configure(self, mode, num_nodes, cache_size, policy, max_miss, min_miss, exp_ratio, shrink_ratio):
        if mode == 'manual':
            num_nodes_diff = num_nodes - self.num_nodes
            if num_nodes_diff > 0:
                for i in range(num_nodes_diff):
                    self.add_node()
            elif num_nodes_diff < 0:
                for i in range(-num_nodes_diff):
                    self.remove_node()
        self.mode = mode
        self.num_nodes = num_nodes
        self.cache_size = cache_size
        self.policy = policy
        self.max_miss = max_miss
        self.min_miss = min_miss
        self.exp_ratio = exp_ratio
        self.shrink_ratio = shrink_ratio
        logger.info(
            "Parameters updated: mode: %s, num_nodes: %s, cache_size: %s, policy: %s, max_miss: %s, min_miss: %s, exp_ratio: %s, shrink_ratio: %s" % (
                self.mode, self.num_nodes, self.cache_size, self.policy, self.max_miss, self.min_miss, self.exp_ratio,
                self.shrink_ratio))

    # Activate a node in the pool
    def add_node(self):
        for node in self.memcache_nodes.values():
            if not node.is_active:
                self.num_nodes += 1
                node.is_active = True
                logger.info("Node %s is activated" % node.node_id)
                return True
        logger.error("All nodes are active")
        return False

    # Deactivate a node in the pool
    def remove_node(self):
        # should keep at least 1 node activate
        if self.num_nodes > 1:
            for name, node in zip(self.memcache_nodes.keys(), self.memcache_nodes.values()):
                if node.is_active:
                    node.is_active = False
                    self.num_nodes -= 1
                    self.key_node_cache[name] = set()
                    # delete keys in cache?
                    request_url = "http://" + str(node.ip) + ":" + str(node.port) + "/api/clear_cache"
                    requests.post(request_url)
                    logger.info("Node %s is deactivated" % node.node_id)
                    return True
        logger.error("All nodes are inactive")
        return False

    # Update the statistics data
    def update_stat(self):
        num_nodes = len(list(filter(lambda x: x.is_active, self.memcache_nodes.values())))
        hit_rate = self.get_hit_rate()
        miss_rate = self.get_miss_rate()
        num_cached_items = self.get_num_cached_items()
        cache_size = self.get_cache_size()
        num_requests = self.get_num_requests()
        self.stat_history.append([num_nodes, hit_rate, miss_rate, num_cached_items, cache_size, num_requests])
        logger.info(
            "Statistics updated: num_nodes: %s, hit_rate: %s, miss_rate: %s, num_cached_items: %s, cache_size: %s, num_requests: %s" % (
                num_nodes, hit_rate, miss_rate, num_cached_items, cache_size, num_requests))

    # TODO: Fetch and calculate the total hit rate from Cloudwatch
    def get_hit_rate(self):
        return 0.0

    # TODO: Fetch and calculate the total miss rate from Cloudwatch
    def get_miss_rate(self):
        return 0.0

    # TODO: Fetch and calculate the total number of cached items from Cloudwatch
    def get_num_cached_items(self):
        return 0

    # TODO: Fetch and calculate the total cache size from Cloudwatch
    def get_cache_size(self):
        return 0.0

    # TODO: Fetch and calculate the total number of requests from Cloudwatch
    def get_num_requests(self):
        return 0
