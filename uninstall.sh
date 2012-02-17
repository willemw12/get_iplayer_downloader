#!/bin/sh

echo
echo "Uninstalling desktop menu item..."
sudo xdg-desktop-menu uninstall get_iplayer_downloader.desktop
echo
echo "Please uninstall get_iplayer_downloader manually, for example:"
echo
echo "sudo rm -rf /usr/local/lib/python2.*/dist-packages/get_iplayer_downloader/"
echo "sudo rm -rf /usr/local/lib/python2.*/dist-packages/get_iplayer_downloader-*.egg-info"
echo "sudo rm /usr/local/bin/get_iplayer_downloader"
echo

