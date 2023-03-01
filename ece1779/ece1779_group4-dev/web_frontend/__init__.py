from flask import Flask
import urllib.request
import platform
import logging
import sys
import os

# Config ang launch the logging service
logfile = './logs/frontend.log'
if not os.path.exists('logs'):
    os.mkdir('logs')
with open(logfile, 'w') as f:
    f.write('\n')
logger = logging
logger.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    handlers=[logging.FileHandler(logfile), logging.StreamHandler(sys.stdout)])

# Because we need to send request to our endpoint server on frontend JavaScript,
#  the endpoint address is declared here and then pass to all the HTML templates
global endpoint_host
if platform.system() == "Linux":
    # if it's running on AWS, get the external IP
    external_ip = urllib.request.urlopen('http://v4.ident.me').read().decode('utf8')
else:
    external_ip = "127.0.0.1"
endpoint_host = 'http://' + external_ip + ':5002'

# Launch the Flask application
frontendapp = Flask(__name__)
from web_frontend import frontend