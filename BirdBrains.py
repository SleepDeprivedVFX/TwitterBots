import configparser
import twitter
import tweepy
import json
import sys
import os
from datetime import datetime, timedelta
from dateutil import parser
import time
import random
import math
import pprint
import logging
from win10toast import ToastNotifier

# Setup Toaster
toaster = ToastNotifier()

twitter_keys = [
    "coordinates",
    "geo",
    "favorited",
    "hashtags",
    "id",
    "lang",
    "place",
    "source",
    "text",
    "truncated",
    "urls",
    "user",
    "user_mentions",
    "retweet_count",
    "retweeted_status",
    "retweeted"
]


def find_file(file_name=None, folder=None):
    path = None
    if file_name:
        sys_path = sys.path
        try:
            if folder:
                path = [f for f in sys_path if os.path.isfile(f + '/' + folder + '/' + file_name)][0] + '/' + folder + \
                       '/' + file_name
                path = path.replace('\\', '/')
            else:
                path = [f for f in sys_path if os.path.isfile(f + '/' + file_name)][0] + '/' + file_name
                path = path.replace('\\', '/')
        except IndexError as e:
            raise e
    return path


def get_configuration():
    '''
    Get the configuration for all twitter activities.
    :return: config_file
    '''

    # Get System path and config file
    config_file = 'twit_config.cfg'
    config_path = find_file(file_name=config_file)
    # Create the configuration connection
    configuration = configparser.ConfigParser()
    configuration.read(config_path)

    config = {}
    # Parse out the configuration to local variables
    # Shotgun
    config['consumer_api_key'] = configuration.get('Consumer', 'api_key')
    config['consumer_secret_key'] = configuration.get('Consumer', 'api_secret_key')
    config['api_token'] = configuration.get('Access Tokens', 'api_token')
    config['api_secret'] = configuration.get('Access Tokens', 'api_secret')
    config['user'] = configuration.get('User', 'screen_name')
    config['record_count'] = configuration.get('params', 'record_count')
    config['read_length'] = configuration.get('params', 'read_length')

    # Debug logging
    config['debug_logging'] = configuration.get('logging', 'debug_logging')

    # Timers
    config['interval'] = configuration.get('timers', 'tweet_interval')
    return config


logger = logging.getLogger('bird_song.brains')
logger.info('Bird Brains Thinking...')
config = get_configuration()
if config['debug_logging'] == True or config['debug_logging'] == 'True':
    level = logging.DEBUG
else:
    level = logging.INFO
logger.setLevel(level)


