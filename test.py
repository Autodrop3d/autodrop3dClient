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




@app.route('/',methods = ['GET', 'POST'])
def index():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, printerMaterial ,SIZEX, SIZEY, SIZEZ 

	if request.method == 'POST':

		AutoDropSerialPort = request.form['AutoDropSerialPort']

		AutoDropSerialPortSpeed =  request.form['AutoDropSerialPortSpeed']

		printerServer =  request.form['printerServer']
		
		printerName = request.form['printerName']

		printerMaterial  = request.form['printerMaterial']
			
		SIZEX = request.form['SIZEX']

		SIZEY = request.form['SIZEY']

		SIZEZ = request.form['SIZEZ']

		STARTGCODE = request.form['STARTGCODE'].replace("\r",'')
		open("start.gcode",'w').write(STARTGCODE)


		ENDGCODE = request.form['ENDGCODE'].replace("\r",'')
		open("end.gcode",'w').write(ENDGCODE)		
			

		PLUGINFUNCTIONS = request.form['PLUGINFUNCTIONS'].replace("\r",'')
		open("custom.py",'w').write(PLUGINFUNCTIONS)	
	
	
			
		
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
		
	
	try:
		PLUGINFUNCTIONS = open("custom.py",'r').read()
	except:
		PLUGINFUNCTIONS = ""
	
	


	return render_template('index.html', AutoDropSerialPort = AutoDropSerialPort , AutoDropSerialPortSpeed = AutoDropSerialPortSpeed, printerServer = printerServer , printerName = printerName, printerMaterial = printerMaterial, SIZEX = SIZEX, SIZEY = SIZEY , SIZEZ = SIZEZ, STARTGCODE = STARTGCODE, ENDGCODE = ENDGCODE, PLUGINFUNCTIONS = PLUGINFUNCTIONS)

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
		
			if str(l).find(";@") != -1: 
				try:
					exec(open("custom.py").read()+ "\n\n" + str(l.split(b'@',1)[1],"ascii"))
				except:
					print("Problem exicuting plugin command " + str(l.split(b'@',1)[1],"ascii"))
			
		else:
			ll = str(l.split(b';',1)[0],"ascii")
			if ll != "":
				print("Sending :" + ll)

	# Close file and serial port
	f.close()

	
#while 1: 
#	time.sleep(10) 
#	print("fake loopping for printer")
	
	
while 1: #loop for ever
	PrintFile("start.gcode")
	time.sleep(10)  
