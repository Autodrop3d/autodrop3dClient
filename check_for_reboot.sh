#!/bin/bash

setup ()
{
  echo Setup
  gpio mode 2 in ;
}
setup
while :
do
        result=`gpio read 2`
        if [ $result -eq 0 ]; then
                mplayer -ao alsa:device=hw=2.0 /home/poohead/shutup.wav 2&>1 > /dev/null
        fi
        sleep 0.1
done
