#!/bin/sh

echo "Uninstalling..."

echo "Removing the following files (not the containing directories)..."
FILE_LIST="installed-files.txt"
cat "$FILE_LIST"
if [ -f "$FILE_LIST" ]; then
  cat "$FILE_LIST" | xargs sudo rm -rfv
fi

echo "Removing desktop menu item..."
sudo xdg-desktop-menu uninstall get_iplayer_downloader.desktop

