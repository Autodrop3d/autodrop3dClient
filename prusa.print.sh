#!/bin/bash
# include this boilerplate

cat prusa.start.gcode download.gcode prusa.end.gcode > out.gcode

./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "out.gcode"



#report Print Job Completed
wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=Done"
source button-wait-and-go.sh
