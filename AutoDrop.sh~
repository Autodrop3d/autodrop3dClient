#!/bin/bash
# include this boilerplate

#These are all the settings for the printer. Change these 
date +'Script initialized at %Y-%m-%d-%H%M' >> /home/pi/3d.log
cd /home/pi/Printrun
printerServer='http://autodrop3d.com/printerinterface/gcode'
printerName='i-feel-fantastic'
printerColor='RED'
printerMaterial='PLA-ORANGE'
SIZEX='120'
SIZEY='120'
SIZEZ='300'
SERIALPORT='/dev/ttyS0'
SERIALSPEED='76800'


function jumpto
{
    label=$1
    cmd=$(sed -n "/$label:/{:a;n;p;ba};" $0 | grep -v ':$')
    eval "$cmd"
    exit
}


TheTop:
clear
figlet AutoDrop3d.com
rm -f download.gcode
date +'GCode download started at %Y-%m-%d-%H%M' >> /home/pi/3d.log
wget -O download.gcode "$printerServer?name=$printerName&Color=$printerColor&material=$printerMaterial&SizeX=$SIZEX&SizeY=$SIZEY&SizeZ=$SIZEZ"
rm -f printpage.txt
sed -n '2,10p' download.gcode >> printpage.txt

echo $printerName >> printpage.txt
echo "Printed on $(date)" >> printpage.txt

read -r PrintQueueInstruction<download.gcode

if test "$PrintQueueInstruction" == ";start" ; then
	date +'Started print at %Y-%m-%d-%H%M'  >> /home/pi/3d.log
	clear
	figlet Starting Print
	jumpto PrintThePart
else
	if test "$PrintQueueInstruction" == "No Print Jobs Available" ; then
		sudo reboot
	fi
fi

echo $PrintQueueInstruction
sleep 10
jumpto TheTop
exit


PrintThePart:
PrintJobID=`sed -n '3p' download.gcode`

SERIALPORT='/dev/ttyS0'
SERIALSPEED='76800'


./printcore.py -b $SERIALSPEED -v $SERIALPORT start.gcode

gpio mode 1 out
gpio write 1 1
sleep 30
gpio write 1 0
sleep 30

./printcore.py -b $SERIALSPEED -v $SERIALPORT download.gcode
sleep 10

./printcore.py -b $SERIALSPEED -v $SERIALPORT end.gcode
gpio mode 1 out
gpio write 1 1
sleep 30
gpio write 1 0
sleep 30

#report Print Job Completed
wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=Done"
date +'%Y-%m-%d-%H%M-print_finished' >> /home/pi/3d.log
sleep 5

sudo reboot
#jumpto TheTop
