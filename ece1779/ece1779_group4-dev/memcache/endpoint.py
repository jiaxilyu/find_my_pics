from flask import render_template, url_for, request
from flask import json
from memcache import webapp
from memcache import db
from memcache import memcache
from memcache.logging_config import logger
import base64
from flask_cors import CORS, cross_origin

import io
import boto3
import os


def delete_all_objects_from_s3():
    """
    This function deletes all files in a folder from S3 bucket
    :return: None
    """
    bucket_name = "ece1779-g4"

    s3_client = boto3.client("s3")

    # First we list all files in folder
    response = s3_client.list_objects_v2(Bucket=bucket_name, )
    files_in_folder = response["Contents"]
    files_to_delete = []

    for f in files_in_folder:
        files_to_delete.append({"Key": f["Key"]})

    response = s3_client.delete_objects(
        Bucket=bucket_name, Delete={"Objects": files_to_delete}
    )


# Process the user's uploaded key and image
@webapp.route('/api/upload', methods=['POST'])
@cross_origin()
def upload_key_and_image():
    # fetch key and file info from the submitted HTML Form
    key = request.form.get('key')
    file = request.files["file"]
    file_name = file.filename
    # read the file data, encode with base64, and then put into memcache
    content = file.read()
    memcache.put(key, base64.b64encode(content).decode())
    # add the filt path or update the existing file path in the database
    if db.query_keypath(key):
        db.update_keypath(key, file_name)
    else:
        db.add_keypath(key, file_name)
    # save the file in s3 instance
    s3 = boto3.client('s3')
    s3.upload_fileobj(io.BytesIO(content), 'ece1779-g4', file_name)
    # log the saved key and filename
    logger.info("Uploaded key: " + key + " filename: " + file_name)
    # send response
    response = webapp.response_class(
        response=json.dumps({"success": "true", "key": [key]}),
        status=200,
        mimetype='application/json'
    )
    return response


# Delete all the keys anva files
@webapp.route('/api/delete_all', methods=['POST'])
def delete_all():
    # clear both the memcache and database
    memcache.clear()
    db.clear_keypath()
    delete_all_objects_from_s3()
    logger.info("All keys and files were deleted")
    # send response
    response = webapp.response_class(
        response=json.dumps({"success": "true"}),
        status=200,
        mimetype='application/json'
    )
    return response


# Query a given key
@webapp.route('/api/key/<key>', methods=['POST'])
def query_key(key):
    try:
        # try to get the base64 encoded file content from the memcache
        image = memcache.get(key)  # FileStorage
        if image:
            # if existed, directly serve it as the file content in response
            logger.info("Image founded in cache")
            content = image
        else:
            # otherwise, fetch file path from the database
            path = db.query_keypath(key)[0][1]
            logger.info("Image is not in cache, fetched from database")
            # query from s3
            s3 = boto3.resource('s3')
            bucket = s3.Bucket('ece1779-g4')
            obj = bucket.Object(path)
            response = obj.get()
            file_stream = response['Body']
            content = file_stream.read()
            content = base64.b64encode(content).decode()
            memcache.put(key, content)

        # send response
        response = webapp.response_class(
            response=json.dumps({"success": "true", "key": [key], "content": content}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        # if something went wrong, such as the key not found, log the error and send nothing
        logger.error("Query key error: " + str(e))
        response = webapp.response_class(
            response=json.dumps({"success": "false", "key": [key], "content": None}),
            status=400,
            mimetype='application/json'
        )
    finally:
        return response


# Clear all the content in memcache
@webapp.route('/api/clear_cache', methods=['POST'])
def clear_cache():
    memcache.clear()
    logger.info("Cache cleared")
    response = webapp.response_class(
        response=json.dumps({"success": "true"}),
        status=200,
        mimetype='application/json'
    )
    return response


# List all the keys
@webapp.route('/api/list_keys', methods=['POST'])
def list_keys():
    # fetch all the keys and corresponding file paths from the database
    kps = db.query_keypath()
    keys = [k for k, p in kps]
    # send response
    response = webapp.response_class(
        response=json.dumps({
            "success": "true",
            "keys": keys
        }),
        status=200,
        mimetype='application/json'
    )
    return response


# ==============================================================
# The following routes are for the communication between the frontend instance and memcache instance

# List the statistic informations
@webapp.route('/api/statistics')
def statistics():
    # (hit_rate, miss_rate, item_num, size, request_num) in deque
    stats = memcache.stat_history
    response = webapp.response_class(
        response=json.dumps({
            "success": "true",
            "stats": tuple(stats)
        }),
        status=200,
        mimetype='application/json'
    )
    return response


# List all the cached keys
@webapp.route('/api/list_cached_keys')
def list_cached_keys():
    cached_keys = list(map(lambda x: x[0], memcache.get_all()))
    response = webapp.response_class(
        response=json.dumps({
            "success": "true",
            "keys": cached_keys
        }),
        status=200,
        mimetype='application/json'
    )
    return response


# Fetch the current cache configuration
@webapp.route('/api/cache_config')
def get_cache_config():
    cache_config = db.query_memcacheconfig()[0]
    response = webapp.response_class(
        response=json.dumps({
            "success": "true",
            "config": cache_config
        }),
        status=200,
        mimetype='application/json'
    )
    return response


# Update the cache configuration
@webapp.route('/api/update_cache_config', methods=['POST'])
def update_cache_config():
    size = request.form.get('size')
    policy = request.form.get('policy')
    logger.info("Cache Config Updated: size=" + size, " policy=" + policy)
    db.update_memcacheconfig((size, policy))
    memcache.refreshConfiguration(db)
    response = webapp.response_class(
        response=json.dumps({"success": "true", "size": size, "policy": policy}),
        status=200,
        mimetype='application/json'
    )
    return response
