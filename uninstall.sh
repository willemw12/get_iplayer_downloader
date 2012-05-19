#!/bin/sh

echo "Uninstalling..."

echo "Removing the following files (and not the containing directories)..."
FILE_LIST="installed-files.txt"
cat "$FILE_LIST"
if [ -f "$FILE_LIST" ]; then
  # Force sudo password prompt
  sudo -K

  cat "$FILE_LIST" | xargs sudo rm -rf
  rm "$FILE_LIST"
else
  echo "$(basename $0): Cannot uninstall get_iplayer_downloader. To uninstall properly, first install then uninstall." >&2
fi

#echo "Removing desktop menu item and icon..."
#sudo xdg-desktop-menu uninstall get_iplayer_downloader.desktop
#sudo xdg-desktop-icon uninstall get_iplayer_downloader.svg
#sudo xdg-icon-resource uninstall --novendor --size 96 res/get_iplayer_downloader.png
#sudo gtk-update-icon-cache -q -t -f usr/share/icons/hicolor

