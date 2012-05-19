#!/bin/sh
#
# Build and install get_iplayer_downloader on Arch Linux
#

rm -rf ~/abs/get_iplayer_downloader
mkdir -p ~/abs/get_iplayer_downloader
cd ~/abs/get_iplayer_downloader
#wget https://github.com/willemw12/get_iplayer_downloader/raw/master/extra/abs/get_iplayer_downloader/get_iplayer_downloader.install
wget https://github.com/willemw12/get_iplayer_downloader/raw/master/extra/abs/get_iplayer_downloader/PKGBUILD
makepkg -sic --skipchecksums

