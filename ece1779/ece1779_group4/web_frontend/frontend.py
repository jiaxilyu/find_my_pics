from flask import render_template, url_for, request, send_from_directory
from flask import json
from web_frontend import frontendapp
from web_frontend import endpoint_host
from web_frontend import logger
import requests

# the "Upload" page
@frontendapp.route("/")
def index():
    return render_template("index.html", host=endpoint_host)

# the "Query" page
@frontendapp.route("/query")
def query():
    return render_template("query.html", host=endpoint_host)

# the "Keys" page
@frontendapp.route("/keys")
def keys():
    # fetch all the keys from the memcache instance's endpoint
    response = requests.post('http://localhost:5000/api/list_keys')
    jsonResponse = response.json()
    keys = jsonResponse["keys"] if jsonResponse["success"] == "true" else []
    logger.info("Keys fetched: " + str(keys))
    # pass the array to jinja template to render HTML
    return render_template("keys.html", host=endpoint_host, keys=keys)

# the "Configurations" page
@frontendapp.route("/configurations")
def configurations():
    # fetch all the cached keys
    keysResp = requests.get('http://localhost:5000/api/list_cached_keys')
    keysJsonResp = keysResp.json()
    cached_keys = keysJsonResp["keys"] if keysJsonResp["success"] == "true" else []
    logger.info("Cached keys fetched: " + str(cached_keys))
    # fetch the cache configuration parameters
    cfgResp = requests.get('http://localhost:5000/api/cache_config')
    cfgJsonResp = cfgResp.json()
    cfg = cfgJsonResp["config"] if cfgJsonResp["success"] == "true" else [0, -1, 'ERROR']
    logger.info("Cache config fetched: " + str(cfg))
    # pass them to jinja template to render HTML
    return render_template("configurations.html", host=endpoint_host, cached_keys=cached_keys, curr_cache_size=cfg[1],
                           curr_policy=cfg[2])

# the "Statistics" page
@frontendapp.route("/statistics")
def statistics():
    # get an array of statistics over the past 10 minutes
    # - each element is [ hit_rate: float, miss_rate: float, item_num: int, item_size: float, requests_num: int]
    response = requests.get('http://localhost:5000/api/statistics')
    jsonResponse = response.json()
    data = jsonResponse["stats"] if jsonResponse["success"] == "true" else [[], [], [], [], []]
    # convert to five separate arrays
    hit_rates = [item[0] for item in data]
    miss_rates = [item[1] for item in data]
    item_nums = [item[2] for item in data]
    item_sizes = [item[3] for item in data]
    requests_nums = [item[4] for item in data]
    return render_template("statistics.html", host=endpoint_host, hit_rates=hit_rates, miss_rates=miss_rates, item_nums=item_nums, item_sizes=item_sizes, requests_nums=requests_nums)

# serve the logfiles
@frontendapp.route('/logs/<path:path>')
def host_logs(path):
    return send_from_directory('../logs', path)