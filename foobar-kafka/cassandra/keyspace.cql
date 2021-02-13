CREATE KEYSPACE IF NOT EXISTS kafkapipeline 
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };