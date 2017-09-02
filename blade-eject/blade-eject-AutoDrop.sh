#!/bin/bash
# include this boilerplate

#These are all the settings for the printer. Change these 
#date +'Script initialized at %Y-%m-%d-%H%M' >> /home/pi/3d.log
cd /home/pi/Printrun
printerServer='http://AUTODROP3D.COM/printerinterface/gcode'
printerName='drewsucks'
printerMaterial='PLA'
SIZEX='100'
SIZEY='100'
SIZEZ='300'
SERIALPORT='/dev/ttyS0'
SERIALSPEED='76800'
PRINTERSTYLE='blade-eject'


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
wget -O download.gcode "$printerServer?name=$printerName&material=$printerMaterial&SizeX=$SIZEX&SizeY=$SIZEY&SizeZ=$SIZEZ"

#Check for the start instruction
read -r PrintQueueInstruction<download.gcode

if test "$PrintQueueInstruction" == ";start" ; then
	clear
	figlet Starting Print
	PrintJobID=`sed -n '3p' download.gcode`
	jumpto PrintThePart
fi

figlet $PrintQueueInstruction
sleep 10
jumpto TheTop
exit


PrintThePart:
cd $PRINTERSTYLE
./print.sh
cd ..
jumpto TheTop
