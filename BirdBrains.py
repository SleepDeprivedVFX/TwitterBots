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

    def update_database(self, key=None, value=None, tid=None):
        if key and tid:
            tid = int(tid)
            logger.info('Updating the Database')
            db = self.open_ads_db()
            logger.debug('Ads DB collected.')
            if not value:
                value = ""
                logger.debug('Value is empty')
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

    def post_tweet(self, tweet=None, collected_tweets=[], retries=0):
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
                    reduced_list = collected_tweets.remove(tweet)
                    db = self.open_ads_db()
                    tweets = db['Tweets']
                    get_tweet_id = self.find_random_tweet(tweet_list=reduced_list)
                    get_tweet = next((twt for twt in tweets if twt['id'] == get_tweet_id), False)
                    logger.info('Sending back through...')
                    logger.debug('Retry tweet: %s' % get_tweet)
                    self.post_tweet(tweet=get_tweet, collected_tweets=tweets, retries=retries)
            if sent:
                logger.debug('Sending tweet to tracker db...')
                self.track_tweet(tweet=sent)
        logger.info('The Little Bird has spoken!')
        return sent



