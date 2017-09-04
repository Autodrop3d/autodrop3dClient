#!/bin/bash
# include this boilerplate


sleep 10
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "prusa-start.gcode"
sleep 10
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "download.gcode"
sleep 10
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "prusa-end.gcode"


#report Print Job Completed
wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=Done"
source button-wait-and-go.sh
