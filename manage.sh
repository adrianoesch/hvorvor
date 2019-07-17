#!/bin/sh

case "$1" in
  start)
    echo -n "Starting Server: "
    cd /home/ec2-user/hvorvor
    gunicorn --workers 2 --bind localhost:5000 --daemon --log-file gunicorn.log wsgi:app
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
