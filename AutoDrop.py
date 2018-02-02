#!/usr/bin/env python

import serial
import time
import RPi.GPIO as GPIO


# Initialize Serial Port




def EjectStuff():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(12, GPIO.OUT)
	GPIO.output(12, 1)
	time.sleep(30)  
	GPIO.output(12, 0)
	time.sleep(30) 







def PrintFile():
	s = serial.Serial("/dev/ttyS0",76800)
	# Wake up grbl
	s.write("\r\n\r\n")
	time.sleep(2)   # Wait for grbl to initialize 
	s.flushInput()  # Flush startup text in serial input
	s.write("\r\n\r\n")


	f = open('test.g','r');

	# Stream g-code to grbl
	for line in f:
		l = line.strip() # Strip all EOL characters for consistency

		if l.startswith(";") |( l == ""):
			print "Skipping line:"  ,l
		else:
			ll = l.split(';',1)[0]
			print "Sending :" ,ll
			s.write(ll + '\n')
			
			beReadingLines = 1
			
			while beReadingLines :
				grbl_out = s.readline() # Wait for grbl response with carriage return
				print ' : ' + grbl_out.strip()
				s.flushInput() 
				beReadingLines = 0
				if "T:" in grbl_out:
					beReadingLines = 1



	# Wait here until grbl is finished to close serial port and file.



	# Close file and serial port
	f.close()
	s.close()    
	
	
while 1: #loop for ever
	EjectStuff()
	PrintFile()