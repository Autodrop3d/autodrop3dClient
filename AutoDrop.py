#! /usr/bin/env python3
ServerTestMode="off"


import _thread
import time
from urllib.request import urlretrieve
from flask import Flask, render_template, request
import subprocess




if ServerTestMode != "on":
	try:
		import RPi.GPIO as GPIO
		import serial
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



currentPrintModeIsRafting = 0


f = open("settings.txt",'r');
AutoDropSerialPort = str(f.readline()).strip()
AutoDropSerialPortSpeed = str(f.readline()).strip()
printerServer = str(f.readline()).strip()
printerName = str(f.readline()).strip()
SliceOnPrinter = str(f.readline()).strip()
printerPositionOffsetOverideX  = str(f.readline()).strip()
printerPositionOffsetOverideY  = str(f.readline()).strip()
printerPositionOffsetOverideZ  = str(f.readline()).strip()
levelingPointA = str(f.readline()).strip()
levelingPointB = str(f.readline()).strip()
levelingPointC = str(f.readline()).strip()
f.close()






CuraSlicerPathAndCommand = "CuraEngine -v -c cura.ini -s posx=0 -s posy=0 {options} -o {OutFile}.gcode {inFile}.stl    2>&1";

@app.route('/image.png')
def liveImageFile():
	subprocess.call('fswebcam -S 20 ./static/junk.png', shell=True)
	return app.send_static_file('junk.png')


@app.route('/',methods = ['GET', 'POST'])
def index():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, SliceOnPrinter, printerPositionOffsetOverideX, printerPositionOffsetOverideY, printerPositionOffsetOverideZ, levelingPointA, levelingPointB, levelingPointC

	if request.method == 'POST':

		AutoDropSerialPort = request.form['AutoDropSerialPort']

		AutoDropSerialPortSpeed =  request.form['AutoDropSerialPortSpeed']

		printerServer =  request.form['printerServer']

		printerName = request.form['printerName']

		SliceOnPrinter = request.form['SliceOnPrinter']


		levelingPointA = request.form['levelingPointA']
		levelingPointB = request.form['levelingPointB']
		levelingPointC = request.form['levelingPointC']



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
		f.write( levelingPointA + "\n")
		f.write( levelingPointB + "\n")
		f.write( levelingPointC + "\n")
		f.close()


	try:
		PLUGINFUNCTIONS = open("custom.py",'r').read()
	except:
		PLUGINFUNCTIONS = ""

	return render_template('index.html', AutoDropSerialPort = AutoDropSerialPort , AutoDropSerialPortSpeed = AutoDropSerialPortSpeed, printerServer = printerServer , printerName = printerName,  PLUGINFUNCTIONS = PLUGINFUNCTIONS, SliceOnPrinter = SliceOnPrinter, printerPositionOffsetOverideX = printerPositionOffsetOverideX, printerPositionOffsetOverideY = printerPositionOffsetOverideY, printerPositionOffsetOverideZ = printerPositionOffsetOverideZ, levelingPointA = levelingPointA, levelingPointB = levelingPointB, levelingPointC = levelingPointC)









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
	global s, currentPrintModeIsRafting, raftOffsetX, raftOffsetY, raftOffsetZ
	raftOffsetY = 0


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
				raftOffsetY = raftOffsetY - .5
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
	global s, printerPositionOffsetOverideX , printerPositionOffsetOverideY, printerPositionOffsetOverideZ
	s = serial.Serial(AutoDropSerialPort,AutoDropSerialPortSpeed)
	piceOfGcodeToSend = request.args['gcode']
	SendGcodeLine(offsetGcodeDuringRaft(piceOfGcodeToSend))
	return piceOfGcodeToSend




def MainPrinterLoop():
	global AutoDropSerialPort,AutoDropSerialPortSpeed, printerServer, printerName, SliceOnPrinter
	while 1: #loop for ever
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

			f.close()

			#PrintFile("start.gcode")
			PrintFile("download.g")
			#PrintFile("end.gcode")

			URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
			print(URLtoDownload)
			urlretrieveWithFail(URLtoDownload, "download.g")

			URLtoDownload = printerServer + "?jobID=" + PrintNumber + "&stat=Done"
			print(URLtoDownload)
			urlretrieveWithFail(URLtoDownload, "download.g")

		time.sleep(10)


_thread.start_new_thread(MainPrinterLoop,())
while 1:
	time.sleep(10)
