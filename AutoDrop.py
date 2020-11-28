#! /usr/bin/env python3
ServerTestMode="off"

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

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
	
	
class currentMachineState:
	pausePrint = 0
	specialAction = ""
	currentExtruderTemp = 0
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
	disableAllOffsets = "false"
	wifiAPmode = False





# Importing socket library
import os
import socket
  
# Function to display hostname and
# IP address
def get_Host_name_IP():
	host_ip = ""
	try:
		getMeSomeIPinfo = os.popen("ip -4 route show default").read().split()
		soThing = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		soThing.connect((getMeSomeIPinfo[2], 0))
		host_ip = soThing.getsockname()[0]
		print(host_ip)

	except:
		print("unable to get IP")
		
	return host_ip
print("Machine IP address is: " + get_Host_name_IP())



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
		GPIO.output(pinConfig.EjectorMotor, 0)
		GPIO.setup(pinConfig.LEDred, GPIO.OUT)
		GPIO.setup(pinConfig.LEDyellow, GPIO.OUT)
		GPIO.setup(pinConfig.LEDgreen, GPIO.OUT)
		time.sleep(1)

			
	except:
		print("failed to start ras pi stuff")



app = Flask(__name__)






if (ServerTestMode == "on"):
	currentMachineState.printerServer = "https://autodrop1.sparkhosted.site/api/jobsQueue/printerRequestJob"
else:
	currentMachineState.printerServer = "http://go.autodrop3d.com/api/jobsQueue/printerRequestJob"
		
		


def printServerBaseURL():
	return currentMachineState.printerServer



try:
	f = open("../settings.txt",'r');
	currentMachineState.AutoDropSerialPort                  = str(f.readline()).strip()
	currentMachineState.AutoDropSerialPortSpeed             = str(f.readline()).strip()
	currentMachineState.printerName                         = str(f.readline()).strip()
	currentMachineState.clientAcessKey                      = str(f.readline()).strip()
	currentMachineState.printerPositionOffsetOverideX	= str(f.readline()).strip()
	currentMachineState.printerPositionOffsetOverideY	= str(f.readline()).strip()
	currentMachineState.printerPositionOffsetOverideZ	= str(f.readline()).strip()
	currentMachineState.disableAllOffsets                   = str(f.readline()).strip()
	f.close()
except:
	print("No configuration file supplied. Configure from web browser")









CuraSlicerPathAndCommand = "CuraEngine -v -c cura.ini -s posx=0 -s posy=0 {options} -o {OutFile}.gcode {inFile}.stl		2>&1";



def takeApicture():
	subprocess.call('fswebcam --fps 1 --no-banner -q -S 8 ./static/junk.png >> /dev/null', shell=True)
	#subprocess.call('raspistill	-w 200 -h 150 -o ./static/junk.png', shell=True)
	time.sleep(1)
	


@app.route('/image.png')
def liveImageFile():
	takeApicture()
	return app.send_static_file('junk.png')





def image_to_data_url(img_file):
		return "data:image/png;base64," + base64.encodestring(open(img_file,"rb").read()).decode('utf8')



