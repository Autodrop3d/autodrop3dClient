#! /bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

# These settings should be defined before setup.


# read settings
# define install location, bed_size(x,y,z), auto_ejection(true/false), material_type, material_color

# install dependencies
sudo apt-get install screen software-properties-common git python-serial python-wxgtk2.8 python-pyglet python-numpy cython python-libxml2 python-gobject python-dbus python-psutil python-cairosvg python-pip libpython-dev figlet


# install python

# create directory for working files
mkdir /autodrop
cp -R . /autodrop/ #this won't work.
cd /autodrop

# get Printrun from Github and compile.
git clone https://github.com/kliment/Printrun.git
cd Printrun
pip install -r requirements.txt
python setup.py build_ext --inplace
cd ..

#clone and build WiringPi
sudo apt purge wiringpi
hash -r
sudo apt update
sudo apt upgrade
cd /autodrop/
git clone git://git.drogon.net/wiringPi
cd wiringPi
git pull origin
./build



#setup reboot at end of script
cp /autodrop/start.sh /etc/init.d/autodrop-start.sh
chmod 755 /etc/init.d/autodrop-start.sh
sudo update-rc.d autodrop-start.sh defaults
chmod +x /autodrop/start.sh
chmod +x /autodrop/stop.sh
chmod +w /autodrop/download.gcode
