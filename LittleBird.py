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
import reader_bot

# Ingest Reader Bot
rb = reader_bot.readerBotTools()

# This setup with the Timedelta can function as the method for running the tweet bot.
''' START EXAMPLE '''
# start_time = datetime.now()
# time.sleep(1)
# end_time = datetime.now()
# time_diff = end_time - start_time
# time_diff += timedelta(days=1)
# print(time_diff)
# if time_diff > timedelta(days=1, seconds=5):
#     print('TOO LONG!')
# else:
#     print('TOO SHORT.')
# ''' END THE EXAMPLE '''
#
# start_time = datetime.now()
# time_diff = start_time - start_time
# while time_diff < timedelta(seconds=10):
#     end_time = datetime.now()
#     time_diff = end_time - start_time
# print(time_diff)
# print('Time\'s up!')

# Setup the queue
q = queue.Queue()


def bird_nest():
    """
    The Queue.
    """
    print('Fart')


# Create and start a Thread
t = threading.Thread(target=bird_nest, name='BirdNest')
t.setDaemon(True)
t.start()


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
        pass


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(littleBird)

