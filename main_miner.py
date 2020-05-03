from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import re
import json

# # # # CREDENTIALS # # # # !
consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

'''
You can get your tokens from
https://www.apps.twitter.com
'''

# # # # TWITTER CLIENT # # # #
class TwitterClient():

    def __init__(self, twitter_user = None):

        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
            friend_list.append(friend)
            return friend_list

    def get_home_timeline(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id = self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# # # # TWITTER AUTHENTICATOR # # # #
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth
 
# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=hash_tag_list)


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True

        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True
          

    def on_error(self, status):
        if status == 420:
            #Returning False in case rate limit occurs
            return False
        print(status)

class TweetAnalyzer():
    '''
    Analyzes Tweets
    '''
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|(\n)", " ", tweet).split())
  
    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
  
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data = [tweet.text for tweet in tweets], columns = ['tweets'])
        
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        
        return df

if __name__ == '__main__':

    screen_name = str(input('Username of the twitter account : '))
    count = int(input('How many tweets do you wish to mine? : '))

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name = screen_name, count = count)
    
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    # print(df)

    # Time Series



    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    

    # print(df.head(count))
    print(df)


    print('Average Sentiment : ', np.mean(df['sentiment']))
    # print(dir(tweets[0]))

    with open('tweets.txt', 'a') as file: #Make sure your file is in the same directory as your project otherwise you have to specify the full path
        
        file.write(str([tweet.id for tweet in tweets]))
        file.write('\n')
        print('Written to File')
    
    confirm = input('Do you wish to see Likes and Retweets graphically? (Y/N) ')

    if confirm == 'Y'.lower():

        print('Loading Graph...')
        time.sleep(1)

        time_likes = pd.Series(data = df['likes'].values, index = df['date'])
        time_likes.plot(figsize = (16,4), label = 'likes', legend = True)

        time_likes = pd.Series(data = df['retweets'].values, index = df['date'])
        time_likes.plot(figsize = (16,4), label = 'retweets', legend = True)

        plt.show()
    
    else:
        print('Closing Miner')
        time.sleep(2)
        quit()

'''
I currently do not know what to do with the saved tweets but
I will work on it in the future. Some possibilities will be
to create a database of them for further analysis.
'''