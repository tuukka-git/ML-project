#!/bin/bash

# Ensure the script exits on errors
set -e

LOG_FILE="flask_app.log"
PID_FILE="flask_app.pid"

case $1 in
    start)
        if [ -f $PID_FILE ]; then
            echo "Service is already running with PID $(cat $PID_FILE)."
            exit 1
        fi

        echo "Starting the Flask application in the background..."
        nohup python3 app.py > $LOG_FILE 2>&1 &
        echo $! > $PID_FILE
        echo "Flask application started with PID $(cat $PID_FILE). Logs are in $LOG_FILE"
        ;;

    stop)
        if [ -f $PID_FILE ]; then
            PID=$(cat $PID_FILE)
            echo "Stopping the Flask application with PID $PID..."
            kill $PID
            rm -f $PID_FILE
            echo "Flask application stopped."
        else
            echo "No PID file found. Is the Flask application running?"
            exit 1
        fi
        ;;

    restart)
        $0 stop
        $0 start
        ;;

    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
