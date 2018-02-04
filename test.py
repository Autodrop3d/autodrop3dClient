#! /usr/bin/env python3

import _thread
import serial
import time
from flask import Flask, render_template, request
app = Flask(__name__)



f = open("settings.txt",'r');
AutoDropSerialPort = str(f.readline()).strip()
AutoDropSerialPortSpeed = str(f.readline()).strip()
printerServer = str(f.readline()).strip()
printerName = str(f.readline()).strip()
printerMaterial = str(f.readline()).strip()
SIZEX = str(f.readline()).strip()
SIZEY = str(f.readline()).strip()
SIZEZ = str(f.readline()).strip()
f.close()




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

		
	TEMP = request.args.get('STARTGCODE','')
	if TEMP !="":
		STARTGCODE = TEMP 
		open("start.gcode",'w').write(STARTGCODE)


	TEMP = request.args.get('ENDGCODE','')
	if TEMP !="":
		ENDGCODE = TEMP 
		open("end.gcode",'w').write(ENDGCODE)		
	
		
		
	open("hello.txt","w")
		
	
	f = open("settings.txt",'w');
	f.write( AutoDropSerialPort + "\n")
	f.write( AutoDropSerialPortSpeed + "\n")
	f.write( printerServer + "\n")
	f.write( printerName + "\n")
	f.write( printerMaterial + "\n")
	f.write( SIZEX + "\n")
	f.write( SIZEY + "\n")
	f.write( SIZEZ + "\n")
	f.close()
	
	try:
		STARTGCODE = open("start.gcode",'r').read()
	except:
		STARTGCODE = ""
		
	
	try:
		ENDGCODE = open("end.gcode",'r').read()
	except:
		ENDGCODE = ""
	
	

	return render_template('index.html', AutoDropSerialPort = AutoDropSerialPort , AutoDropSerialPortSpeed = AutoDropSerialPortSpeed, printerServer = printerServer , printerName = printerName, printerMaterial = printerMaterial, SIZEX = SIZEX, SIZEY = SIZEY , SIZEZ = SIZEZ, STARTGCODE = STARTGCODE, ENDGCODE = ENDGCODE)

def flaskThread():
    app.run(host='0.0.0.0', port=8080)
	
if __name__ == "__main__":
	_thread.start_new_thread(flaskThread,())






def EjectStuff():
	print("Ejecting Stuff")
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(12, GPIO.OUT)
	GPIO.output(12, 1)
	time.sleep(30)  
	GPIO.output(12, 0)
	time.sleep(30) 




def PrintFile(gcodeFileName = 'test.g'):

	f = open(gcodeFileName,'r');

	# Stream g-code to grbl
	for line in f:
		l = line.strip() # Strip all EOL characters for consistency
		l = l.encode("ascii")
		l = l.strip();

		if l.startswith(b';') |( l == ''):
			if str(l).find(";EJECT") != -1:
				EjectStuff()
				
			exec(open("custom.py").read()+ "\n\n" + str(l.split(b'@',1)[1],"ascii"))
			
		else:
			ll = str(l.split(b';',1)[0],"ascii")
			if ll != "":
				print("Sending :" + ll)

	# Close file and serial port
	f.close()
	s.close()    
	
	
#while 1: 
#	time.sleep(10) 
#	print("fake loopping for printer")
	
	
while 1: #loop for ever
	PrintFile("start.gcode")
	time.sleep(10)  
