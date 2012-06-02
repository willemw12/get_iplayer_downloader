#!/bin/sh

echo "Installing..."

sudo python3 setup.py install --record /tmp/installed-files.txt
cp /tmp/installed-files.txt .
sudo rm /tmp/installed-files.txt

sudo python3 setup.py clean 
sudo rm -r build
sudo find . -name __pycache__ -exec rm -rf '{}' \; 2>/dev/null

#echo "Installing desktop menu item and icon..."
#sudo xdg-desktop-menu install --novendor res/get_iplayer_downloader.desktop
#sudo xdg-desktop-icon install --novendor res/get_iplayer_downloader.desktop
#sudo xdg-icon-resource install --novendor --size 96 res/get_iplayer_downloader.png
#sudo gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor

