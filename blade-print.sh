#!/bin/bash
# include this boilerplate


./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "blade-start.gcode"
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "download.gcode"
sleep 10
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "blade-end.gcode"


#report Print Job Completed
wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=Done"
sleep 5
sudo reboot
