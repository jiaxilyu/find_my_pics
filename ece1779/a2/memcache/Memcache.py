import random
import sys
from collections import deque


class ListNode:
    def __init__(self, val, key, pre=None):
        self.val = val
        self.key = key
        self.next = None
        self.pre = pre

    def __str__(self):
        return "%s:%s" % (self.key, self.val)


class MemCache:
    def __init__(self, capacity, policy):
        self.size = 0
        self.capacity = capacity
        self.policy = policy
        self.data = {}
        self.head = None
        self.tail = None
        self.n_query = 0
        self.missing = 0
        self.request = 0
        # a deque that holds the statistics data over the past 10 minutes
        # - each element is a subarray with [hit_rate: float, miss_rate: float, item_num: int, item_size: float, requests_num]
        self.stat_history = deque([[1.0, 0.0, 0, 0.0, 0]] * 120, maxlen=120)

    def reset_policy(self, policy):
        self.policy = policy

    def reset_capacity(self, capacity):
        self.capacity = capacity
        # delete key-value from the cache until the size of cache <= new capacity
        while self.size > self.capacity:
            # abandon key according to policy
            if self.policy == "RND":
                self.RND_policy()
            elif self.policy == "LRU":
                self.LRU_policy()

    #  to read mem-cache related details from the database and reconfigure it based on the values set by the user
    def refreshConfiguration(self, db):
        # query memcache config data from db
        id, capacity, policy = db.query_memcacheconfig()[0]
        self.reset_policy(policy)
        self.reset_capacity(capacity * 1024 * 1024)

    def get_sizeof(self, obj):
        return sys.getsizeof(obj)

    # discard element from double link list
    def discard(self, key):
        if key in self.data:
            node = self.data[key]
            value = node.val
            # reset head and tail
            if node == self.head:
                self.head = node.next
            if node == self.tail:
                self.tail = node.pre
            # remove node from double link list
            pre = node.pre
            next = node.next
            if pre:
                pre.next = next
            if next:
                next.pre = pre
            # drop the key
            del self.data[key]
            return value
        else:
            return 0

    # disable a key
    def invalidateKey(self, key):
        result = self.discard(key)
        # if find the key
        if result:
            self.size -= self.get_sizeof(result)
            return self.size
        else:
            return 0

    # LRU discard policy
    def LRU_policy(self):
        # abandon the head node
        key = self.head.key
        return self.invalidateKey(key)

    # random discard policy
    def RND_policy(self):
        # abdondon a random key
        key = random.choice(list(self.data.keys()))
        return self.invalidateKey(key)

    # get the value of key from db
    def get(self, key):
        self.n_query += 1
        self.request += 1
        # if find key-value in cache
        if key in self.data.keys():
            value = self.data[key].val
            # remove the node from the list
            self.invalidateKey(key)
            # append the node to the end of list
            self.append(key, value)
            return value
        else:
            self.missing += 1
            # missing signal
            return 0

    # append key-value node to the end of list
    def append(self, key, value):
        # append the node to the end of list
        node = ListNode(val=value, key=key, pre=self.tail)
        # update table
        self.data[key] = node
        # update size
        self.size += self.get_sizeof(value)
        # update linklist
        # if list is empty
        if self.head == None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node

    # set up key-value pair
    # use cas to solve the problem that two client update a key-value pair simultaneously
    def put(self, key, value):
        self.request += 1
        # impossible to cache that value
        if self.get_sizeof(value) > self.capacity:
            return 0
        # replace key
        elif key in self.data.keys():
            # remove the node from the list
            self.invalidateKey(key)
            while self.size + self.get_sizeof(value) > self.capacity:
                # abandon key according to policy
                if self.policy == "RANDOM":
                    self.RND_policy()
                elif self.policy == "LRU":
                    self.LRU_policy()
            # append the node to the end of list
            self.append(key, value)
        # add key
        else:
            while self.size + self.get_sizeof(value) > self.capacity:
                # abandon key according to policy
                if self.policy == "RANDOM":
                    self.RND_policy()
                elif self.policy == "LRU":
                    self.LRU_policy()
            # remove the node from the list
            self.invalidateKey(key)
            # append the node to the end of list
            self.append(key, value)

    # clear cache
    def clear(self):
        self.data = {}
        self.size = 0
        self.head = None
        self.tail = None

    # return a list of all key-value pair on the memcache
    # [[key, value]]
    def get_all(self) -> list:
        return list(map(lambda x: [x, self.data[x].val], self.data.keys()))

    # return the missing rate of cache
    def get_missing_rate(self):

        if self.n_query == 0:
            return 0.
        else:
            return self.missing / self.n_query

    # return hit_rate: float, miss_rate: float, item_num: int, item_size: float of this cache and requests_num
    def statistic(self):
        miss_rate = self.get_missing_rate()
        return 1 - miss_rate, miss_rate, len(self.data), self.size / (1024 * 1024), self.request
    
    # report the cache statistic to cloudwatch
    def report_statistics(self, cloudwatch):
        stats = self.statistic()
        self.stat_history.append(stats)
        cloudwatch.publish_metrics(stats[0], stats[1], stats[2], stats[3], stats[4])

    def __str__(self):
        string = "current size %s:\n" % self.size
        node = self.head
        while node is not None:
            string += str(node)
            string += "->"
            node = node.next
        string += "None"
        return string
