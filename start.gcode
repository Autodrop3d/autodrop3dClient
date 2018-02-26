;@eject

G28 ; Home extruder
M107 ; Turn off fan
G90 ; Absolute positioning
M82 ; Extruder in absolute mode

; Activate all used extruder
M104 T0 S210
G92 E0 ; Reset extruder position
; Wait for all used extruders to reach temperature
M109 T0 S210

;@myFunction()
