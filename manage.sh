#!/bin/sh

case "$1" in
  start)
    echo -n "Starting Server: "
    cd /home/ec2-user/hvorvor
    gunicorn --workers 1 --bind localhost:8000 --daemon --access-logfile access.log --error-logfile error.log app:app
    echo "Success"
    ;;
  stop)
    echo -n "Stopping Server: "
    pkill gunicorn
    echo "Success"
    ;;
  restart)
    # Re-run this script with stop and start arguments.
    $0 stop
    sleep 2
    $0 start
    ;;
  deploy)
    # Re-run this script with stop and start arguments.
    $0 stop
    sleep 2
    echo -n "Git pull: "
    git pull
    echo "Success"
    $0 start
    ;;
  reload|force-reload)
    echo "WARNING reload and force-reload not supported by this script"
esac
