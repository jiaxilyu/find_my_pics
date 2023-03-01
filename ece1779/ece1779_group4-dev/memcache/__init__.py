import time
from flask import Flask
from memcache.database import create_db
from memcache.Memcache import MemCache
from memcache.logging_config import logger
from memcache.cloudwatch import CloudWatch
import threading
from flask_cors import CORS
import os
import boto3
import datetime

# Create a folder to store all the images
if not os.path.exists('images'):
    os.mkdir('images')

# Update statistics every 5 seconds
def updater():
    while True:
        update_statistics()
        time.sleep(5)

def update_statistics():
    memcache.report_statistics(cloudwatch)


# Launch the flask application
webapp = Flask(__name__)

# Config the CORS 
CORS(webapp, supports_credentials=True)

# Config memcache and database
global db
global memcache

db = create_db()
db.initialize()
cloudwatch = CloudWatch()
cfg = db.query_memcacheconfig()[0]
memcache = MemCache(cfg[1] * 1024 * 1024, cfg[2])

# create a thread updating stats every 5 seconds
t = threading.Thread(target=updater)
t.start()

from memcache import endpoint
