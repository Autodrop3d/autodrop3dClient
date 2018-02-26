#! /usr/bin/env python3
import os


#Number of different gcode files to produce
xx = 10
yy = 10




#Settings for slicer
slicerPath = r'"CuraEngine.exe -p -v -c "C:\Users\Me\AppData\Local\RepetierHost\cura.ini" -s posx=0 -s posy=0 '

for x in range(1, xx+1):
	for y in range(1, yy+1):
		os.system('openscad -o '+str(x)+'0x'+str(y)+'0.stl -D "x='+str(x)+'0;y='+str(y)+'0;" SeedFile.scad')
		os.system(slicerPath + "  -o " + str(x) + '0x'+str(y) + '0.gcode ' + str(x) + '0x' + str(y) + '0.stl  "-"')

