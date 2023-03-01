import requests
from flask import render_template, url_for, request, send_from_directory
from flask import json

from manager import logger
from manager import managerapp
from manager import manager


# Endpoint for adding a node
@managerapp.route("/api/add_node", methods=['POST'])
def add_node():
    flag = manager.add_node()
    response = managerapp.response_class(
        response=json.dumps({"success": "true" if flag else "false"}),
        status=200 if flag else 403,
        mimetype='application/json',
    )
    return response


# Endpoint for removing a node
@managerapp.route("/api/remove_node>", methods=['POST'])
def remove_node():
    flag = manager.remove_node()
    response = managerapp.response_class(
        response=json.dumps({"success": "true" if flag else "false"}),
        status=200 if flag else 403,
        mimetype='application/json',
    )
    return response


# Endpoint for querying an image
@managerapp.route("/api/key/<key>", methods=['POST'])
def query(key):
    node = manager.get_assigned_node(key)

    request_url = 'http://' + str(node.ip) + ':' + str(node.port) + '/api/key/' + key

    resp = requests.post(url=request_url)

    if resp.json()['success'] == 'true':
        manager.key_node_cache[node.node_id].add(key)
        response = managerapp.response_class(
            response=json.dumps({"success": "true", "key": key, "content": resp.json()['content']}),
            status=200,
            mimetype='application/json',
        )
    else:
        response = managerapp.response_class(
            response=json.dumps({"success": "false", "key": key, "content": None}),
            status=400,
            mimetype='application/json'
        )

    return response


# Endpoint for uploading an image
@managerapp.route("/api/upload", methods=['POST'])
def upload():
    key = request.form.get('key')
    file = request.files["file"]
    file_name = key + '.' + file.filename.split('.')[1]

    node = manager.get_assigned_node(key)

    host = 'http://' + str(node.ip) + ':' + str(node.port)

    resp = requests.post(url=host + "/api/upload", data={'key': key}, files={'file': (file_name, file)})

    if resp.json()['success'] == 'true':
        manager.key_node_cache[node.node_id].add(key)

    response = managerapp.response_class(
        response=json.dumps({"success": "true", "host": host}),
        status=200,
        mimetype='application/json'
    )
    return response


# Endpoint for getting number of nodes
@managerapp.route("/api/getNumNodes", methods=['POST'])
def get_num_nodes():
    response = managerapp.response_class(
        response=json.dumps({"success": "true", "numNodes": manager.num_nodes}),
        status=200,
        mimetype='application/json'
    )
    return response


# Endpoint for getting hit and miss rates
# - url params: rate = 'miss' or 'hit'
@managerapp.route("/api/getRate", methods=['POST'])
def get_rate():
    rate = request.args.get('rate')
    if rate == 'miss':
        curr_miss_rate = 0.0
        response = managerapp.response_class(
            response=json.dumps({"success": "true", "rate": "miss", "value": curr_miss_rate}),
            status=200,
            mimetype='application/json'
        )
        return response
    elif rate == 'hit':
        curr_hit_rate = 0.0
        response = managerapp.response_class(
            response=json.dumps({"success": "true", "rate": "hit", "value": curr_hit_rate}),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        response = managerapp.response_class(
            response=json.dumps({"success": "false", "error": "Invalid params"}),
            status=400,
            mimetype='application/json'
        )
        return response


# Endpoint for configuring cache settings
# - url params: mode = 'auto' or 'manual', numNodes = int, cacheSize = int, policy = 'LRU' or 'RR', expRatio = int, shrinkRatio = int, maxMiss = float, minMiss = float
@managerapp.route("/api/configure_cache", methods=['POST'])
def configure_cache():
    try:
        mode = request.args.get('mode')
        if mode != 'auto' and mode != 'manual':
            raise Exception("Invalid mode")
        num_nodes = int(request.args.get('numNodes'))
        if num_nodes <= 0:
            raise Exception("Invalid number of nodes")
        cache_size = int(request.args.get('cacheSize'))
        if cache_size < 0:
            raise Exception("Invalid cache size")
        policy = request.args.get('policy')
        if policy != 'LRU' and policy != 'RR':
            raise Exception("Invalid policy")
        exp_ratio = int(request.args.get('expRatio'))
        if exp_ratio <= 0:
            raise Exception("Invalid expansion ratio")
        shrink_ratio = float(request.args.get('shrinkRatio'))
        if shrink_ratio <= 0 or shrink_ratio > 1:
            raise Exception("Invalid shrink ratio")
        max_miss = float(request.args.get('maxMiss'))
        if max_miss <= 0 or max_miss > 1:
            raise Exception("Invalid max miss rate")
        min_miss = float(request.args.get('minMiss'))
        if min_miss <= 0 or min_miss > 1:
            raise Exception("Invalid min miss rate")
        manager.configure(mode, num_nodes, cache_size, policy, max_miss, min_miss, exp_ratio, shrink_ratio)
        response = managerapp.response_class(
            response=json.dumps(
                {"success": "true", "mode": mode, "numNodes": num_nodes, "cacheSize": cache_size, "policy": policy}),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        err_msg = "Invalid params: " + str(e)
        response = managerapp.response_class(
            response=json.dumps({"success": "false", "error": err_msg}),
            status=400,
            mimetype='application/json'
        )
        return response


# Endpoint for deleting all keys and values from the application
@managerapp.route("/api/delete_all", methods=['POST'])
def delete_all():
    for node in manager.memcache_nodes.values():
        if node.is_active:
            manager.key_node_cache[node.node_id] = set()
            request_url = 'http://' + str(node.ip) + ':' + str(node.port) + "/api/delete_all"
            requests.post(url=request_url)
    response = managerapp.response_class(
        response=json.dumps({"success": "true"}),
        status=200,
        mimetype='application/json'
    )
    return response


# Endpoint for listing all keys
@managerapp.route("/api/list_keys", methods=['POST'])
def list_keys():
    for node in manager.memcache_nodes.values():
        if node.is_active:
            request_url = 'http://' + str(node.ip) + ':' + str(node.port) + "/api/list_keys"
            resp = requests.post(url=request_url)
            response = managerapp.response_class(
                response=json.dumps({
                    "success": "true",
                    "keys": resp.json()['keys']
                }),
                status=200,
                mimetype='application/json'
            )
        break

    return response


# Endpoint for clearing the cache
@managerapp.route("/api/clear_cache", methods=['POST'])
def clear_cache():
    for node in manager.memcache_nodes.values():
        if node.is_active:
            manager.key_node_cache[node.node_id] = set()
            request_url = 'http://' + str(node.ip) + ':' + str(node.port) + "/api/clear_cache"
            requests.post(url=request_url)

    response = managerapp.response_class(
        response=json.dumps({"success": "true"}),
        status=200,
        mimetype='application/json'
    )
    return response

@managerapp.route("/api/getThreshold", methods=['GET'])
def get_threshold():
    max_miss = manager.max_miss
    min_miss = manager.min_miss
    response = managerapp.response_class(
            response=json.dumps({"success": "true", "max_miss": max_miss, "min_miss":min_miss}),
            status=200,
            mimetype='application/json'
    )
    return response