# autodrop3dClient
Client software for 3d printers interfacing with AutoDrop3D


This is the client software for the autodrop3d printer system.
This software automatically retrieves gcode print jobs from the autodrop3d server and sends the gcode via serial to the printer connected to the raspberry pi.

There are additional features to make automatic part ejection possible by toggling the GPIO pins of the raspberry pi using wiringpi.


When this script is run a web server will start serving on port 8080 from the pi. 
You can then go to that address and modify the settings for the printer, configure your autodrop3d url and serial interface/basud speed.


You can download the raspberry pi from
https://github.com/Autodrop3d/autodrop3dClient/releases/download/1.0/AD3d.image.zip
