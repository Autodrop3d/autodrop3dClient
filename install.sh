# Install apt requirements.
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install fswebcam
sudo apt-get install python3-serial

#move service files to service location.
sudo mkdir /autodrop3dClient/
sudo cp -a . /autodrop3dClient/
sudo chmod 755 -R /autodrop3dClient

#move to service location and install pip requirements.
cd /autodrop3dClient
pip3 install -r requirements.txt
pip3 install flask

#Create, Enable, and Start AD3D service.
sudo cp /autodrop3dClient/AD3D.service /lib/systemd/system/AD3D.service
sudo systemctl enable AD3D
sudo systemctl start AD3D
