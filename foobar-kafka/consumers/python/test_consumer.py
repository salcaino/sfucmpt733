"""Produce emails by randomly sampling data set and sending to kafka topic."""
import os, json, random
from time import sleep
from kafka import KafkaProducer
import nltk
from nltk.corpus import twitter_samples


path = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(path)
cwd = parent + "/nltk_data"
print("Set NLTK path to {}".format(cwd))
nltk.data.path = [cwd]

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE"))
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 10))


def get_random_tweet_batch(n=BATCH_SIZE):
    # allow user to provide an environment var for this process
    # to control the emails we're sampling. If not provided, sample randomly.
    text = twitter_samples.strings('tweets.20150430-223406.json')
    random.shuffle(text)
    batch = text[0:n]
    print("Returning {} tweets".format(len(batch)))
    return batch


def run():
    print("Setting up Kafka producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode('ascii'),
    )

    while True:
        print("Getting a new batch of tweets")
        batch = get_random_tweet_batch()
        print("Sending new batch of tweets to topic {}".format(TOPIC_NAME))
        producer.send(TOPIC_NAME, value=batch)
        print("Back to sleep...zzzz")
        sleep(SLEEP_TIME)


if __name__ == "__main__":
    run()
