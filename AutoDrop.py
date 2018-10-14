#! /usr/bin/env python3
ServerTestMode="off"


import _thread
import time
from urllib.request import urlretrieve
from flask import Flask, render_template, request

if ServerTestMode != "on":
	try:
		import RPi.GPIO as GPIO
		import serial
	except:
			print("failed to start ras pi stuff")



app = Flask(__name__)

s = '';


currentRaftOfsetX = 0
currentRaftOfsetY = 0
currentRaftOfsetZ = 40

currentPrintModeIsRafting = 0


f = open("settings.txt",'r');
AutoDropSerialPort = str(f.readline()).strip()
AutoDropSerialPortSpeed = str(f.readline()).strip()
printerServer = str(f.readline()).strip()
printerName = str(f.readline()).strip()
printerMaterial = str(f.readline()).strip()
SIZEX = str(f.readline()).strip()
SIZEY = str(f.readline()).strip()
SIZEZ = str(f.readline()).strip()
SliceOnPrinter = str(f.readline()).strip()
currentRaftOfsetX  = str(f.readline()).strip()
currentRaftOfsetY  = str(f.readline()).strip()
currentRaftOfsetZ  = str(f.readline()).strip()
f.close()






CuraSlicerPathAndCommand = "CuraEngine -v -c cura.ini -s posx=0 -s posy=0 {options} -o {OutFile}.gcode {inFile}.stl    2>&1";


@app.route('/',methods = ['GET', 'POST'])
def index():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, printerMaterial ,SIZEX, SIZEY, SIZEZ, SliceOnPrinter, currentRaftOfsetX, currentRaftOfsetY, currentRaftOfsetZ

	if request.method == 'POST':

		AutoDropSerialPort = request.form['AutoDropSerialPort']

		AutoDropSerialPortSpeed =  request.form['AutoDropSerialPortSpeed']

		printerServer =  request.form['printerServer']

		printerName = request.form['printerName']

		printerMaterial  = request.form['printerMaterial']

		SIZEX = request.form['SIZEX']

		SIZEY = request.form['SIZEY']

		SIZEZ = request.form['SIZEZ']

		SliceOnPrinter = request.form['SliceOnPrinter']

		currentRaftOfsetX = request.form['currentRaftOfsetX']
		currentRaftOfsetY = request.form['currentRaftOfsetY']
		currentRaftOfsetZ = request.form['currentRaftOfsetZ']


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
		f.write( SliceOnPrinter + "\n")
		f.write( currentRaftOfsetX + "\n")
		f.write( currentRaftOfsetY + "\n")
		f.write( currentRaftOfsetZ + "\n")
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

	return render_template('index.html', AutoDropSerialPort = AutoDropSerialPort , AutoDropSerialPortSpeed = AutoDropSerialPortSpeed, printerServer = printerServer , printerName = printerName, printerMaterial = printerMaterial, SIZEX = SIZEX, SIZEY = SIZEY , SIZEZ = SIZEZ, STARTGCODE = STARTGCODE, ENDGCODE = ENDGCODE, PLUGINFUNCTIONS = PLUGINFUNCTIONS, SliceOnPrinter = SliceOnPrinter, currentRaftOfsetX = currentRaftOfsetX, currentRaftOfsetY = currentRaftOfsetY, currentRaftOfsetZ = currentRaftOfsetZ)









@app.route('/slicer',methods = ['GET', 'POST'])
def slicer():
	return render_template('slicer.html')


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



def offsetGcodeDuringRaft(orgNonManipulatedString = ""):
	global currentRaftOfsetX, currentRaftOfsetY, currentRaftOfsetZ
	ManipulatedString = ""
	for member in orgNonManipulatedString.split( ):
		if (member[0] == "X"):
			member = member.replace("X","")
			member = "X" + str(round(float(member) + float(currentRaftOfsetX), 6) )
		if (member[0] == "Y"):
			member = member.replace("Y","")
			member = "Y" + str(round(float(member) + float(currentRaftOfsetY), 6) )
		if (member[0] == "Z"):
			member = member.replace("Z","")
			member = "Z" + str(round(float(member) + float(currentRaftOfsetZ), 6) )

		ManipulatedString = ManipulatedString + " " + member + " "

	ManipulatedString = ManipulatedString.strip()
	print("ORG GCODE " + orgNonManipulatedString)
	print("Maniuplated Gcode " +  ManipulatedString)
	return ManipulatedString



