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

# This setup with the Timedelta can function as the method for running the tweet bot.
''' START EXAMPLE '''
start_time = datetime.now()
time.sleep(1)
end_time = datetime.now()
time_diff = end_time - start_time
time_diff += timedelta(days=1)
print(time_diff)
if time_diff > timedelta(days=1, seconds=5):
    print('TOO LONG!')
else:
    print('TOO SHORT.')
''' END THE EXAMPLE '''

start_time = datetime.now()
time_diff = start_time - start_time
while time_diff < timedelta(seconds=10):
    end_time = datetime.now()
    time_diff = end_time - start_time
print(time_diff)
print('Time\'s up!')


def bird_bot():
    """
    The Queue.
    """
    print('Fart')


# Create and start a Thread
th = threading.Thread(target=bird_bot, name='BirdBot')
th.setDaemon(True)
th.start()


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

