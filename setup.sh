#!/bin/bash
#! /bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

# These settings should be defined before setup.


# read settings
# define install location, bed_size(x,y,z), auto_ejection(true/false), material_type, material_color

# install dependencies
sudo apt-get install software-properties-common python-software-properties git


# install python

# get Printrun from Github.
cp start.sh /etc/init.d/autodrop-start.sh
chmod 755 /etc/init.d/autodrop-start.sh
sudo update-rc.d /etc/init.d/autodrop-start.sh defaults
