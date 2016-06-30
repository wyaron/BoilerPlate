#!/bin/bash

COMMAND=./src/boiler.py
LOGFILE=./log/restart.log

writelog() {
  now=`date`
  echo "$now $*" >> $LOGFILE
}


cd `pwd`

#writelog "Waiting till the network is up..."
#PATH+=/sbin
#adapter=eth0
#internal=""

#until [[ $internal =~ [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} ]]; do
#    sleep 1
#    echo "no ip acquired yet..."
#    internal=$(
#        ifconfig "$adapter" |
#        awk -F'(inet add?r:| +|:)' '/inet add?r/{print $3}'
#    )
#done

# sleep 60 seconds before trying to connect
# if we fail the boiler controller will retry
sleep 10

writelog "Starting boiler application"
while true ; do
  $COMMAND
  writelog "Oops, boiler application has exited with status $?"
  writelog "Restarting boiler application..."
done

