"""
A LITTLE BIRD TOLD ME
-------------------------------------------------------------------
This is the Twitter Bot that will run in the background, occasionally checking Twitter for tween statuses and such,
And then posting certain things on my behalf.

GOALS:
1. Have it post a "random" ad for me every X number of times that I tweet or retweet for reals.
2. Have it automatically Follow people who like, or retweet my ads.
3. Have it Direct Message people who like and retweet my ads, or who comment on them.

CHALLENGES:
1. Need to keep track of automatically posted ads.  I think this could be as simple as saving the last post ID in the
ad itself.
2. Have it check for the number of tweets/retweets made (and require at least 1 tweet)
"""

from datetime import datetime, timedelta
import time
import os
import sys
import threading
import queue
import win32file
import win32con
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import BirdBrains
import logging
from logging.handlers import TimedRotatingFileHandler

config = BirdBrains.get_configuration()
sys_path = sys.path[0]

# Setup logging system
log_filename = 'bird_song.log'
log_root = os.path.join(sys_path, 'logs')
log_file = os.path.join(log_root, log_filename)
if config['debug_logging'] == True or config['debug_logging'] == 'True':
    level = logging.DEBUG
else:
    level = logging.INFO
logger = logging.getLogger('bird_song')
logger.setLevel(level)
fh = TimedRotatingFileHandler(log_file, when='d', interval=7, backupCount=30)
fm = logging.Formatter(fmt='%(asctime)s - %(name)s | %(levelname)s : %(lineno)d - %(message)s')
fh.setFormatter(fm)
logger.addHandler(fh)

logger.info('A little bird told me....')

# Ingest Reader Bot
brains = BirdBrains.birdBrains()

# # Setup the queue
# q = queue.Queue()
#
#
# def bird_nest():
#     """
#     The Queue.
#     """
#     print('Fart')
#
#
# # Create and start a Thread
# t = threading.Thread(target=bird_nest, name='BirdNest')
# t.setDaemon(True)
# t.start()


class littleBird(win32serviceutil.ServiceFramework):
    """
    A simple listener for running Twitter events.
    """
    _svc_name_ = 'LittleBird'
    _svc_display_name_ = "Little Bird"
    queue_prep = []

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

        # set Initial start and end times
        # TODO: Start time should eventually be saved in a document, for when the computer is off.
        self.start_time = datetime.now()
        brains.update_start_time(start_time=self.start_time)
        self.end_time = datetime.now()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        """
        The main loop
        """

        while True:
            if (self.start_time + timedelta(hours=int(config['interval']))) < self.end_time:
                self.start_time = datetime.now()
            self.end_time = datetime.now()
            time.sleep(30)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(littleBird)