def SendGcodeLine(ll = ''):
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


def PrintFile(gcodeFileName = 'test.g'):
	global s, currentPrintModeIsRafting, currentRaftOfsetY
	currentRaftOfsetY = 0


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
			print("This is a comment line :*" +str( l) + "*")

			if l.startswith(b';LAYER:-2'):
				currentPrintModeIsRafting = currentPrintModeIsRafting + 1
				currentRaftOfsetY = currentRaftOfsetY - .5
			if l.startswith(b';LAYER:0'):
				currentPrintModeIsRafting = 0
			if str(l).find(";@") != -1:
				if str(l.split(b'@',1)[1],"ascii") == "eject":
					EjectStuff()
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
	s.close()

def urlretrieveWithFail(OptionA = "",OptionB = ""):
	try:
		f = open(OptionB,'w');
		f.write("")
		f.close()
		urlretrieve(OptionA,OptionB)
	except:
		print("Failed Retrieve File")


if ServerTestMode == "on":
	while 1:
		time.sleep(10)
		print("fake looping for printer")


@app.route('/manualcontroll',methods = ['GET', 'POST'])
def manualcontroll():
	global s, currentRaftOfsetX , currentRaftOfsetY, currentRaftOfsetZ
	s = serial.Serial(AutoDropSerialPort,AutoDropSerialPortSpeed)
	piceOfGcodeToSend = request.args['gcode']
	SendGcodeLine(offsetGcodeDuringRaft(piceOfGcodeToSend))
	return piceOfGcodeToSend

def MainPrinterLoop():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, printerMaterial ,SIZEX, SIZEY, SIZEZ ,SliceOnPrinter
	while 1: #loop for ever
		URLtoDownload = printerServer + "?name=" + printerName +  "&material=" + printerMaterial + "&SizeX=" + 	SIZEX +"&SizeY=" + SIZEY + "&SizeZ=" + SIZEZ + "&NoGcode=" + SliceOnPrinter
		urlretrieveWithFail(URLtoDownload, "download.g")
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

			bla = str(f.readline()).strip()
			bla = str(f.readline()).strip()
			bla = str(f.readline()).strip()
			bla = str(f.readline()).strip()
			bla = str(f.readline()).strip()
			bla = str(f.readline()).strip()
			bla = str(f.readline()).strip()
			PrintDimensions =  bla.replace(";","").strip().split(".")

			PrintDimensionsX = int(PrintDimensions[1])
			PrintDimensionsY = int(PrintDimensions[2])
			PrintDimensionsX = int(round((PrintDimensionsX +10) /10.0)*10.0)
			PrintDimensionsY = int(round((PrintDimensionsY +10) /10.0)*10.0)

			print("Size x = ")
			print(PrintDimensionsX)

			print("Size y = ")
			print(PrintDimensionsY)

			print("Print Dimensions are")
			print(PrintDimensions )

			print("PrintNumber=" + PrintNumber)

			f.close()
			PrintFile("start.gcode")
			#PrintFile("./Batch Raft Builder/" + str(PrintDimensionsX) + "x" + str(PrintDimensionsY) + ".gcode" )

			#PrintFile("SetPostion.gcode")

			PrintFile("download.g")
			PrintFile("end.gcode")


			URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
			print(URLtoDownload)
			urlretrieveWithFail(URLtoDownload, "download.g")

		time.sleep(10)


_thread.start_new_thread(MainPrinterLoop,())
while 1:
	time.sleep(10)
