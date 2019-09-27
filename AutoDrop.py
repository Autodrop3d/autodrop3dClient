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

class pinConfig:
		FilamentSensor1 = 22
		FilamentSensor2 = 37
		Config = 32
		Cancel = 12
		Next = 33
		FilamentLoad1 = 36
		FilamentLoad2 = 11

		EjectorMotor = 16

		LEDred = 7
		LEDyellow = 29
		LEDgreen = 18
		
		LEDstateRed = "off"
		LEDstateYellow = "off"
		LEDstateGreen = "off"
		

		

if ServerTestMode != "on":
		try:
				import RPi.GPIO as GPIO
				import serial
				GPIO.setwarnings(False)
				GPIO.setmode(GPIO.BOARD)

				GPIO.setup(pinConfig.FilamentSensor1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.setup(pinConfig.FilamentSensor2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.setup(pinConfig.Config, GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.setup(pinConfig.Cancel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.setup(pinConfig.Next, GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.setup(pinConfig.FilamentLoad1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
				GPIO.setup(pinConfig.FilamentLoad2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

				GPIO.setup(pinConfig.EjectorMotor, GPIO.OUT)
				GPIO.setup(pinConfig.LEDred, GPIO.OUT)
				GPIO.setup(pinConfig.LEDyellow, GPIO.OUT)
				GPIO.setup(pinConfig.LEDgreen, GPIO.OUT)
				time.sleep(1)

				
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
clientAcessKey = ""
printerPositionOffsetOverideX	= ""
printerPositionOffsetOverideY	= ""
printerPositionOffsetOverideZ	= ""
printerServer = ""
wifiAPname = ""
wifiAPpass = ""

wifiAPmode = False




if (ServerTestMode == "on"):
	printerServer = "https://autodrop1.sparkhosted.site/api/jobsQueue/printerRequestJob"
else:
	printerServer = "https://go.autodrop3d.com/api/jobsQueue/printerRequestJob"
		
		


def printServerBaseURL():
	global printerServer, printerName
	return printerServer



try:
	f = open("settings.txt",'r');
	AutoDropSerialPort = str(f.readline()).strip()
	AutoDropSerialPortSpeed = str(f.readline()).strip()
	printerName = str(f.readline()).strip()
	clientAcessKey = str(f.readline()).strip()
	printerPositionOffsetOverideX	= str(f.readline()).strip()
	printerPositionOffsetOverideY	= str(f.readline()).strip()
	printerPositionOffsetOverideZ	= str(f.readline()).strip()
	f.close()
except:
	print("No configuration file supplied. Configure from web browser")









CuraSlicerPathAndCommand = "CuraEngine -v -c cura.ini -s posx=0 -s posy=0 {options} -o {OutFile}.gcode {inFile}.stl		2>&1";



def takeApicture():
	subprocess.call('fswebcam -S 20 ./static/junk.png', shell=True)
	#subprocess.call('raspistill	-w 200 -h 150 -o ./static/junk.png', shell=True)
	time.sleep(10)
	


@app.route('/image.png')
def liveImageFile():
	takeApicture()
	return app.send_static_file('junk.png')





def image_to_data_url(img_file):
		return "data:image/png;base64," + base64.encodestring(open(img_file,"rb").read()).decode('utf8')



@app.route('/',methods = ['GET', 'POST'])
def index():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, clientAcessKey, printerPositionOffsetOverideX, printerPositionOffsetOverideY, printerPositionOffsetOverideZ

	listOfSerialDevices = ""

#	ports = list(serial.tools.list_ports.comports())
#	for p in ports:
#		print(p[0])
#		listOfSerialDevices = listOfSerialDevices + ", " + p[0]

	listOfSerialDevices = subprocess.check_output('ls /dev/tty*', shell=True).decode("utf-8")



	if request.method == 'POST':

		AutoDropSerialPort = request.form['AutoDropSerialPort']

		AutoDropSerialPortSpeed =	request.form['AutoDropSerialPortSpeed']

		printerName = request.form['printerName']

		clientAcessKey = request.form['clientAcessKey']


		printerPositionOffsetOverideX = request.form['printerPositionOffsetOverideX']
		printerPositionOffsetOverideY = request.form['printerPositionOffsetOverideY']
		printerPositionOffsetOverideZ = request.form['printerPositionOffsetOverideZ']

		PLUGINFUNCTIONS = request.form['PLUGINFUNCTIONS'].replace("\r",'')
		open("custom.py",'w').write(PLUGINFUNCTIONS)


		f = open("settings.txt",'w');
		f.write( AutoDropSerialPort + "\n")
		f.write( AutoDropSerialPortSpeed + "\n")
		#f.write( printerServer + "\n")
		f.write( printerName + "\n")
		f.write( clientAcessKey + "\n")
		f.write( printerPositionOffsetOverideX + "\n")
		f.write( printerPositionOffsetOverideY + "\n")
		f.write( printerPositionOffsetOverideZ + "\n")
		f.close()
		
		wifiAPname = request.form['wifiAPname']
		wifiAPpass = request.form['wifiAPpass']
		if wifiAPname != "":
			print("wifi name was specified")
			subprocess.call('sudo ./setup_wlan_and_AP_modes.sh -s ' + wifiAPname + ' -p ' + wifiAPpass + ' -a autodrop3dConfig -r autodrop3d', shell=True)
			#subprocess.call('sudo ./switchToWlan.sh', shell=True)


	try:
		PLUGINFUNCTIONS = open("custom.py",'r').read()
	except:
		PLUGINFUNCTIONS = ""

	return render_template('index.html', listOfSerialDevices = listOfSerialDevices, AutoDropSerialPort = AutoDropSerialPort , AutoDropSerialPortSpeed = AutoDropSerialPortSpeed, printerName = printerName,	PLUGINFUNCTIONS = PLUGINFUNCTIONS, clientAcessKey = clientAcessKey, printerPositionOffsetOverideX = printerPositionOffsetOverideX, printerPositionOffsetOverideY = printerPositionOffsetOverideY, printerPositionOffsetOverideZ = printerPositionOffsetOverideZ)









@app.route('/slicer',methods = ['GET', 'POST'])
def slicer():
	return render_template('slicer.html')


def flaskThread():
	app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
	_thread.start_new_thread(flaskThread,())



def EjectStuff():
	 print("Ejecting Stuff")
	 GPIO.output(pinConfig.EjectorMotor, 1)
	 time.sleep(30)
	 GPIO.output(pinConfig.EjectorMotor, 0)
	 time.sleep(30)





def offsetGcodeDuringRaft(orgNonManipulatedString = ""):
	global printerPositionOffsetOverideX, printerPositionOffsetOverideY, printerPositionOffsetOverideZ, raftOffsetX, raftOffsetY, raftOffsetZ
	ManipulatedString = ""
	print(orgNonManipulatedString)
	for member in orgNonManipulatedString.split( ):
		print(member[0], member)
		if (member[0] == "X"):
			member = member.replace("X","")
			member = "X" + str(round(float(member) + float(printerPositionOffsetOverideX) + raftOffsetX, 6) )
		if (member[0] == "Y"):
			member = member.replace("Y","")
			member = "Y" + str(round(float(member) + float(printerPositionOffsetOverideY) + raftOffsetY, 6) )
		if (member[0] == "Z"):
			member = member.replace("Z","")
			print(float(member))
			print("Member with z removed", member)
			print("mebers value"+member+"endofmember value")
			member = "Z" + str(round(float(member) + float(printerPositionOffsetOverideZ) + raftOffsetZ, 6) )

		ManipulatedString = ManipulatedString + " " + member + " "

	ManipulatedString = ManipulatedString.strip()
	print("ORG GCODE " + orgNonManipulatedString)
	print("Maniuplated Gcode " +	ManipulatedString)
	return ManipulatedString



def SendGcodeLine(ll = ''):
	#print("Sending :" + ll)
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
			if "echo:busy" in	grbl_out:
				beReadingLines = 1
			if "ok " in grbl_out:
				beReadingLines = 0
	else:
		time.sleep(.001)



def PrintFile(gcodeFileName = 'test.g'):
	global s, cancellCurentPrint, currentPrintModeIsRafting, raftOffsetX, raftOffsetY, raftOffsetZ, currentPrintLineNumber, currentPrintTotalLineNumber, printerServer, printerName, PrintNumber, printerServer, noPicNow, finalPic
	raftOffsetY = 0

	pinConfig.LEDstateGreen = "slow"
	currentPrintTotalLineNumber = sum(1 for line in open(gcodeFileName))

	f = open(gcodeFileName,'r');
	currentPrintLineNumber = 0
	CurrentlyPrintingRightNow = 1
	finalPic = "False"

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
					while GPIO.input(pinConfig.Next) == 1:
						print("Hit button to continue")

				elif str(l.split(b'@',1)[1],"ascii") == "finalPic":
					finalPic = "True"
					takeApicture()
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
	pinConfig.LEDstateGreen = "on"

def urlretrieveWithFail(OptionA = "",OptionB = ""):
	try:
		f = open(OptionB,'w');
		f.write("")
		f.close()
		urlretrieve(OptionA,OptionB)
		pinConfig.LEDstateRed = "off"
	except:
		print("Failed Retrieve File")
		pinConfig.LEDstateRed = "fast"





@app.route('/manualcontroll',methods = ['GET', 'POST'])
def manualcontroll():
	global s, printerPositionOffsetOverideX , printerPositionOffsetOverideY, printerPositionOffsetOverideZ
	s = serial.Serial(AutoDropSerialPort,int(AutoDropSerialPortSpeed))
	piceOfGcodeToSend = request.args['gcode']
	SendGcodeLine(offsetGcodeDuringRaft(piceOfGcodeToSend))
	return piceOfGcodeToSend

def StatusUpdateLoopWhilePrinting():
	global currentPrintLineNumber, currentPrintTotalLineNumber, printerServer, printerName, cancellCurentPrint, clientAcessKey, finalPic
	while 1:
		if currentPrintTotalLineNumber > 10:
			time.sleep(6)

			try:
				if finalPic == "False":
					takeApicture()
					#print("Would have taken picture here")

				else:
					print("final picture taken")

				howFarAlongInThePrintAreWe = str((currentPrintLineNumber / currentPrintTotalLineNumber) * 100)
				
				if (cancellCurentPrint == 1):
				    howFarAlongInThePrintAreWe = "canceled"

				data = { "jobID":PrintNumber, "name":printerName, "key":clientAcessKey, "stat":"update", "jobStatus": howFarAlongInThePrintAreWe , "img":image_to_data_url('./static/junk.png')}
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				print("sending request now to update statius")
				
				#print(requests.post(printerServer , json=data).content)
				
				response = requests.post(printerServer , json=data).content.decode("utf-8")
				
				if response.find("CANCELED") > -1:
					print("Job should be canceled now")
					cancellCurentPrint = 1
				pinConfig.LEDstateRed = "off"
			except:
				print("Update status failed.")
				pinConfig.LEDstateRed = "fast"










def MainPrinterLoop():
	global s, AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, clientAcessKey, PrintNumber, cancellCurentPrint, finalPic
	pinConfig.LEDstateGreen = "on"

	if ServerTestMode != "on":
		s = serial.Serial(AutoDropSerialPort,AutoDropSerialPortSpeed)
		# Wake up grbl
		s.write(('\r\n\r\n').encode("ascii"))
		time.sleep(2)	 # Wait for grbl to initialize
		s.flushInput()	# Flush startup text in serial input
		s.write(('\r\n\r\n').encode("ascii"))

	while 1: #loop for ever
		cancellCurentPrint = 0
		URLtoDownload = printerServer + "?name=" + printerName +	"&key=" + clientAcessKey
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
				URLtoDownload = printerServer + "?name=" + printerName + "&jobID=" + PrintNumber +	"&key=" + clientAcessKey + "&stat=Done"
				#print(URLtoDownload)
				urlretrieveWithFail(URLtoDownload, "download.g")

				URLtoDownload = printerServer + "?name=" + printerName + "&jobID=" + PrintNumber +	"&key=" + clientAcessKey + "&stat=Done"
				#print(URLtoDownload)
				urlretrieveWithFail(URLtoDownload, "download.g")

		time.sleep(10)
		pinConfig.LEDstateGreen = "on"




def LEDblinking():
		global time
		ledCycles = 0
		while 1:
				ledCycles = ledCycles + 1
				
				if (ledCycles == 1):
						fastBlinkONorOFF = 1
						slowBlinkONorOFF = 1
				if (ledCycles == 2):
						fastBlinkONorOFF = 0
						slowBlinkONorOFF = 1
				if (ledCycles == 3):
						fastBlinkONorOFF = 1
						slowBlinkONorOFF = 0
				if (ledCycles == 4):
						fastBlinkONorOFF = 0
						slowBlinkONorOFF = 0
				
				
				
				time.sleep(.25)
				
				
				
				
				
#handle LED on / off
				if (pinConfig.LEDstateRed == "off"):
						GPIO.output(pinConfig.LEDred,1)
				if (pinConfig.LEDstateYellow == "off"):
						GPIO.output(pinConfig.LEDyellow,1)
				if (pinConfig.LEDstateGreen == "off"):
						GPIO.output(pinConfig.LEDgreen,1)

				if (pinConfig.LEDstateRed == "on"):
						GPIO.output(pinConfig.LEDred,0)
				if (pinConfig.LEDstateYellow == "on"):
						GPIO.output(pinConfig.LEDyellow,0)
				if (pinConfig.LEDstateGreen == "on"):
						GPIO.output(pinConfig.LEDgreen,0)



#handle blinking led fast
				if (pinConfig.LEDstateRed == "fast"):
						GPIO.output(pinConfig.LEDred,fastBlinkONorOFF)
				if (pinConfig.LEDstateYellow == "fast"):
						GPIO.output(pinConfig.LEDyellow,fastBlinkONorOFF)
				if (pinConfig.LEDstateGreen == "fast"):
						GPIO.output(pinConfig.LEDgreen,fastBlinkONorOFF)

#handle blinking led slow

				if (pinConfig.LEDstateRed == "slow"):
						GPIO.output(pinConfig.LEDred,slowBlinkONorOFF)
				if (pinConfig.LEDstateYellow == "slow"):
						GPIO.output(pinConfig.LEDyellow,slowBlinkONorOFF)
				if (pinConfig.LEDstateGreen == "slow"):
						GPIO.output(pinConfig.LEDgreen,slowBlinkONorOFF)
				
				if (ledCycles == 4):
						ledCycles = 0
				
				
				


_thread.start_new_thread(LEDblinking,())

pinConfig.LEDstateRed = "fast"
pinConfig.LEDstateGreen = "fast"
pinConfig.LEDstateYellow = "fast"
time.sleep(2)
pinConfig.LEDstateRed = "off"
pinConfig.LEDstateGreen = "off"
pinConfig.LEDstateYellow = "off"



_thread.start_new_thread(MainPrinterLoop,())
_thread.start_new_thread(StatusUpdateLoopWhilePrinting,())






while 1:
	time.sleep(.01)
	if ServerTestMode != "on":
		if GPIO.input(pinConfig.FilamentSensor1) == 0:
			print("FilamentSensor1")
		
		if GPIO.input(pinConfig.FilamentSensor2) == 0:
			print("FilamentSensor2")
		
		if GPIO.input(pinConfig.Next) == 0:
			print("Next")
		
		if GPIO.input(pinConfig.FilamentLoad1) == 0:
			print("FilamentLoad1")
		
		if GPIO.input(pinConfig.FilamentLoad2) == 0:
			print("FilamentLoad2")
			 
		if GPIO.input(pinConfig.Cancel) == 0:
			cancellCurentPrint = 1
			print("cancelling")
			 



				

		if GPIO.input(pinConfig.Config) == 0:
			print("toggling ap/station mode")
			time.sleep(2)
			wifiAPmode = not wifiAPmode
			if wifiAPmode == True:
				subprocess.call('sudo ./switchToAP.sh', shell=True)
				pinConfig.LEDstateYellow = "fast"
			else:
				subprocess.call('sudo ./switchToWlan.sh', shell=True)
				pinConfig.LEDstateYellow = "off"
