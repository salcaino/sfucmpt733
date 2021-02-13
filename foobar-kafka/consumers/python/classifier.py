from tweet_analytics import *
from kafka import KafkaConsumer, KafkaProducer
import nltk, os, pickle
from sklearn.pipeline import Pipeline
import ast, json
import pandas as pd
from cassandrautils import saveTwitterDf

if __name__ == "__main__":
    print("Starting Twitter data consumer")

    SINK_TOPIC = os.environ.get("SINK_TOPIC_NAME", "twittersink")

    path = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(path)
    cwd = parent + "/nltk_data"
    print("Set NLTK path to {}".format(cwd))
    nltk.data.path = [cwd]
    csvbackupfile = parent + "/data/" + "twitter.csv"

    TOPIC_NAME = os.environ.get("TOPIC_NAME")
    KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL") if os.environ.get("KAFKA_BROKER_URL") else 'localhost:9092'
    print("Reading model file")
    with open(path + '/trainedpipe.pkl', 'rb') as f:
        classifier = pickle.load(f)
    print("Setting up Kafka consumer at {}".format(KAFKA_BROKER_URL))
    consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=[KAFKA_BROKER_URL])
    producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda x: x.encode('utf8'),
            api_version=(0, 10, 1)
        )
    print('Waiting for msg...')
    for msg in consumer:
        # print('got one!')
        msg = msg.value.decode('utf-8')
        data = ast.literal_eval(msg)
        df = pd.DataFrame([data])
                
        target = df.loc[0].tweet.encode('unicode-escape')
        # target = target.encode('ascii', "ignore")
        target = target.decode('ascii', 'ignore')
                
        location = df.loc[0].location
        timestamp = pd.to_datetime(df.loc[0].datetime, unit='s', origin='unix') 
        print("Timestamp: {} Location: {}".format(timestamp, location))
        res = classifier.predict([target])
        classification = "Positive" if res == 1 else "Negative"
        dic = {"tweet" : target, "datetime" : timestamp.strftime('%Y-%m-%d %H:%M:%S'), "location" : location, "classification" : classification}
        df = pd.DataFrame([dic])
        # saveTwitterDf(df,CASSANDRA_HOST, CASSANDRA_KEYSPACE)
        print("Saved to CSV")
        df.to_csv(csvbackupfile, mode='a', header=False, index=False)
        print("Sending it to Cassandra Sink")
        dic = json.dumps(dic)
        producer.send(SINK_TOPIC, value = dic)
        print("Sent")

    print("Bye-Bye")