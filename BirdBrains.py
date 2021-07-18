
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
    if file_name:
        path = None
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
    config['debug_logging'] = True
    return config


class birdBrains(object):
    '''
    The smarts for the Little Bird
    '''
    def __init__(self):
        super(birdBrains, self).__init__()

        # Get Configuration
        self.config = get_configuration()

        # Setup and authorize Twitter connection and api
        auth = tweepy.OAuthHandler(self.config['consumer_api_key'], self.config['consumer_secret_key'])
        auth.set_access_token(self.config['api_token'], self.config['api_secret'])
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
            if ads_db:
                ads = ads_db['Tweets']
            else:
                ads = None
        return ads
