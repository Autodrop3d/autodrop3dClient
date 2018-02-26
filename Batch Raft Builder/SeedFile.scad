x=5;
y=5;

union() {
cube([x,y,.5],true);
translate([0,0,-3]) cube([.5,.5,3],false);
}

