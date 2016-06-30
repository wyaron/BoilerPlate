#/bin/bash

killall -KILL boiler_run_forever.sh
killall -KILL boiler.py

echo 'cleaning up some files...'
find . -iname "*.pyc" | xargs -I{} rm -v {}
find . -iname "*~" | xargs -I{} rm -v {}

echo 'removing installation files...'
rm -vfr dist/ boiler.egg-info/ 

echo 'done.'