@app.route('/',methods = ['GET', 'POST'])
def index():

	listOfSerialDevices = ""

	listOfSerialDevices = subprocess.check_output('ls /dev/tty*', shell=True).decode("utf-8")



	if request.method == 'POST':

		currentMachineState.AutoDropSerialPort = request.form['AutoDropSerialPort']

		currentMachineState.AutoDropSerialPortSpeed =	request.form['AutoDropSerialPortSpeed']

		currentMachineState.printerName = request.form['printerName']

		currentMachineState.clientAcessKey = request.form['clientAcessKey']
		
		currentMachineState.disableAllOffsets = request.form['disableAllOffsets']

		currentMachineState.printerPositionOffsetOverideX = request.form['printerPositionOffsetOverideX']
		currentMachineState.printerPositionOffsetOverideY = request.form['printerPositionOffsetOverideY']
		currentMachineState.printerPositionOffsetOverideZ = request.form['printerPositionOffsetOverideZ']

		PLUGINFUNCTIONS = request.form['PLUGINFUNCTIONS'].replace("\r",'')
		open("../custom.py",'w').write(PLUGINFUNCTIONS)


		f = open("../settings.txt",'w');
		f.write( currentMachineState.AutoDropSerialPort + "\n")
		f.write( currentMachineState.AutoDropSerialPortSpeed + "\n")
		#f.write( currentMachineState.printerServer + "\n")
		f.write( currentMachineState.printerName + "\n")
		f.write( currentMachineState.clientAcessKey + "\n")
		f.write( currentMachineState.printerPositionOffsetOverideX + "\n")
		f.write( currentMachineState.printerPositionOffsetOverideY + "\n")
		f.write( currentMachineState.printerPositionOffsetOverideZ + "\n")
		f.write( currentMachineState.disableAllOffsets + "\n")
		f.write( "\n")
		f.write( "\n")
		f.write( "\n")
		f.write( "\n")
		f.write( "\n")

		f.close()
		
		currentMachineState.wifiAPname = request.form['wifiAPname']
		currentMachineState.wifiAPpass = request.form['wifiAPpass']
		if currentMachineState.wifiAPname != "":
			print("wifi name was specified")
			subprocess.call('sudo ./setup_wlan_and_AP_modes.sh -s ' + currentMachineState.wifiAPname + ' -p ' + currentMachineState.wifiAPpass + ' -a autodrop3dConfig -r autodrop3d', shell=True)
			#subprocess.call('sudo ./switchToWlan.sh', shell=True)


	try:
		PLUGINFUNCTIONS = open("../custom.py",'r').read()
	except:
		PLUGINFUNCTIONS = ""

	return render_template('index.html', listOfSerialDevices = listOfSerialDevices, AutoDropSerialPort = currentMachineState.AutoDropSerialPort , AutoDropSerialPortSpeed = currentMachineState.AutoDropSerialPortSpeed, printerName = currentMachineState.printerName,	PLUGINFUNCTIONS = PLUGINFUNCTIONS, clientAcessKey = currentMachineState.clientAcessKey, printerPositionOffsetOverideX = currentMachineState.printerPositionOffsetOverideX, printerPositionOffsetOverideY = currentMachineState.printerPositionOffsetOverideY, printerPositionOffsetOverideZ = currentMachineState.printerPositionOffsetOverideZ, disableAllOffsets = currentMachineState.disableAllOffsets)









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
	if currentMachineState.disableAllOffsets == "TRUE":
		return orgNonManipulatedString


	ManipulatedString = ""
	print("this is the original un manipulated string")
	print(orgNonManipulatedString)
	for member in orgNonManipulatedString.split( ):
		#print(member[0], member)
		if (member[0] == "X"):
			member = member.replace("X","")
			member = "X" + str(round(float(member) + float(currentMachineState.printerPositionOffsetOverideX) + currentMachineState.raftOffsetX, 6) )
		if (member[0] == "Y"):
			member = member.replace("Y","")
			member = "Y" + str(round(float(member) + float(currentMachineState.printerPositionOffsetOverideY) + currentMachineState.raftOffsetY, 6) )
		if (member[0] == "Z"):
			member = member.replace("Z","")
			member = "Z" + str(round(float(member) + float(currentMachineState.printerPositionOffsetOverideZ) + currentMachineState.raftOffsetZ, 6) )

		ManipulatedString = ManipulatedString + " " + member + " "

	ManipulatedString = ManipulatedString.strip()
	#print("ORG GCODE " + orgNonManipulatedString +"end of original gcode")
	#print("Maniuplated Gcode " +	ManipulatedString)
	return ManipulatedString



def SendGcodeLine(ll = '', returnJustPrinterResponse = 0):
	if ServerTestMode != "on":
		currentMachineState.s.flushInput()
		currentMachineState.s.write(ll.encode("ascii") + b'\n')
		print("Sent " +str( currentMachineState.currentPrintLineNumber)  + " : " + ll + " | waiting for response")

		beReadingLines = 1
		millis = int(round(time.time() * 1000))
		print("this is the start time")
		print(millis)

		while beReadingLines:
			grbl_out = ""

			thatEndOfLineIsHere = False
			while True:
				theCurrentSerialBuffer = currentMachineState.s.read()
				#print("this is the serial buffer")
				#print(theCurrentSerialBuffer)
				for c in theCurrentSerialBuffer:
					grbl_out = grbl_out + str(chr(c))
					if (chr(c) == '\n'):
						#print("We got an end of line character:")
						thatEndOfLineIsHere = True
						break
					if (chr(c) == '\r'):
						#print("We got an end of line character:")
						thatEndOfLineIsHere = True
						break
					if currentMachineState.cancellCurentPrint == 1:
						break
				if (thatEndOfLineIsHere == True):
					break
				if currentMachineState.cancellCurentPrint == 1:
					break
				if millis + 10000 < int(round(time.time() * 1000)):
					currentMachineState.s.write(("M114").encode("ascii") + b'\n')
					print("Some thing must have stalled the gcode send" )
					print(millis)
					print(int(round(time.time() * 1000)))
					break
			
			#print("got that line back")
			print('response : ' + grbl_out.strip())
			#currentMachineState.s.flushInput()
			beReadingLines = 0
			if "T:" in grbl_out:
				beReadingLines = 1
				millis = int(round(time.time() * 1000))
			if "echo:busy" in	grbl_out:
				beReadingLines = 1
				millis = int(round(time.time() * 1000))
			if "ok" in grbl_out:
				beReadingLines = 0
			if currentMachineState.cancellCurentPrint == 1:
				break
	else:
		time.sleep(.002)
	if (returnJustPrinterResponse):
		return "    Sent : " + ll + "   Result: " + grbl_out
	else:
		return grbl_out



