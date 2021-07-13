"""
This is my new reader bot.
"""

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


def get_configuration():
    '''
    Get the configuration for all twitter activities.
    :return: config_file
    '''

    # Get System path and config file
    sys_path = sys.path
    config_file = 'twit_config.cfg'
    try:
        config_path = [f for f in sys_path if os.path.isfile(f + '/' + config_file)][0] + '/' + config_file
        config_path = config_path.replace('\\', '/')
    except IndexError as e:
        raise e

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
    return config


class readerBotTools(object):
    '''
    Tools for manipulating the readerBot
    '''
    def __init__(self):
        super(readerBotTools, self).__init__()
        self.config = get_configuration()
        auth = tweepy.OAuthHandler(self.config['consumer_api_key'], self.config['consumer_secret_key'])
        auth.set_access_token(self.config['api_token'], self.config['api_secret'])
        self.api = tweepy.API(auth)

    def save_tweet(self, text=None, image=None, link=None, last_posted=None):
        previous_tweets = self.get_saved_tweets()
        # print(previous_tweets)

        if not last_posted:
            last_posted = '%s %s' % (datetime.now().date(), datetime.now().time())

        all_tweets = previous_tweets['Tweets']

        sorted_tweets = sorted(all_tweets, key=lambda x: x['id'], reverse=True)
        last_id = sorted_tweets[0]['id']
        next_id = last_id + 1

        new_data = {
            'text': text,
            'id': next_id,
            'image': image,
            'link': link,
            'last_posted': last_posted
        }

        all_tweets.append(new_data)
        # print(all_tweets)
        data = {
            "Tweets": all_tweets
        }
        # print(data)
        tweet_file = open('tweets.json', 'w')
        save_this_data = json.dump(data, tweet_file, indent=4)
        tweet_file.close()
        # print(save_this_data)

    def get_saved_tweets(self):
        fh = open('data/tweets.json', 'r')
        listed_tweets = json.load(fh)
        # print(listed_tweets)
        return listed_tweets

    def get_tweets(self, screen_name=None):
        # timeline = self.api.GetUserTimeline(screen_name=screen_name, count=10)
        timeline = self.api.user_timeline(screen_name=screen_name, count=10)
        earliest_tweet = min(timeline, key=lambda x: x.id).id

        while True:
            tweets = self.api.user_timeline(
                screen_name=screen_name, max_id=earliest_tweet, count=10
            )
            new_earliest = min(tweets, key=lambda x: x.id).id

            if not tweets or new_earliest == earliest_tweet:
                break
            else:
                earliest_tweet = new_earliest
                # print("getting tweets before:", earliest_tweet)
                timeline += tweets
                break

        return timeline

    def collect_random_seed(self):
        text_seed = self.get_tweets(screen_name=self.config['user'])
        collection = ''
        for s in text_seed:
            data = s.AsDict()
            text = data['text']
            for x in text:
                collection += x
        return collection

    def truly_random(self, collection=None):
        rando = 0.0
        if collection:
            final = collection
            a = 0
            b = 0
            c = 0
            d = 0

            random.seed = int(time.time() * math.sin(time.time()))
            A = random.randrange(a, len(final) + 1)
            B = random.randrange(b, len(final) + 1)
            C = random.randrange(c, len(final) + 1)
            D = random.randrange(d, len(final) + 1)
            a = ord(final[A])
            b = ord(final[B])
            c = ord(final[C])
            d = ord(final[D])
            rando = ((a * b) / c) * ((d / 2) * math.sin(4 * time.time()))
        return rando

    def rando_range(self, min=None, max=None, integer=False):
        collection = self.collect_random_seed()
        if not min and not max:
            min = 0.0
            max = 100.0
        elif min and not max:
            max = float(min)
            min = 0.0
        elif max and not min:
            max = float(max)
            min = 0.0
        else:
            max = float(max)
            min = float(min)
        A = self.truly_random(collection)
        B = self.truly_random(collection)
        C = self.truly_random(collection)
        num_list = sorted([A, B, C])
        low = num_list[0]
        hi = num_list[2]
        mid = num_list[1]
        diff = hi - low
        m_diff = mid - low

        range_diff = max - min
        rando = (min + (range_diff * (m_diff / diff)))
        if integer:
            rando = int(rando)
        return rando

    def pick_random_tweet(self):
        tweet_list = self.get_saved_tweets()
        tweets_collection = []
        new_tweet = None
        for tweet in tweet_list['Tweets']:
            date_obj = parser.parse(tweet['last_posted'])
            if date_obj > (datetime.now() - timedelta(days=4)):
                tweets_collection.append(tweet)
        if tweets_collection:
            count = len(tweets_collection)
            rnd = self.rando_range(count, integer=True)
            new_tweet = tweets_collection[rnd]
        return new_tweet

    def twit_search(self, terms=None, result_type='recent', count=20):
        # search = self.api.GetSearch(term=terms, result_type=result_type, count=count)
        search = [status for status in tweepy.Cursor(self.api.search, q=terms).items(count)]
        found = {}
        all_found = []
        for txt in search:
            text = str(txt)
            parse_search = json.loads(text)
            for k in twitter_keys:
                if k in parse_search.keys():
                    tweet = parse_search[k]
                    found[k] = tweet
                    continue
                all_found.append(found)
        return all_found

    def check_twitter_temperature(self):
        """
        Get the latest tweet.
        Is it in the database?
        No:
            Is it a retweet?:
                Yes:
                    With Comment?:
                        Yes:
                            Add to list and get the next tweet
        :return:
        """
        latest_tweets = self.get_tweets(screen_name=self.config['user'])
        tweet_count = 0
        retweet_count = 0
        if latest_tweets:
            for tweet in latest_tweets:
                print(tweet)
                this_tweet = tweet.AsDict()
                if 'retweeted' in this_tweet.keys() and this_tweet['retweeted']:
                    # This is a retweet: treat it as such
                    print('retweet = %s' % this_tweet['retweeted'])
                    retweet_count += 1
                    print('retween count: %s' % retweet_count)
                    # TODO: Cycle through the tweet ids:
                    #       id[0] = 25
                    #       id[1] = 29
                    #       id[2] = 32
                    #       Other conditions not met, start cycling IDs
                    #       id[0] = 34
                    #       id[1] = 37
                    #       All conditions met, print the results:
                    #       [34, 37, 32]
                elif 'retweeted' not in this_tweet.keys() or 'retweeted' in this_tweet.keys() and \
                        not this_tweet['retweeted']:
                    print('retweet = False')
                    tweet_count += 1
                    print('Tweet Count = %s' % tweet_count)

    def find_friends(self, terms=None, result_type='recent', count=20):
        pp = pprint.PrettyPrinter(indent=1)
        if terms:
            with open('data/terms_keywords_hashtags.json') as tkh:
                tkh_data = json.load(tkh)
            negative_phrases = tkh_data['Negative Phrases']
            positive_phrases = tkh_data['Positive Phrases']
            hashtags = tkh_data['Hashtags']

            # search_results = self.api.GetSearch(term=terms, result_type=result_type, count=count)
            search_results = [status for status in tweepy.Cursor(self.api.search, q=terms).items(count)]
            pp.pprint(search_results)
            i = 0
            for result in search_results:
                # print(i)
                # i += 1
                pp.pprint(result)
                # if 'hashtags' in result.keys():
                #     tags = result['hashtags']
                #     for tag in tags:
                #         if tag in hashtags:
                #             pp.pprint('TAG FOUND: %s' % tag)
                for positive in positive_phrases:
                    if positive['positive_phrase'] in result['text']:
                        pp.pprint('Found Friend!')
                for negative in negative_phrases:
                    if negative['negative_phrase'] in result['text']:
                        pp.pprint('RUN!!!!')
                pp.pprint('TEXT: %s' % result['text'])

    def send_simple_tweet(self, message=None, file_name=None):
        if message:
            # Testing sending an image first...
            if file_name:
                post_id = self.api.update_with_media(file_name, message)
            else:
                post_id = self.api.update_status(status=message)
            print('Post_ID: %s' % post_id)


if __name__ == "__main__":
    test = readerBotTools()
    # print(test.rando_range(0, 100, integer=True))
    # print(test.pick_random_tweet())
    # test.check_twitter_temperature()
    # results = test.twit_search(terms='book')
    # print(results)
    # for book in results:
    #     for page in book:
    #         print(page, book[page])
    #     print('-' * 60)
    # test.find_friends(terms='book', count=10)
    test.send_simple_tweet(message='Stranded in the distant past, attempting to preserve an uncertain future.\nThe Roswell Paradox book 1 is an adventure in time that stretches across millions of years. Sometimes the only way forward is back.\n#TheRoswellParadox\n#BackInTime\n#Books https://www.amazon.com/dp/B07R6LJGZ7/ref=cm_sw_r_tw_dp_TGT7DA3R1504FYWYCP6P via @amazon ')
# for x in range(0, 98):
#     print(int(math.fmod(x, 12)))
