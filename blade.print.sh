#!/bin/bash
# include this boilerplate


cat blade.start.gcode download.gcode blade.end.gcode > out.gcode

./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "out.gcode"





#report Print Job Completed
wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=Done"
sleep 5
sudo reboot