def handleFilamentChange(areWePrinting = ""):
	if (currentMachineState.specialAction == "ejectFillament1"):
		currentMachineState.currentExtruderTemp = float(SendGcodeLine("M105", True).split("/")[1].split(" ")[0])
		if currentMachineState.currentExtruderTemp == 0:
			currentMachineState.currentExtruderTemp = 200
			SendGcodeLine("M109 T0 S" + str(currentMachineState.currentExtruderTemp - 5)  + " B" + str(currentMachineState.currentExtruderTemp + 5)  , True)
		if areWePrinting == "not printing":
			SendGcodeLine("G28", True)
			SendGcodeLine("G1 Z100", True)
		SendGcodeLine("G91", True)
		if areWePrinting != "not printing":
			SendGcodeLine("G0 Z20", True)
		SendGcodeLine("G0 E-100", True)
		SendGcodeLine("G0 E-100", True)
		SendGcodeLine("G0 E-100", True)
		SendGcodeLine("G0 E-100", True)
		SendGcodeLine("G0 E-100", True)
		SendGcodeLine("G0 E-100", True)
		SendGcodeLine("M104 S0", True)
		#print(" ------------------------------------  " + str( currentMachineState.currentExtruderTemp))
	if (currentMachineState.specialAction == "loadFillament1"):
		if currentMachineState.currentExtruderTemp == 0:
			currentMachineState.currentExtruderTemp = 200
		if areWePrinting == "not printing":
			SendGcodeLine("G28", True)
			SendGcodeLine("G1 Z100", True)
		SendGcodeLine("M109 T0 S" + str(currentMachineState.currentExtruderTemp - 5)  + " B" + str(currentMachineState.currentExtruderTemp + 5)  , True)
		SendGcodeLine("G0 E100", True)
		SendGcodeLine("G0 E100", True)
		SendGcodeLine("G0 E100", True)
		SendGcodeLine("G0 E100", True)
		SendGcodeLine("G0 E100", True)
		SendGcodeLine("G0 E100", True)
		if areWePrinting != "not printing":
			SendGcodeLine("G1 Z-20", True)
		SendGcodeLine("G90", True)
		currentMachineState.pausePrint = False
	currentMachineState.specialAction = ""






