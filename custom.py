import RPi.GPIO as GPIO

def myFunction():
	print("You successfully activated me from gcode")
	print(AutoDropSerialPort)
	print("i made a change here")

def EjectStuff():

 	print("Ejecting Stuff")
 	GPIO.setwarnings(False)
 	GPIO.setmode(GPIO.BOARD)
 	GPIO.setup(12, GPIO.OUT)
 	GPIO.output(12, 1)
 	time.sleep(30)  
 	GPIO.output(12, 0)
 	time.sleep(30) 