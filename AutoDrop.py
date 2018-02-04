#! /usr/bin/env python3

import _thread
import serial
import time
#import RPi.GPIO as GPIO
from urllib.request import urlretrieve 
from flask import Flask, render_template, request
app = Flask(__name__)



AutoDropSerialPort = "/dev/ttyS0"
AutoDropSerialPortSpeed = 76800
printerServer = 'http://autodrop3d.com/printerinterface/gcode'
printerName = 'NEW-GCODE-CLIENT'
printerMaterial = 'PLA-YELLOW'
SIZEX = '120'
SIZEY = '120'
SIZEZ = '300'



@app.route('/')
def index():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, printerMaterial ,SIZEX, SIZEY, SIZEZ 

	TEMP = request.args.get('AutoDropSerialPort','')
	if TEMP !="":
		AutoDropSerialPort = TEMP 

		
	TEMP = request.args.get('AutoDropSerialPortSpeed','')
	if TEMP !="":
		AutoDropSerialPortSpeed = TEMP 
		
		
	TEMP = request.args.get('printerServer','')
	if TEMP !="":
		printerServer = TEMP 
		
		
	TEMP = request.args.get('printerName','')
	if TEMP !="":
		printerName = TEMP 
		
		
	TEMP = request.args.get('printerMaterial','')
	if TEMP !="":
		printerMaterial = TEMP 
		
		
	TEMP = request.args.get('SIZEX','')
	if TEMP !="":
		SIZEX = TEMP 
		
	TEMP = request.args.get('SIZEY','')
	if TEMP !="":
		SIZEY = TEMP 
	
	
	TEMP = request.args.get('SIZEZ','')
	if TEMP !="":
		SIZEZ = TEMP 
		

	return render_template('index.html', AutoDropSerialPort = AutoDropSerialPort , AutoDropSerialPortSpeed = AutoDropSerialPortSpeed, printerServer = printerServer , printerName = printerName, printerMaterial = printerMaterial, SIZEX = SIZEX, SIZEY = SIZEY , SIZEZ = SIZEZ )

def flaskThread():
    app.run(host='0.0.0.0', port=8080)
	
if __name__ == "__main__":
	_thread.start_new_thread(flaskThread,())






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
	
	
while 1: 
	time.sleep(10) 
	print("fake loopping for printer")
	
	
while 1: #loop for ever
	URLtoDownload = printerServer + "?name=" + printerName +  "&material=" + printerMaterial + "&SizeX=" + 	SIZEX +"&SizeY=" + SIZEY + "&SizeZ=" + SIZEZ
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
		EjectStuff()
		
		URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
		print(URLtoDownload)
		urlretrieve(URLtoDownload, "download.g")
		
	time.sleep(10)  
