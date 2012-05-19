#!/bin/sh
#
# Build and install get_iplayer_downloader on Debian/Ubuntu
#
# Prerequisite: build and package tools
#   sudo apt-get install python-stdeb
#

echo "ERROR: Distutils command \"bdist_deb\" in package \"python-stdeb\" is not available for Python 3."
echo "ERROR: get_iplayer_downloader runs in Python 3 and this script does not work in Python 3."
exit 1

# Create a .deb file in directory deb_dist from Python setuptools (distutils) files
sudo rm *.deb
python3 setup.py --command-packages=stdeb.command bdist_deb

# Install the .deb file
sudo dpkg -i deb_dist/python-get-iplayer-downloader_*_all.deb
rm -rf deb_dist/
