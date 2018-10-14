M104 T0 S200
G28
;You could use this one or make your own as in the plugin functions @eject
;@EjectStuff()


G28 ; Home extruder
M107 ; Turn off fan
G90 ; Absolute positioning
M82 ; Extruder in absolute mode

; Activate all used extruder
; M104 T0 S200
G92 E0 ; Reset extruder position
; Wait for all used extruders to reach temperature
M109 T0 S200

;@myFunction()

; Turn on fan 
M106 P0
M106 P1
M106 P2



;set extrude factor override percentage (over/under-extrusion fix)
M221 S130
;set speed factor percentage
M220 S100

G1 X0 Y0 Z0
