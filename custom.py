def myFunction():
	print("You successfully activated me from gcode")
	print(AutoDropSerialPort)
	print("i made a change here")

 def EjectStuff():
 	print("Ejecting Stuff")
 	GPIOa.setwarnings(False)
 	GPIOa.setmode(GPIO.BOARD)
 	GPIOa.setup(12, GPIO.OUT)
 	GPIOa.output(12, 1)
 	time.sleep(30)  
 	GPIOa.output(12, 0)
 	time.sleep(30) 