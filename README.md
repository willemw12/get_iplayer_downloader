get\_iplayer\_downloader
========================

get\_iplayer\_downloader is a download utility for the BBC get\_iplayer program.

This program is a graphical version of the command `get_iplayer --tree`, followed by `get_iplayer --pid` or `get_iplayer --info`. It displays programmes in a large treeview with two main columns: serie title and episode title plus description.

It is a small utility program for me to try and find out what can be done with standard Python and GTK+ 3. This is after I tried creating a version of the downloader with zenity in bash, which was far too slow.

You can continue using the program, while get\_iplayer is downloading in the background. I let the downloads run in one or more terminal windows, so I can see when a download hangs or fails.

This program works best with a screen resolution of 1024x768 or higher.

Some screenshots:

* [screenshot1](https://github.com/willemw12/get_iplayer_downloader/wiki/images/screenshot1.png)
* [screenshot2](https://github.com/willemw12/get_iplayer_downloader/wiki/images/screenshot2.png)

For the latest version go to:

* [https://github.com/willemw12/get\_iplayer\_downloader](https://github.com/willemw12/get_iplayer_downloader)

For other news go to:

* [https://github.com/willemw12/get\_iplayer\_downloader/wiki](https://github.com/willemw12/get_iplayer_downloader/wiki)

This program is licensed under GPLv3 (see included file COPYING).

Disclaimer: this program doesn't perform any downloading itself. It relies on the get\_iplayer program to do the actual downloading.



Dependencies
------------

* get\_iplayer and its dependencies  
  [http://www.infradead.org/get\_iplayer/html/get\_iplayer.html](http://www.infradead.org/get_iplayer/html/get_iplayer.html)
* Python 2.7 or higher (not Python 3)
* Python setuptools, to run setup.py
* GNOME libraries for Python (mainly GTK+ 3)
* Linux. Only required to run get\_iplayer in a terminal window.  
  This program may work on other platforms, however, that has not been tested



Configuration
-------------


### get\_iplayer

Currently, get\_iplayer\_downloader uses two get\_iplayer presets: one for radio and podcasts and one for television.

The default preset names used by get\_iplayer\_downloader are: radio and tv. The preset file names are configurable in get\_iplayer\_downloader.

Reuse existing preset files or create new presets files. To create new preset files, either run `get_iplayer --preset=radio --prefs-add ...`, etc. or edit the preset files ~/.get\_iplayer/presets/radio and ~/.get\_iplayer/presets/tv directly. 

Here are two preset file examples. Lines starting with # are commented out.

File ~/.get\_iplayer/presets/radio:

    aactomp3 1
    #command /usr/local/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>/<categorymain>_<category>/<longname>" --verbose
    fileprefix <name>-<episode>-<lastbcast>
    isodate 1
    output /var/tmp/get_iplayer_downloader/Music
    radiomode flashaudio,realaudio,flashaac,wma

File ~/.get\_iplayer/presets/tv:

    #command /usr/local/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>/<categorymain>_<category>/<longname>" --verbose
    fileprefix <name>-<episode>-<lastbcast>
    isodate 1
    output /var/tmp/get_iplayer_downloader/Videos
    tvmode flashhigh,flashstd,flashnormal

Now `get_iplayer --preset=radio ...` and `get_iplayer --preset=tv ...` should work properly from the command line.

Optionally, setup a get\_iplayer pvr scheduler (a cron job) to download queued programmes.


### get\_iplayer\_downloader

Most configuration settings can be managed from the GUI. Other settings can be found in the configuration file (~/.config/get\_iplayer\_downloader/get\_iplayer\_downloader.conf), which will be created after running the program for the first time. Make sure the program is not running, before editing the configuration file.

Before downloading programmes for the first time, verify the download paths and terminal emulator program name in the GUI or in the configuration file.

The preconfigured search channels and categories are a reduced set. To start off with category lists containing all available categories, run:

    get_iplayer --preset=radio --flush
    get_iplayer --preset=tv --flush
    <path to this directory>/src/get_iplayer_downloader.py --list-categories --quiet

and put the printed output in the configuration file. The same can be done for channels (`get_iplayer_downloader.py --list-channels`) or clear the channel lists in the configuration to search in all channels.

If the program crashes when the mouse cursor moves over the first column in the search result treeview, then disable "show-tooltip" in the configuration file or update the GNOME libraries (in particular GTK+ 3).



Installation
------------

To execute without installing, run:

    <path to this directory>/src/get_iplayer_downloader.py

There are several ways to install the program.


### General install script

Run from this directory:

    ./install.sh

Then to execute, run:

    get_iplayer_downloader

or run it from the desktop menu.

To uninstall, run from this directory:

    ./uninstall.sh

If the python 2 (2.7 or higher) executable name is python2, then replace the first command above by:

    python2 <path to this directory>/src/get_iplayer_downloader.py

and change the install.sh and uninstall.sh scripts.


### For Debian/Ubuntu

Build and install a .deb file:

    # Install build and package tools
    sudo apt-get install python-stdeb

    # Create a .deb file in directory deb_dist from Python setuptools (distutils) files
    sudo rm *.deb
    python setup.py --command-packages=stdeb.command bdist_deb

    # Install .deb file
    sudo dpkg -i deb_dist/python-get-iplayer-downloader_*_all.deb
    rm -rf deb_dist/


### For Arch Linux

There are two PKGBUILD files. For example, to build and install the latest version:

    rm -rf ~/abs/get_iplayer_downloader-git
    mkdir -p ~/abs/get_iplayer_downloader-git
    cd ~/abs/get_iplayer_downloader-git
    wget https://github.com/willemw12/get_iplayer_downloader/raw/master/extra/abs/get_iplayer_downloader-git/PKGBUILD
    #makepkg -ic --skipchecksums
    makepkg -ic



Keyboard shortcuts
------------------

    alt + enter     Properties  View properties of highlighted programme (of programme in focus)
    ctrl + d        Download    Download or queue selected programmes
    ctrl + q        Queue       Queue selected programmes for one-off downloading by get_iplayer pvr
    ctrl + f        Find        Go to search entry field on the tool bar
    ctrl + t        Toggle      Rotate between programme types (radio, podcast, tv)
    ctrl + c        Clear       Clear programme download selection
    ctrl + r        Refresh     Refresh programme cache
    f1              Help        View keyboard shortcuts

    down-arrow                  Go from tool bar to the search result
    space or enter              Toggle programme selection in the search result



Extra
-----

File ./extra/get\_iplayer\_post\_subdir.py is a get\_iplayer post-processing script. It is an extension to the get\_iplayer subdir output option. The script supports additional property substitutions (category, week, ...) in the output subdirectory names. For more information, run:

    ./extra/get_iplayer_post_subdir.py --help 

To install and configure, copy or link the script to a directory in $PATH, for example:

    ln -s <absolute path to this directory>/extra/get_iplayer_post_subdir.py ~/bin/get_iplayer_post_subdir.py

or add a path in front of the command below. Then put, for example, in ~/.get\_iplayer/presets/tv:

    command get_iplayer_post_category.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>/<categorymain>_<category>/<longname>"

If the python 2 (2.7 or higher) executable name is python2, then start the command with:

    command python2 get_iplayer_post_category.py

The script is also installed in /usr/share/get\_iplayer\_downloader/scripts or in /usr/local/share/get\_iplayer\_downloader/scripts.

