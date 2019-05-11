#! /usr/bin/env python3
ServerTestMode="off"


import _thread
import time
from urllib.request import urlretrieve

from requests.utils import requote_uri

import urllib.parse

import requests

from flask import Flask, render_template, request
import subprocess
import base64
import json




buttonsStopPin = 16
buttonsRestartPin = 18

if ServerTestMode != "on":
	try:
		import RPi.GPIO as GPIO
		import serial
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(buttonsStopPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(buttonsRestartPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	except:
		print("failed to start ras pi stuff")



app = Flask(__name__)

s = '';


printerPositionOffsetOverideX = 0
printerPositionOffsetOverideY = 0
printerPositionOffsetOverideZ = 40

raftOffsetX = 0
raftOffsetY = 0
raftOffsetZ = 0

CurrentlyPrintingRightNow = 0
currentPrintLineNumber = 0
currentPrintTotalLineNumber = 0
PrintNumber = ""

currentPrintModeIsRafting = 0
cancellCurentPrint = 0

finalPic = "False"


AutoDropSerialPort = ""
AutoDropSerialPortSpeed = ""
printerServer = ""
printerName = ""
SliceOnPrinter = ""
printerPositionOffsetOverideX  = ""
printerPositionOffsetOverideY  = ""
printerPositionOffsetOverideZ  = ""




try:
	f = open("settings.txt",'r');
	AutoDropSerialPort = str(f.readline()).strip()
	AutoDropSerialPortSpeed = str(f.readline()).strip()
	printerServer = str(f.readline()).strip()
	printerName = str(f.readline()).strip()
	SliceOnPrinter = str(f.readline()).strip()
	printerPositionOffsetOverideX  = str(f.readline()).strip()
	printerPositionOffsetOverideY  = str(f.readline()).strip()
	printerPositionOffsetOverideZ  = str(f.readline()).strip()
	f.close()
except:
	print("No configuration file supplied. Configure from web browser")









CuraSlicerPathAndCommand = "CuraEngine -v -c cura.ini -s posx=0 -s posy=0 {options} -o {OutFile}.gcode {inFile}.stl    2>&1";

@app.route('/image.png')
def liveImageFile():
	subprocess.call('raspistill -w 200 -h 150 -o ./static/junk.png', shell=True)
	return app.send_static_file('junk.png')





def image_to_data_url(img_file):
    return "data:image/png;base64," + base64.encodestring(open(img_file,"rb").read()).decode('utf8')



@app.route('/',methods = ['GET', 'POST'])
def index():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, SliceOnPrinter, printerPositionOffsetOverideX, printerPositionOffsetOverideY, printerPositionOffsetOverideZ

	if request.method == 'POST':

		AutoDropSerialPort = request.form['AutoDropSerialPort']

		AutoDropSerialPortSpeed =  request.form['AutoDropSerialPortSpeed']

		printerServer =  request.form['printerServer']

		printerName = request.form['printerName']

		SliceOnPrinter = request.form['SliceOnPrinter']


		printerPositionOffsetOverideX = request.form['printerPositionOffsetOverideX']
		printerPositionOffsetOverideY = request.form['printerPositionOffsetOverideY']
		printerPositionOffsetOverideZ = request.form['printerPositionOffsetOverideZ']

		PLUGINFUNCTIONS = request.form['PLUGINFUNCTIONS'].replace("\r",'')
		open("custom.py",'w').write(PLUGINFUNCTIONS)


		f = open("settings.txt",'w');
		f.write( AutoDropSerialPort + "\n")
		f.write( AutoDropSerialPortSpeed + "\n")
		f.write( printerServer + "\n")
		f.write( printerName + "\n")
		f.write( SliceOnPrinter + "\n")
		f.write( printerPositionOffsetOverideX + "\n")
		f.write( printerPositionOffsetOverideY + "\n")
		f.write( printerPositionOffsetOverideZ + "\n")
		f.close()


	try:
		PLUGINFUNCTIONS = open("custom.py",'r').read()
	except:
		PLUGINFUNCTIONS = ""

	return render_template('index.html', AutoDropSerialPort = AutoDropSerialPort , AutoDropSerialPortSpeed = AutoDropSerialPortSpeed, printerServer = printerServer , printerName = printerName,  PLUGINFUNCTIONS = PLUGINFUNCTIONS, SliceOnPrinter = SliceOnPrinter, printerPositionOffsetOverideX = printerPositionOffsetOverideX, printerPositionOffsetOverideY = printerPositionOffsetOverideY, printerPositionOffsetOverideZ = printerPositionOffsetOverideZ)









@app.route('/slicer',methods = ['GET', 'POST'])
def slicer():
	return render_template('slicer.html')


def flaskThread():
	app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
	_thread.start_new_thread(flaskThread,())



def EjectStuff():
 	print("Ejecting Stuff")

 	GPIO.setup(12, GPIO.OUT)
 	GPIO.output(12, 1)
 	time.sleep(30)
 	GPIO.output(12, 0)
 	time.sleep(30)





def offsetGcodeDuringRaft(orgNonManipulatedString = ""):
	global printerPositionOffsetOverideX, printerPositionOffsetOverideY, printerPositionOffsetOverideZ, raftOffsetX, raftOffsetY, raftOffsetZ
	ManipulatedString = ""
	for member in orgNonManipulatedString.split( ):
		if (member[0] == "X"):
			member = member.replace("X","")
			member = "X" + str(round(float(member) + float(printerPositionOffsetOverideX) + raftOffsetX, 6) )
		if (member[0] == "Y"):
			member = member.replace("Y","")
			member = "Y" + str(round(float(member) + float(printerPositionOffsetOverideY) + raftOffsetY, 6) )
		if (member[0] == "Z"):
			member = member.replace("Z","")
			member = "Z" + str(round(float(member) + float(printerPositionOffsetOverideZ) + raftOffsetZ, 6) )

		ManipulatedString = ManipulatedString + " " + member + " "

	ManipulatedString = ManipulatedString.strip()
	print("ORG GCODE " + orgNonManipulatedString)
	print("Maniuplated Gcode " +  ManipulatedString)
	return ManipulatedString



def SendGcodeLine(ll = ''):
	print("Sending :" + ll)
	if ServerTestMode != "on":
		s.flushInput()
		s.write(ll.encode("ascii") + b'\n')

		beReadingLines = 1

		while beReadingLines:
			print("Sent : " + ll + " | waiting for response")
			grbl_out = str(s.readline(),"ascii") # Wait for grbl response with carriage return
			#print("got that line back")
			print('response : ' + grbl_out.strip())
			s.flushInput()
			beReadingLines = 0
			if "T:" in grbl_out:
				beReadingLines = 1
			if "echo:busy" in  grbl_out:
				beReadingLines = 1
			if "ok " in grbl_out:
				beReadingLines = 0
	else:
		time.sleep(.01)

def PrintFile(gcodeFileName = 'test.g'):
	global s, cancellCurentPrint, currentPrintModeIsRafting, raftOffsetX, raftOffsetY, raftOffsetZ, currentPrintLineNumber, currentPrintTotalLineNumber, printerServer, printerName, PrintNumber, printerServer, noPicNow
	raftOffsetY = 0


	currentPrintTotalLineNumber = sum(1 for line in open(gcodeFileName))

	f = open(gcodeFileName,'r');
	currentPrintLineNumber = 0
	CurrentlyPrintingRightNow = 1

	# Stream g-code to grbl
	for line in f:
		if cancellCurentPrint == 1:
			break
		currentPrintLineNumber += 1
		l = line.strip() # Strip all EOL characters for consistency
		l = l.encode("ascii")
		l = l.strip();

		if l.startswith(b';') |( l == ''):
			print("This is a comment line :*" +str( l) + "*")

			if l.startswith(b';LAYER:-2'):
				currentPrintModeIsRafting = currentPrintModeIsRafting + 1
				raftOffsetY = raftOffsetY - .5
			if l.startswith(b';LAYER:0'):
				currentPrintModeIsRafting = 0
			if str(l).find(";@") != -1:
				if str(l.split(b'@',1)[1],"ascii") == "eject":
					EjectStuff()
				elif str(l.split(b'@',1)[1],"ascii") == "notifycomplete":
					URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
					print(URLtoDownload)
					urlretrieveWithFail(URLtoDownload, "notifyComplete.txt")
					URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
					print(URLtoDownload)
					urlretrieveWithFail(URLtoDownload, "notifyComplete.txt")
					while GPIO.input(buttonsRestartPin) == 1:
						print("Hit button to continue")

				elif str(l.split(b'@',1)[1],"ascii") == "finalPic":
					finalPic = "True"



				else:
					try:
						exec(open("custom.py").read()+ "\n\n" + str(l.split(b'@',1)[1],"ascii"))
					except:
						print("Problem executing plug in command " + str(l.split(b'@',1)[1],"ascii"))

		else:
			ll = str(l.split(b';',1)[0],"ascii")
			ll = offsetGcodeDuringRaft(ll)
			if ll != "":
				SendGcodeLine(ll)



	# Close file and serial port
	f.close()
	CurrentlyPrintingRightNow = 0

def urlretrieveWithFail(OptionA = "",OptionB = ""):
	try:
		f = open(OptionB,'w');
		f.write("")
		f.close()
		urlretrieve(OptionA,OptionB)
	except:
		print("Failed Retrieve File")





@app.route('/manualcontroll',methods = ['GET', 'POST'])
def manualcontroll():
	global s, printerPositionOffsetOverideX , printerPositionOffsetOverideY, printerPositionOffsetOverideZ
	s = serial.Serial(AutoDropSerialPort,AutoDropSerialPortSpeed)
	piceOfGcodeToSend = request.args['gcode']
	SendGcodeLine(offsetGcodeDuringRaft(piceOfGcodeToSend))
	return piceOfGcodeToSend

def StatusUpdateLoopWhilePrinting():
	global currentPrintLineNumber, currentPrintTotalLineNumber, printerServer, printerName, cancellCurentPrint
	while 1:
		if currentPrintTotalLineNumber > 10:
			time.sleep(6)

			try:
				if finalPic == "False":
					subprocess.call('raspistill  -w 200 -h 150 -o ./static/junk.png', shell=True)
					time.sleep(10)

				howFarAlongInThePrintAreWe = (currentPrintLineNumber / currentPrintTotalLineNumber) * 100

				data = { "jobID":PrintNumber, "stat":"update", "jobStatus":str(howFarAlongInThePrintAreWe), "img":image_to_data_url('./static/junk.png')}
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


				response = requests.post(printerServer , json=data,)




				print(response)

				serverMsg = response

				print(str(serverMsg))
				if serverMsg.find("CANCELED") > -1:
					print("Job should be canceled now")
					cancellCurentPrint = 1

			except:
				print("Update status failed.")










def MainPrinterLoop():
	global s, AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, SliceOnPrinter, PrintNumber, cancellCurentPrint, finalPic

	if ServerTestMode != "on":
		s = serial.Serial(AutoDropSerialPort,AutoDropSerialPortSpeed)
		# Wake up grbl
		s.write(('\r\n\r\n').encode("ascii"))
		time.sleep(2)   # Wait for grbl to initialize
		s.flushInput()  # Flush startup text in serial input
		s.write(('\r\n\r\n').encode("ascii"))

	while 1: #loop for ever
		cancellCurentPrint = 0
		URLtoDownload = printerServer + "?name=" + printerName +  "&NoGcode=" + SliceOnPrinter
		urlretrieveWithFail(URLtoDownload, "download.g")
		print(URLtoDownload)
		f = open("download.g",'r');
		serverMsg = str(f.readline())
		print(str(serverMsg))

		if serverMsg.find(";START") == -1:
			print("Np print job for you")
			f.close()
		else:
			bla = str(f.readline()).strip()
			PrintNumber = str(f.readline()).replace(";","").strip()


			print("PrintNumber=" + PrintNumber)
			finalPic = "False"

			f.close()

			#PrintFile("start.gcode")
			PrintFile("download.g")
			#PrintFile("end.gcode")

			if cancellCurentPrint == 0:
				URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
				print(URLtoDownload)
				urlretrieveWithFail(URLtoDownload, "download.g")

				URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
				print(URLtoDownload)
				urlretrieveWithFail(URLtoDownload, "download.g")

		time.sleep(10)


_thread.start_new_thread(MainPrinterLoop,())
_thread.start_new_thread(StatusUpdateLoopWhilePrinting,())
while 1:
	time.sleep(.01)
	#print(GPIO.input(buttonsStopPin))
	if ServerTestMode != "on":
		if GPIO.input(buttonsStopPin) == 0:
			cancellCurentPrint = 1
			print("cancelling")
