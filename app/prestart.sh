#/usr/bin/env bash
set -e

# check for config file
CONFIG_PATH=/app/utils/config.py
echo "Checking for existance of $CONFIG_PATH"
if [ ! -f $CONFIG_PATH ] ; then
    echo "No configuration file exists, exiting."
    exit 1
fi

# wait for db
echo "Config exists, waiting for database."
sleep 10
