#!/bin/sh

echo "Uninstalling..."

echo "Removing the following files (not the directories)..."
cat installed-files.txt
cat installed-files.txt | xargs sudo rm -rfv

echo "Removing desktop menu item..."
sudo xdg-desktop-menu uninstall get_iplayer_downloader.desktop

