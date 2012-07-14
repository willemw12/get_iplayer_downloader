#!/bin/sh
#
# Build and install get_iplayer_downloader-git on Arch Linux
#

rm -rf ~/abs/get_iplayer_downloader-git
mkdir -p ~/abs/get_iplayer_downloader-git

cd ~/abs/get_iplayer_downloader-git

#wget https://github.com/willemw12/get_iplayer_downloader/raw/master/extra/abs/get_iplayer_downloader-git/get_iplayer_downloader-git.install
wget https://github.com/willemw12/get_iplayer_downloader/raw/master/extra/abs/get_iplayer_downloader-git/PKGBUILD
makepkg -sic

