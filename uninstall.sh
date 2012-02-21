#!/bin/sh

echo "Uninstalling..."

echo "Removing the following files (and not the containing directories)..."
FILE_LIST="installed-files.txt"
cat "$FILE_LIST"
if [ -f "$FILE_LIST" ]; then
  cat "$FILE_LIST" | xargs sudo rm -rfv
  rm -f "$FILE_LIST"
else
  echo "$(basename $0): Cannot uninstall get_iplayer_downloader" >&2
fi

echo "Removing desktop menu item..."
sudo xdg-desktop-menu uninstall get_iplayer_downloader.desktop

