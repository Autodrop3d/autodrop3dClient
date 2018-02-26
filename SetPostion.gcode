M999
;@time.sleep(5) 
G28 ; Home extruder

G90 ; Absolute positioning
M82 ; Extruder in absolute mode


G92 E0 ; Reset extruder position

M400
G92 X0 Y0 Z0
M400
G1 X0 Y0 Z3.8
M400
G92 X0 Y0 Z0
M400
G1 X0 Y0
;set extrude factor override percentage (over/under-extrusion fix)
M221 S100
;set speed factor percentage
M220 S100


