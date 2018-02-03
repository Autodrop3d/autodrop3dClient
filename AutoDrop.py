#!/usr/bin/env python
import serial
import time
import RPi.GPIO as GPIO
from urllib.request import urlretrieve

# Initialize Serial Port
AutoDropSerialPort = "/dev/ttyS0"
AutoDropSerialPortSpeed = 76800

printerServer = 'http://autodrop3d.com/printerinterface/gcode'
printerName = 'NEW-GCODE-CLIENT'
printerColor = 'RED'
printerMaterial = 'PLA-YELLOW'
SIZEX = '120'
SIZEY = '120'
SIZEZ = '300'


def EjectStuff():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(12, GPIO.OUT)
	GPIO.output(12, 1)
	time.sleep(30)  
	GPIO.output(12, 0)
	time.sleep(30) 




def PrintFile(gcodeFileName = 'test.g'):
	s = serial.Serial(AutoDropSerialPort,AutoDropSerialPortSpeed)
	# Wake up grbl
	s.write(('\r\n\r\n').encode("ascii"))
	time.sleep(2)   # Wait for grbl to initialize 
	s.flushInput()  # Flush startup text in serial input
	s.write(('\r\n\r\n').encode("ascii"))


	f = open(gcodeFileName,'r');

	# Stream g-code to grbl
	for line in f:
		l = line.strip() # Strip all EOL characters for consistency
		l = l.encode("ascii")
		l = l.strip();

		if l.startswith(b';') |( l == ''):
			print("Skipping line:" + str(l,"ascii"))
		else:
			ll = str(l.split(b';',1)[0],"ascii")
			if ll != "":
				print("Sending :" + ll)
				s.write(ll.encode("ascii") + b'\n')
				
				beReadingLines = 1
				
				while beReadingLines :
					grbl_out = str(s.readline(),"ascii") # Wait for grbl response with carriage return
					print(' : ' + grbl_out.strip())
					s.flushInput() 
					beReadingLines = 0
					if "T:" in grbl_out:
						beReadingLines = 1

	# Close file and serial port
	f.close()
	s.close()    
	
	

	
while 1: #loop for ever
	URLtoDownload = printerServer + "?name=" + printerName + "&Color=" + printerColor + "&material=" + printerMaterial + "&SizeX=" + 	SIZEX +"&SizeY=" + SIZEY + "&SizeZ=" + SIZEZ
	urlretrieve(URLtoDownload, "download.g")
	print(URLtoDownload)
	f = open("download.g",'r');
	serverMsg = str(f.readline())
	print(str(serverMsg))
	
	if serverMsg.find(";start") == -1:
		print("Np print job for you")
		f.close()
	else:
		bla = str(f.readline()).strip()
		PrintNumber = str(f.readline()).replace(";","").strip()
		
		print("PrintNumber=" + PrintNumber)
		
		f.close()
		EjectStuff()
		PrintFile("download.g")
		
		URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
		print(URLtoDownload)
		urlretrieve(URLtoDownload, "download.g")
		
	time.sleep(10)  