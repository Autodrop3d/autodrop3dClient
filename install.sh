sudo apt update
sudo apt -y install git
sudo apt -y install python3
sudo apt -y install python3-pip
sudo apt -y install fswebcam


sudo cp -a . /autodrop3dClient/
sudo chmod 755 -R /autodrop3dClient

cd /
cd /autodrop3dClient
pip3 install -r requirements.txt


#Create the file for the service to be added
sudo cp /autodrop3dClient/AD3D.service /lib/systemd/system/AD3D.service
sudo systemctl enable AD3D
sudo systemctl start AD3D
