#!/bin/sh

echo "Installing..."

sudo python setup.py install --record /tmp/installed-files.txt
cp /tmp/installed-files.txt .
sudo rm /tmp/installed-files.txt

sudo python setup.py clean 
sudo rm -r build

echo "Installing desktop menu item..."
sudo xdg-desktop-menu install --novendor res/get_iplayer_downloader.desktop