def PrintFile(gcodeFileName = 'test.g'):
	currentMachineState.raftOffsetY = 0

	pinConfig.LEDstateGreen = "slow"
	currentMachineState.currentPrintTotalLineNumber = sum(1 for line in open(gcodeFileName))

	f = open(gcodeFileName,'r');
	currentMachineState.currentPrintLineNumber = 0
	currentMachineState.CurrentlyPrintingRightNow = 1
	currentMachineState.finalPic = "False"

	# Stream g-code to grbl
	for line in f:
		if currentMachineState.cancellCurentPrint == 1:
			break
		currentMachineState.currentPrintLineNumber += 1
		l = line.strip() # Strip all EOL characters for consistency
		l = l.encode("ascii")
		l = l.strip();
		
		
		while currentMachineState.pausePrint:
			handleFilamentChange()
			time.sleep(1)
		
		
		if (l != ""):
			if l.startswith(b';') |( l == ''):
				print("comment line :*" + l.decode("utf-8"))
	
				if l.startswith(b';LAYER:-2'):
					currentMachineState.currentPrintModeIsRafting = currentMachineState.currentPrintModeIsRafting + 1
					currentMachineState.raftOffsetY = currentMachineState.raftOffsetY - .5
				if l.startswith(b';LAYER:0'):
					currentMachineState.currentPrintModeIsRafting = 0
				if str(l).find(";@") != -1:
					if str(l.split(b'@',1)[1],"ascii") == "eject":
						EjectStuff()
					elif str(l.split(b'@',1)[1],"ascii") == "notifycomplete":
						URLtoDownload = currentMachineState.printerServer + "?jobID=" + currentMachineState.PrintNumber + "&stat=Done" + "&ip=" + get_Host_name_IP()
						urlretrieveWithFail(URLtoDownload, "notifyComplete.txt")
						urlretrieveWithFail(URLtoDownload, "notifyComplete.txt")
						while GPIO.input(pinConfig.Next) == 1:
							print("Hit button to continue")
	
					elif str(l.split(b'@',1)[1],"ascii") == "finalPic":
						currentMachineState.finalPic = "True"
						takeApicture()
					elif str(l.split(b'@',1)[1],"ascii") == "finalPic":
						currentMachineState.finalPic = "True"
						takeApicture()
					elif str(l.split(b'@',1)[1],"ascii") == "finalPic":
						currentMachineState.finalPic = "True"
						takeApicture()
					else:
						try:
							exec(open("../custom.py").read()+ "\n\n" + str(l.split(b'@',1)[1],"ascii"))
						except:
							print("Problem executing plug in command " + str(l.split(b'@',1)[1],"ascii"))
	
			else:
				ll = str(l.split(b';',1)[0],"ascii")
				

				if ll.startswith("G28"):
					print("not goint to manipulate G28 gcode lines")
				else:
					ll = offsetGcodeDuringRaft(ll)
				if ll != "":
					SendGcodeLine(ll)



	# Close file and serial port
	f.close()
	currentMachineState.CurrentlyPrintingRightNow = 0
	pinConfig.LEDstateGreen = "on"

def urlretrieveWithFail(OptionA = "",OptionB = ""):
	print(OptionA)
	try:
		f = open(OptionB,'w');
		f.write("")
		f.close()
		urlretrieve(OptionA,OptionB)
		pinConfig.LEDstateRed = "off"
	except:
		print("Failed Retrieve File")
		pinConfig.LEDstateRed = "fast"





@app.route('/manualcontrol',methods = ['GET', 'POST'])
def manualcontrol():
	currentMachineState.s = serial.Serial(currentMachineState.AutoDropSerialPort,int(currentMachineState.AutoDropSerialPortSpeed))
	piceOfGcodeToSend = request.args['gcode']
	manualGcodeSendResponse = SendGcodeLine(offsetGcodeDuringRaft(piceOfGcodeToSend))
	print("Manual send response should be " + manualGcodeSendResponse)
	return manualGcodeSendResponse

def StatusUpdateLoopWhilePrinting():
	while 1:
		if currentMachineState.currentPrintTotalLineNumber > 10:
			time.sleep(6)

			try:
				if currentMachineState.finalPic == "False":
					takeApicture()
				else:
					print("final picture taken")

				howFarAlongInThePrintAreWe = str((currentMachineState.currentPrintLineNumber / currentMachineState.currentPrintTotalLineNumber) * 100)
				
				if (currentMachineState.cancellCurentPrint == 1):
				    howFarAlongInThePrintAreWe = "canceled"

				data = { "jobID":currentMachineState.PrintNumber, "name":currentMachineState.printerName, "key":currentMachineState.clientAcessKey, "stat":"update", "jobStatus": howFarAlongInThePrintAreWe , "img":image_to_data_url('./static/junk.png'), "ip": get_Host_name_IP()}
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				
				response = requests.post(currentMachineState.printerServer , json=data).content.decode("utf-8")
				
				if response.find("CANCELED") > -1:
					print("Job should be canceled now")
					currentMachineState.cancellCurentPrint = 1
				pinConfig.LEDstateRed = "off"
			except:
				print("Update status failed.")
				pinConfig.LEDstateRed = "fast"