class birdBrains(object):
    '''
    The smarts for the Little Bird
    '''

    def __init__(self):
        super(birdBrains, self).__init__()

        # Setup and authorize Twitter connection and api
        auth = tweepy.OAuthHandler(config['consumer_api_key'], config['consumer_secret_key'])
        auth.set_access_token(config['api_token'], config['api_secret'])
        self.api = tweepy.API(auth)

        # Collect and create the ads database
        self.ads = self.open_ads_db()

    def open_ads_db(self):
        ads_db = None
        ads = None
        ads_file = 'tweets.json'
        ads_path = find_file(file_name=ads_file, folder='data')
        if ads_path:
            with open(ads_path, 'r+') as ads:
                ads_db = json.load(ads)
                logger.info('Ads DB opened.')
            if ads_db:
                ads = ads_db
            else:
                ads = None
        return ads

    def update_start_time(self, start_time=None):
        if start_time:
            if type(start_time) == datetime:
                start_time = start_time.strftime("%m/%d/%Y, %H:%M:%S")
            logger.debug('Start time added: %s' % start_time)
            get_current_db = self.open_ads_db()
            get_current_db['StartDate'] = start_time
            ads_file = 'tweets.json'
            logger.info('CDB: %s' % get_current_db['StartDate'])
            ads_path = find_file(file_name=ads_file, folder='data')
            if ads_path:
                save = json.dumps(get_current_db, sort_keys=True, indent=4, separators=(',', ': '))
                with open(ads_path, 'w+') as save_file:
                    save_file.write(save)
                logger.info('Date Updated')

    def update_database(self, key=None, value=None, tid=None, val_type=None):
        if not val_type:
            val_type = str
        if key and tid:
            tid = int(tid)
            logger.info('Updating the Database')
            db = self.open_ads_db()
            logger.debug('Ads DB collected.')
            if not value and val_type == str:
                value = ""
                logger.debug('Value is empty')
            elif not value and val_type == bool:
                value = False
                logger.debug('Value is False')
            elif not value and val_type == int:
                value = 0
                logger.debug('Value is %i' % value)
            else:
                logger.debug('Value is %s' % value)

            # Set the new value in the database
            logger.debug('Setting the value to %s' % value)
            c = len(db['Tweets']) + 1
            logger.debug('DB length + 1 = %s' % c)
            for x in range(0, c):
                logger.debug('ITERATING: %s' % db['Tweets'][x])
                if db['Tweets'][x]['id'] == tid:
                    logger.debug('ID found: %s' % tid)
                    logger.debug('Updating database...')
                    db['Tweets'][x][key] = value
                    logger.debug('JSON updated')
                    logger.debug('ENTRY: %s' % db['Tweets'][x])
                    break

            logger.info('Saving database...')
            ads_file = 'tweets.json'
            ads_path = find_file(file_name=ads_file, folder='data')
            if ads_path:
                save = json.dumps(db, sort_keys=True, indent=4, separators=(',', ': '))
                with open(ads_path, 'w+') as save_file:
                    save_file.write(save)
                    logger.info('File saved.')

    def find_random_tweet(self, tweet_list=None):
        logger.info('Finding Random Tweet...')
        tweet_id = None
        if tweet_list:
            total_tweets = len(tweet_list)
            rand = random.randrange(0, (total_tweets + 1))
            logger.debug('Random Number: %s' % rand)
            tweet_id = tweet_list[rand]['id']
            logger.debug('Tweet ID: %s' % tweet_id)
        logger.info('Random Tweet ID: %s' % tweet_id)
        return tweet_id

    def track_tweet(self, tweet=None):
        if tweet:
            # TODO: Make this save the tweet into the post_watch_list.json document.
            pass

    def popup_tweet(self, title=None, msg=None):
        try:
            logger.debug('Popup Toaster Message sent...')
            toaster.show_toast(
                title=title,
                msg=msg,
                icon_path=None,
                threaded=True,
                duration=10
            )
            logger.debug('Popup Toaster Message Done.')
        except Exception as e:
            logger.error('POP UP FAILED!!! {}'.format(e))

    def get_tweets(self):
        db = self.open_ads_db()
        tweets = db['Tweets']
        logger.debug('TWEETS: %s' % tweets)
        collect_tweets = []
        try:
            for tweet in tweets:
                logger.debug('ACTIVE AD: %s' % tweet['active_ad'])
                if tweet['active_ad']:
                    logger.debug(type(tweet))
                    logger.debug('TWEET: %s' % tweet)
                    collect_tweets.append(
                        {
                            'id': tweet['id'],
                            'last_posted': tweet['last_posted'],
                            'last_posted_id': tweet['last_posted_id'],
                            'post_count': tweet['post_count']
                        }
                    )
        except Exception as e:
            logger.error('This shit dont work! %s' % e)
        return collect_tweets, tweets

    def get_tweet(self, tid=None):
        tweet = None
        if tid:
            db = self.open_ads_db()
            tweets = db['Tweets']
            tweet = [t for t in tweets if t['id'] == tid][0]
        return tweet

    def post_tweet(self, tweet=None, retries=0):
        logger.debug('post_tweet started.')
        sent = None
        if tweet:
            try:
                logger.debug('Sending Tweet: %s' % tweet)
                logger.debug('TYPE: %s' % type(tweet))
                for key, val in tweet.items():
                    logger.debug('%s: %s' % (key, val))

                # Get file if it exists
                file_name = tweet['image']

                message = '''
{text}

{link}

{hash_tags}
                '''.format(text=tweet['text'], link=tweet['link'], hash_tags=tweet['hashtags'])

                if message:
                    # Testing sending an image first...
                    if file_name:
                        post_id = self.api.update_with_media(file_name, message)
                    else:
                        post_id = self.api.update_status(status=message)
                    sent = post_id
            except Exception as e:
                logger.error('POST TWEET FAILED: %s' % e)
                retries += 1
                if retries <= 5:
                    logger.info('Retrying...  Attempt #{0}'.format(retries))
                    logger.info('Killing bad Tweet...')
                    # TODO: This is where the popups would be nice.
                    get_tweet = self.get_tweet(tid=tweet['id'])
                    failures = get_tweet['failures']
                    failures += 1
                    self.update_database(key='failures', value=failures, tid=tweet['id'], val_type=int)
                    if failures > 5:
                        self.update_database(key='active_ad', value=False, tid=tweet['id'], val_type=bool)
                    time.sleep(5)
                    logger.info('Getting new tweet...')
                    get_tweets = self.get_tweets()
                    collect_tweets = get_tweets[0]
                    tweets = get_tweets[1]
                    get_tweet_id = self.find_random_tweet(tweet_list=collect_tweets)
                    get_tweet = next((twt for twt in tweets if twt['id'] == get_tweet_id), False)
                    logger.info('Trying the next tweet: %s' % get_tweet)
                    logger.info('Sending back through...')
                    logger.debug('Retry tweet: %s' % get_tweet)
                    self.post_tweet(tweet=get_tweet, retries=retries)
                    fail_msg = 'Attempt #{0} - Tweet ID: {1}'.format(retries, get_tweet_id)
                    self.popup_tweet(title='POST FAILED!! - Trying again.', msg=fail_msg)
            if sent:
                logger.debug('Sending tweet to tracker db...')
                self.track_tweet(tweet=sent)
                self.popup_tweet(title='Tweet Sent!', msg=message)
        logger.info('The Little Bird has spoken!')
        return sent

    def tweet_analyzer(self):
        data = self.open_ads_db()
        tweets = data['Tweets']
        ordered_tweets = sorted(tweets, key=lambda i: (i['post_count']), reverse=False)[:10]

        for t in ordered_tweets:
            print(t)


