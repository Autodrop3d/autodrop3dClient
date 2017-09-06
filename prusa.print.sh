#!/bin/bash
# include this boilerplate


sleep 10
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "prusa.start.gcode"
sleep 10
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "download.gcode"
sleep 10

#take photo of completed print
fswebcam -r 640x480 --no-banner image.jpg

#end gcode
./Printrun/printcore.py -b $SERIALSPEED -v $SERIALPORT "prusa.end.gcode"

#report Print Job Completed and send photo of completed print to server
new="image.jpg"

curl -s \
"$printerServer" \
-F jobID=${PrintJobID:1} \
-F stat=Done \
-F content=$new \
-F name=image \
-F "filename=$new;image/jpeg;" \
-F "image=@$new" -o download.gcode

source button-wait-and-go.sh
