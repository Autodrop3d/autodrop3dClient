#!/bin/bash
# include this boilerplate

#These are all the settings for the printer. Change these 

printerServer='http://AUTODROP3D.COM/printerinterface/gcode'
printerName='HARAMBE3D'
printerColor='RED'
printerMaterial='PLA'
SIZEX='150'
SIZEY='150'
SIZEZ='150'


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
rm -f printpage.txt
sed -n '2,10p' download.gcode >> printpage.txt

echo $printerName >> printpage.txt
echo "Printed on $(date)" >> printpage.txt

read -r PrintQueueInstruction<download.gcode

if test "$PrintQueueInstruction" == ";start" ; then
	clear
	figlet Starting Print
	jumpto PrintThePart
fi

echo $PrintQueueInstruction
sleep 10
jumpto TheTop
exit


PrintThePart:
PrintJobID=`sed -n '3p' download.gcode`

#./printcore.py -b 115200 -v '/dev/ttyUSB0' start.gcode
sleep 10
#this is to print the file
#lpr printpage.txt


#CheckPrintStaus:
#figlet Wating For Printer

#PrintStatus="$(lpq -a)"
#if test "$PrintStatus" != "no entries" ; then
#	jumpto CheckPrintStaus
#fi


sleep 10
./printcore.py -b 115200 -v '/dev/ttyUSB0' start.gcode
sleep 25
./printcore.py -b 115200 -v '/dev/ttyUSB0' download.gcode
sleep 10
./printcore.py -b 115200 -v '/dev/ttyUSB0' end.gcode


#report Print Job Completed
wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=Done"
source button-wait-and-go.sh
jumpto TheTop
