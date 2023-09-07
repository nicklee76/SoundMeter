#!/bin/bash

FILENAME="sound_level.py"

pids=($(pgrep -f $FILENAME))

if [ ${#pids[@]} -gt 0 ] ; then
                echo "$FILENAME already running by pid ${pids}"
                exit
fi

echo "Starting $FILENAME"

python3 /home/ubuntu/projects/sound_meter/sound_level.py &
