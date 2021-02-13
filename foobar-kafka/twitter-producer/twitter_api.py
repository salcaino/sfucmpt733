import json
import os
from datetime import datetime
import tweepy
from kafka import KafkaProducer
import configparser

TWIITER_API_GEOBOX_FILTER = [-123.371556, 49.009125, -122.264683, 49.375294]
TWITTER_API_LANGS_FILTER = ['en']

# Twitter API Keys
config = configparser.ConfigParser()
config.read('twitter_service.cfg')
api_credential = config['twitter_api_credential']
access_token = api_credential['access_token']
access_token_secret = api_credential['access_token_secret']
consumer_key = api_credential['consumer_key']
consumer_secret = api_credential['consumer_secret']


# Kafka settings
KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL") if os.environ.get(
    "KAFKA_BROKER_URL") else 'localhost:9092'
TOPIC_NAME = os.environ.get("TOPIC_NAME") if os.environ.get(
    "TOPIC_NAME") else 'from_twitter'

# a static location is used for now as a
# geolocation filter is imposed on twitter API
TWEET_LOCATION = 'MetroVancouver'


class stream_listener(tweepy.StreamListener):

    def __init__(self):
        super(stream_listener, self).__init__()
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda x: json.dumps(x).encode('utf8'),
            api_version=(0, 10, 1)
        )

    def on_status(self, status):
        tweet = status.text
        twitter_df = {
            'tweet': tweet,
            'datetime': datetime.utcnow().timestamp(),
            'location': TWEET_LOCATION
        }
        print(tweet)

        self.producer.send(TOPIC_NAME, value=twitter_df)
        self.producer.flush()
        # print('a tweet sent to kafka')
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False
        print('Streaming Error: ' + str(status_code))


class twitter_stream():

    def __init__(self):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.stream_listener = stream_listener()

    def twitter_listener(self):
        stream = tweepy.Stream(auth=self.auth, listener=self.stream_listener)
        stream.filter(locations=TWIITER_API_GEOBOX_FILTER,
                      languages=TWITTER_API_LANGS_FILTER)


if __name__ == '__main__':
    ts = twitter_stream()
    ts.twitter_listener()
