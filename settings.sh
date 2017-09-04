#!/bin/bash
# include this boilerplate

printerServer='http://AUTODROP3D.COM/printerinterface/gcode'
printerName='drewsucks'
printerMaterial='PLA'
SIZEX='100'
SIZEY='100'
SIZEZ='300'
SERIALPORT='/dev/ttyUSB0'
SERIALSPEED='115200'
PRINTERSTYLE='prusa'






if [ $printerServer == 'NULL' ] ; then
	echo "Your settings indicate you have an auto-ejection system configured."
	echo "If you do, press any key to continue installation."
	echo "If you do not, use Ctrl+C to cancel installation so you can fix your config."
	read -p "Press any key to continue... " -n1 -s
fi

if [ $printerServer == 'NULL' ] ; then
 echo "Please define a printer server."
 exit 1;
fi

if [ $printerName == 'NULL' ] ; then
 echo "Please define a printer name."
 exit 1;
fi

if [ $printerColor == 'NULL' ] ; then
 echo "Please define a material color."
 exit 1;
fi

if [ $printerMaterial == 'NULL' ] ; then
 echo "Please define a material type."
 exit 1;
fi

if [ $SIZEX == 'NULL' ] ; then
 echo "Please define the x-dimension of your print area."
 exit 1;
fi

if [ $SIZEY == 'NULL' ] ; then
 echo "Please define the y-dimension of your print area."
 exit 1;
fi

if [ $SIZEZ == 'NULL' ] ; then
 echo "Please define the z-dimension of your print area."
 exit 1;
fi

if [ $SERIALPORT == 'NULL' ] ; then
 echo "Please define the correct serial port for your printer."
 exit 1;
fi

if [ $SERIALSPEED == 'NULL' ] ; then
 echo "Please define the serial speed of your print controller."
 exit 1;
fi

if [ $LOGGING !== 'TRUE' ] ; then
 echo "No Print Logging is enabled."
fi
