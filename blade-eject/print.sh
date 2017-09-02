#!/bin/bash
# include this boilerplate


./printcore.py -b $SERIALSPEED -v $SERIALPORT start.gcode
./printcore.py -b $SERIALSPEED -v $SERIALPORT download.gcode
sleep 10
./printcore.py -b $SERIALSPEED -v $SERIALPORT end.gcode


#report Print Job Completed
wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=Done"
sleep 5
sudo reboot
