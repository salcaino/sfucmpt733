#!/bin/bash
set -e

# First arg is `-f` or `--some-option` then prepend default dse command to option(s)
if [ "${1:0:1}" = '-' ]; then
  set -- dse cassandra -f "$@"
fi

# If we're starting Cassandra
if [ "$1" = 'dse' -a "$2" = 'cassandra' ]; then
  # See if we've already completed bootstrapping
  if [ ! -f /var/lib/cassandra/cassandra_bootstrapped ]; then
    echo 'Setting up Cassandra'

    # Invoke the entrypoint script to start Cassandra as a background job and get the pid
    # starting Cassandra in the background the first time allows us to monitor progress and register schema
    echo '=> Starting Cassandra'
    /docker-entrypoint.sh &
    dse_pid="$!"

    # Wait for port 9042 (CQL) to be ready for up to 240 seconds
    echo '=> Waiting for Cassandra to become available'
    ./wait-for-it.sh -t 240 127.0.0.1:9042
    echo '=> Cassandra is available'

    # Create the keyspace if necessary
    echo '=> Ensuring keyspace is created'
    cqlsh -f /opt/scripts/keyspace.cql 127.0.0.1 9042

    # Create the schema if necessary
    echo '=> Ensuring schema is created'
    cqlsh -f /opt/scripts/schema.cql -k kafkapipeline 127.0.0.1 9042

    # Shutdown Cassandra after bootstrapping to allow the entrypoint script to start normally
    echo '=> Shutting down Cassandra after bootstrapping'
    kill -s TERM "$dse_pid"

    # Cassandra will exit with code 143 (128 + 15 SIGTERM) once stopped
    set +e
    wait "$dse_pid"
    if [ $? -ne 143 ]; then
      echo >&2 'Cassandra setup failed'
      exit 1
    fi
    set -e

    # Don't bootstrap next time we start
    touch /var/lib/cassandra/cassandra_bootstrapped
    
    # Now allow Cassandra to start normally below
    echo 'Cassandra has been setup, starting normally'
  fi
fi

# Run the main entrypoint script from the base image
exec /docker-entrypoint.sh
