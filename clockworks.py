from datetime import datetime, timedelta
import time
import os
import sys
import threading
import queue

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

