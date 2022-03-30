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
import socketserver
from datetime import datetime, timedelta
import time
import os
import sys
import threading
import queue
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import BirdBrains
import logging
from logging.handlers import TimedRotatingFileHandler
import requests
from win10toast import ToastNotifier

# Setup Toast Notifier
toaster = ToastNotifier()

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
logger.getChild('brains')
logger.setLevel(level)
fh = TimedRotatingFileHandler(log_file, when='d', interval=1, backupCount=30)
fm = logging.Formatter(fmt='%(asctime)s - %(name)s | %(levelname)s : %(lineno)d - %(message)s')
fh.setFormatter(fm)
logger.addHandler(fh)

logger.info('A little bird told me....')

# Ingest Reader Bot
brains = BirdBrains.birdBrains()

# Setup the queue
q = queue.Queue()


def bird_nest():
    """
    The Queue.
    """
    logger.debug('Queue Running...')
    while True:
        package = q.get(block=True)
        logger.debug('PACKAGE: %s' % package)

        if package:
            get_tweets = brains.get_tweets()
            collect_tweets = get_tweets[0]
            tweets = get_tweets[1]
            if collect_tweets:
                try:
                    sorted_tweets = sorted(collect_tweets, key=lambda i: (i['post_count']), reverse=False)[:15]
                    logger.debug('SORTED TWEETS: %s' % sorted_tweets)
                    logger.info('Grabbing a pre-built tweet...')
                    get_tweet_id = brains.find_random_tweet(tweet_list=sorted_tweets)
                    logger.debug('Tweet ID: %s' % get_tweet_id)
                    get_tweet = next((twt for twt in tweets if twt['id'] == get_tweet_id), False)
                    post_count = int(get_tweet['post_count'])
                    logger.debug('SELECTED TWEET: %s' % get_tweet)
                    posted_tweet = brains.post_tweet(tweet=get_tweet)
                    tweet_data = posted_tweet._json
                    logger.info('A Little Bird told me: %s' % tweet_data['text'])
                    logger.debug('Tweet posted: %s' % tweet_data)
                    post_count += 1
                    brains.update_database(key="post_count", value=post_count, tid=get_tweet_id)
                    new_id = str(tweet_data['id'])
                    brains.update_database(key='last_posted_id', value=new_id, tid=get_tweet_id)
                    new_post_time = tweet_data['created_at']
                    # Tue Jul 20 05:18:56 +0000 2021
                    corrected_post_time = datetime.strptime(new_post_time, "%a %b %d %H:%M:%S %z %Y")
                    logger.debug('CORRECTED Time: %s' % corrected_post_time)
                    logger.debug('CORRECTED TYPE: %s' % type(corrected_post_time))
                    updated_time = corrected_post_time.strftime("%m/%d/%Y, %H:%M:%S")
                    logger.debug('UPDATED TIME: %s' % updated_time)
                    logger.debug('UPDATED Type: %s' % type(updated_time))
                    brains.update_database(key="last_posted", value=updated_time, tid=get_tweet_id)
                    logger.info('Database Tweet Specs Saved!')

                except Exception as e:
                    logger.error('The collected tweet didn\'t work', e)


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
        logger.info('Starting service...')
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.start_time = None
        self.end_time = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        logger.info('Starting Little Bird')
        self.main()

    def internet_check(self):
        try:
            test = requests.get(url='http://google.com', timeout=2)
            logger.debug('Internet Connected.', test)
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as t:
            logger.warning('Internet connection cannot be found.', t)
            return False

    def main(self):
        """
        The main loop
        """
        logger.info('Little Bird started.')
        # set Initial start and end times
        self.end_time = datetime.now()
        # try:
        self.start_time = brains.open_ads_db()['StartDate']

        logger.debug('Showing Startup Toaster....')
        toaster.show_toast(
            'Little Bird',
            'A little bird has started',
            icon_path=None,
            threaded=True,
            duration=10
        )
        logger.debug('Finished startup Toaster.')

        if not self.start_time:
            self.start_time = datetime.now()
            logger.debug('The start time was empty.  Updating with a real date: %s' % self.start_time)
            start_date_to_string = self.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            brains.update_start_time(start_time=start_date_to_string)
        elif type(self.start_time) != datetime:
            logger.debug('Converting date time to Datetime')
            self.start_time = datetime.strptime(self.start_time, '%m/%d/%Y, %H:%M:%S')
        logger.info('Start Time updated from DB: %s' % self.start_time)
        brains.update_start_time(start_time=self.start_time.strftime("%m/%d/%Y, %H:%M:%S"))
        self.end_time = datetime.now()
        brains.popup_tweet(title='Little Bird!', msg='Little Bird has Started!')
        # except Exception as e:
        #     logger.error('The fit hit the shan!', e)

        while True:
            if self.internet_check():
                if (self.start_time + timedelta(hours=int(config['interval']))) < self.end_time:
                    self.start_time = datetime.now()
                    logger.debug('LOOP: %s' % self.start_time)
                    logger.info('Updating Start Date...')
                    brains.update_start_time(self.start_time)
                    logger.info('Starting Tweet Function...')
                    brains.popup_tweet(title='Starting Tweet Function...', msg='Tweeting...')
                    q.put(self.start_time)
                self.end_time = datetime.now()
            time.sleep(30)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(littleBird)

    # test = littleBird()
    # test.main()
