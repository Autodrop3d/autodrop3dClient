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

	
	
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080)