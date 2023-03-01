from flask import Flask
from manager.manager import Manager
import threading
import time
import urllib.request
import platform
import logging
import sys
import os

# Config ang launch the logging service
logfile = './logs/manager.log'
if not os.path.exists('logs'):
    os.mkdir('logs')
with open(logfile, 'w') as f:
    f.write('\n')
logger = logging
logger.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(message)s',
                   datefmt='%m/%d/%Y %H:%M:%S',
                   handlers=[logging.FileHandler(logfile), logging.StreamHandler(sys.stdout)])

global manager
manager = Manager()


# Update statistics every minute
def updater():
    while True:
        manager.update_stat()
        time.sleep(60)


# create a thread updating stats
t = threading.Thread(target=updater)
t.start()

managerapp = Flask(__name__)

from manager import endpoint
from manager import frontend
