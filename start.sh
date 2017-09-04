#! /bin/bash
sleep 10
until ping -c1 www.google.com &>/dev/null; do :; done
cd /autodrop
screen -d -m /bin/bash './AutoDrop.sh'
echo Process started

exit 0