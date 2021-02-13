FROM cassandra

WORKDIR /opt/scripts

# Copy schema files into /opt/scripts
COPY [ "schema.cql", "keyspace.cql" , "bootstrap.sh", "wait-for-it.sh" , "./" ]
RUN chmod +x /opt/scripts/*
# Set the entrypoint to the bootstrap script
ENTRYPOINT [ "/opt/scripts/bootstrap.sh" ]

# Run DSE in search mode in the foreground by default
CMD [ "dse", "cassandra", "-s", "-g", "-f" ]
