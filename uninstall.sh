#!/bin/sh

echo "Uninstalling..."

# Uninstall desktop menu item
sudo xdg-desktop-menu uninstall get_iplayer_downloader.desktop

cat installed-files.txt | xargs sudo rm -rfv

