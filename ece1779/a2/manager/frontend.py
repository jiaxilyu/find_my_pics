from flask import render_template, url_for, request, send_from_directory
from flask import json

from manager import logger
from manager import managerapp
from manager import manager

# The frontend for Manager Application - Statistics Page
@managerapp.route("/")
def index():
    history = manager.stat_history
    node_nums = [item[0] for item in history]
    hit_rates = [item[1] for item in history]
    miss_rates = [item[2] for item in history]
    item_nums = [item[3] for item in history]
    item_sizes = [item[4] for item in history]
    requests_nums = [item[5] for item in history]
    return render_template('index.html', node_nums=node_nums, hit_rates=hit_rates, miss_rates=miss_rates, item_nums=item_nums, item_sizes=item_sizes, requests_nums=requests_nums)

# The frontend for Manager Application - Configuration Page
@managerapp.route("/configurations")
def config():
    # Host of endpoint
    host = 'http://localhost:5002'
    # Cache node size in MB
    curr_cache_size = manager.cache_size
    # Cache node replacement policy: 'LRU' or 'RR'
    curr_policy = manager.policy
    # Cache pool resizing mode: 'auto' or 'manual'
    curr_pool_mode = manager.mode
    # Number of cache nodes in the pool when in manual mode
    curr_pool_num_nodes = manager.num_nodes
    # Max miss rate threshold for increasing cache pool size
    curr_pool_max_miss_rate = manager.max_miss
    # Min miss rate threshold for decreasing cache pool size
    curr_pool_min_miss_rate = manager.min_miss
    # Ratio by which to expand the cache pool
    curr_pool_expand_ratio = manager.exp_ratio
    # Ratio by which to shrink the cache pool
    curr_pool_shrink_ratio = manager.shrink_ratio
    return render_template('configurations.html', host=host, curr_cache_size=curr_cache_size, curr_policy=curr_policy, curr_pool_mode=curr_pool_mode, curr_pool_num_nodes=curr_pool_num_nodes, curr_pool_max_miss_rate=curr_pool_max_miss_rate, curr_pool_min_miss_rate=curr_pool_min_miss_rate, curr_pool_expand_ratio=curr_pool_expand_ratio, curr_pool_shrink_ratio=curr_pool_shrink_ratio)
