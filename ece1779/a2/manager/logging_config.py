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