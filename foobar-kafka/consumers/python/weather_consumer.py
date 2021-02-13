
from kafka import KafkaConsumer
import pandas as pd
import os, json
import ast
from cassandrautils import saveWeatherreport



if __name__ == "__main__":
    print("Starting Weather Consumer")
    TOPIC_NAME = os.environ.get("TOPIC_NAME")
    KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")
    CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "localhost")
    CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE", "kafkapipeline")

    path = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(path) + "/data/"
    csvbackupfile = parent + "weather.csv"

    print("Setting up Kafka consumer at {}".format(KAFKA_BROKER_URL))
    consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=[KAFKA_BROKER_URL])
    
    print('Waiting for msg...')
    for msg in consumer:
        # print('got one!')
        msg = msg.value.decode('ascii')
        jsonData=json.loads(msg)
        df = pd.DataFrame([jsonData])
        print("Saving {} new report".format(df.shape[0]))
        # saveWeatherreport(df,CASSANDRA_HOST, CASSANDRA_KEYSPACE)
        df.to_csv(csvbackupfile, mode='a', header=False, index=False)
        print("Report saved")
        
    print("Bye-Bye")