def MainPrinterLoop():
	pinConfig.LEDstateGreen = "on"

	if ServerTestMode != "on":
		currentMachineState.s = serial.Serial(currentMachineState.AutoDropSerialPort,currentMachineState.AutoDropSerialPortSpeed)
		# Wake up grbl
		currentMachineState.s.write(('\r\n\r\n').encode("ascii"))
		time.sleep(2)	 # Wait for grbl to initialize
		currentMachineState.s.flushInput()	# Flush startup text in serial input
		currentMachineState.s.write(('\r\n\r\n').encode("ascii"))

	while 1: #loop for ever
		if currentMachineState.cancellCurentPrint == 1:
			SendGcodeLine("G28", True)
			
		currentMachineState.cancellCurentPrint = 0
		handleFilamentChange("not printing")
		currentMachineState.pausePrint = False
		URLtoDownload = currentMachineState.printerServer + "?name=" + currentMachineState.printerName +	"&key=" + currentMachineState.clientAcessKey + "&ip=" + get_Host_name_IP()
		urlretrieveWithFail(URLtoDownload, "download.g")
		f = open("download.g",'r');
		serverMsg = str(f.readline())
		print(str(serverMsg))

		if serverMsg.find(";START") == -1:
			print("No print job for you")
			f.close()
		else:
			bla = str(f.readline()).strip()
			currentMachineState.PrintNumber = str(f.readline()).replace(";","").strip()


			print("currentMachineState.PrintNumber=" + currentMachineState.PrintNumber)
			currentMachineState.finalPic = "False"

			f.close()


			PrintFile("download.g")


			if currentMachineState.cancellCurentPrint == 0:
				URLtoDownload = currentMachineState.printerServer + "?name=" + currentMachineState.printerName + "&jobID=" + currentMachineState.PrintNumber +	"&key=" + currentMachineState.clientAcessKey + "&stat=Done" + "&ip=" + get_Host_name_IP()
				urlretrieveWithFail(URLtoDownload, "download.g")

				URLtoDownload = currentMachineState.printerServer + "?name=" + currentMachineState.printerName + "&jobID=" + currentMachineState.PrintNumber +	"&key=" + currentMachineState.clientAcessKey + "&stat=Done" + "&ip=" + get_Host_name_IP()
				urlretrieveWithFail(URLtoDownload, "download.g")

		time.sleep(10)
		pinConfig.LEDstateGreen = "on"




def LEDblinking():
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
			print("FilamentSensor1 Triggered")
			if currentMachineState.pausePrint == False:
				time.sleep(1)
				currentMachineState.pausePrint = True
				currentMachineState.specialAction = "ejectFillament1"
				time.sleep(1)

		if GPIO.input(pinConfig.FilamentLoad1) == 0:
			print("FilamentLoad1")
			time.sleep(1)
			if GPIO.input(pinConfig.FilamentLoad1) == 0:
				if currentMachineState.pausePrint == False:
					time.sleep(1)
					currentMachineState.pausePrint = True
					currentMachineState.specialAction = "ejectFillament1"
					time.sleep(1)
			else:
				currentMachineState.specialAction = "loadFillament1"


		if GPIO.input(pinConfig.FilamentSensor2) == 0:
			print("FilamentSensor2 Triggered")
			if currentMachineState.pausePrint == False:
				time.sleep(1)
				currentMachineState.pausePrint = True
				currentMachineState.specialAction = "ejectFillament2"
				time.sleep(1)

		if GPIO.input(pinConfig.FilamentLoad2) == 0:
			print("FilamentLoad2")
			time.sleep(1)
			if GPIO.input(pinConfig.FilamentLoad2) == 0:
				if currentMachineState.pausePrint == False:
					time.sleep(1)
					currentMachineState.pausePrint = True
					currentMachineState.specialAction = "ejectFillament2"
					time.sleep(1)
			else:
				currentMachineState.specialAction = "loadFillament2"







		
		if GPIO.input(pinConfig.Next) == 0:
			print("Next")
			 
		if GPIO.input(pinConfig.Cancel) == 0:
			currentMachineState.cancellCurentPrint = 1
			print("cancelling")

		if GPIO.input(pinConfig.Config) == 0:
			print("toggling ap/station mode")
			time.sleep(2)
			if GPIO.input(pinConfig.Config) == 0:
				pinConfig.LEDstateYellow = "slow"
				time.sleep(5)
				print("updating client")
				subprocess.call('git reset --hard  && git pull && reboot now', shell=True)
			else:
				currentMachineState.wifiAPmode = not currentMachineState.wifiAPmode
				if currentMachineState.wifiAPmode == True:
					subprocess.call('sudo ./switchToAP.sh', shell=True)
					pinConfig.LEDstateYellow = "fast"
				else:
					subprocess.call('sudo ./switchToWlan.sh', shell=True)
					pinConfig.LEDstateYellow = "off"
