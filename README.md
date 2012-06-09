get\_iplayer\_downloader
========================

get\_iplayer\_downloader is a download utility for the BBC get\_iplayer program.

It is a small utility program for me to try and find out the capabilities of standard Python and GTK+ 3. This is after I tried creating a version of the downloader with zenity in bash, which was far too slow.

This program is a graphical version of the command `get_iplayer --tree`, followed by `get_iplayer --pid` or `get_iplayer --info`. It displays programmes in a large tree view with two main columns: serie title, episode title plus episode description. This program works best with a screen resolution of 1024x768 or higher. You can continue using the program, while get\_iplayer is downloading in the background. Note that get\_iplayer has a fixed download list size (info\_limit = 40). There is also an option to run get\_iplayer in a terminal emulator window when it is downloading programmes.

Some screenshots:

* [tree view](https://github.com/willemw12/get_iplayer_downloader/wiki/images/tree_view.jpg)
* [properties](https://github.com/willemw12/get_iplayer_downloader/wiki/images/properties.jpg)
* [preferences](https://github.com/willemw12/get_iplayer_downloader/wiki/images/preferences.jpg)

For the latest version go to:

* [https://github.com/willemw12/get\_iplayer\_downloader](https://github.com/willemw12/get_iplayer_downloader)

For other news go to:

* [https://github.com/willemw12/get\_iplayer\_downloader/wiki](https://github.com/willemw12/get_iplayer_downloader/wiki)

This program is licensed under GPLv3 (see included file COPYING).

Disclaimer: this program does not perform any downloading itself. It relies on the get\_iplayer program to do the actual downloading.



Dependencies
------------

The dependencies are:

* get\_iplayer and its dependencies  
  [http://www.infradead.org/get\_iplayer/html/get\_iplayer.html](http://www.infradead.org/get_iplayer/html/get_iplayer.html)
* Python 3 (3.2 or higher)
* Python setuptools (pytyon3-setuptools), to install get\_iplayer\_downloader
* GNOME libraries for Python (mainly GTK+ 3). In most cases, already installed.  
  For Debian/Ubuntu, check that the following packages are also installed: python3-gi, python3-gi-cairo 
* Linux. This program may work on other platforms (with a few minor software changes), however, that has not been tested



Configuration
-------------

### get\_iplayer

Currently, get\_iplayer\_downloader uses two get\_iplayer presets: one for radio programmes and podcasts and one for television programmes. The default preset names used by get\_iplayer\_downloader are: radio and tv. The preset file names are configurable.

Either reuse existing preset files or create new presets files. To create new preset files, run `get_iplayer --preset=radio --prefs-add ...`, etc. or edit the preset files ~/.get\_iplayer/presets/radio and ~/.get\_iplayer/presets/tv directly. 

Here are two preset file examples. Lines starting with # are commented out.

File ~/.get\_iplayer/presets/radio:

    aactomp3 1
    #command /usr/local/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>/<categorymain>_<category>/<longname>" --verbose
    #ffmpeg /usr/bin/avconv
    fileprefix <name>-<episode>-<lastbcast>
    isodate 1
    #listformat <index>:   <name>: <episode> (<pid>)
    output /home/willemw12/Music/bbc
    radiomode flashaudio,realaudio,flashaac,wma

File ~/.get\_iplayer/presets/tv:

    #command /usr/local/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>/<categorymain>_<category>/<longname>" --verbose
    fileprefix <name>-<episode>-<lastbcast>
    isodate 1
    #listformat <index>:   <name>: <episode> (<pid>)
    output /home/willemw12/Videos/bbc
    tvmode flashhigh,flashstd,flashnormal

Verify that `get_iplayer --preset=radio ...` and `get_iplayer --preset=tv ...` work properly from the command line.
	
Optionally, setup a get\_iplayer pvr scheduler (a cron job) to download queued programmes. Check the get\_iplayer documentation on how to do that.


### get\_iplayer\_downloader

Most configuration settings can be managed from the GUI. Other settings can be found in the configuration file (~/.config/get\_iplayer\_downloader/config), which will be created after running the program for the first time. Make sure the program is not running, before editing the configuration file.

Before downloading programmes for the first time, verify the download paths and optionally the terminal emulator program name and options. To use the default download path specified in get\_iplayer, leave the download path empty.

The radio and tv category lists and the radio channel list are very long and have been reduced to what is on the BBC iPlayer Radio and TV web pages. You can define your own search categories by editing the configuration file (lists of key-value pairs, i.e. <search term>-<GUI label> pairs). To generate lists containing all the available categories and channels, which can be put in the configuration file, run from this directory:

    ./get_iplayer_downloader.py --list-categories --quiet
    ./get_iplayer_downloader.py --list-channels --quiet

If the program crashes immediately on startup or when the mouse cursor moves over the first column in the programme search result, disable the "show-tooltip" option or update the GNOME libraries (in particular GTK+ 3).



Installation
------------

There are several ways to install the program, see sections below.

After installation, run:

    get_iplayer_downloader

or run it from the desktop menu.

To execute without installing, run:

    <path to this directory>/src/get_iplayer_downloader.py

Or create a symbolic link of get_iplayer_downloader.py in a directory of $PATH. From this directory:

    ln -s $(pwd)/src/get_iplayer_downloader.py ~/bin/get_iplayer_downloader

and run it as:

    get_iplayer_downloader
    

### Installing by install script

This should work on any Linux distribution. Run from this directory:

    ./install.sh

To uninstall, run from this directory:

    ./uninstall.sh


### Installing as an Arch Linux package

To install the latest git version:

    ./install-pkgbuild-git.sh

To install the latest version:

    ./install-pkgbuild.sh

### Installing as a Debian/Ubuntu package

__Warning: this does not work in Python 3. Distutils command "bdist_deb" in package "python-stdeb" is not available for Python 3.__

    # Install build and package tools
    sudo apt-get install python-stdeb

    ./install-deb.sh



Keyboard shortcuts
------------------

The keyboard shortcuts are:

    Shortcut                Command       Description

    alt+enter               Properties    View properties of highlighted programme (of programme in focus)
    ctrl+c                  Clear         Clear programme download selection
    ctrl+d                  Download      Download or queue selected programmes
    ctrl+f                  Find          Go to search entry field on the tool bar
    ctrl+l                  Log           View log
    ctrl+q                  Queue         Queue selected programmes for one-off downloading by get_iplayer pvr
    ctrl+r                  Refresh       Refresh programme cache
    ctrl+s, ctrl+shift+s    Since         Select since programmes were added to the search cache
    ctrl+t                  Type          Select programme type (radio, podcast, tv)
    f1                      Help          View keyboard shortcuts

    down-arrow                            Go from tool bar to the search result
    space or enter                        Toggle programme selection in the search result



Extra
-----

Want to group downloaded programmes automatically by main category or by week?

File ./extra/get\_iplayer\_post\_subdir.py is a get\_iplayer post-processing script. It is an extension to the get\_iplayer "subdir" output option. The script supports additional property substitutions (category, categorymain, week) in the output subdirectory names. For more information, run:

    ./extra/get_iplayer_post_subdir.py --help 

The script is installed in /usr/share/get\_iplayer\_downloader/scripts or in /usr/local/share/get\_iplayer\_downloader/scripts.

To configure, put for example in ~/.get\_iplayer/presets/tv:

    command /usr/local/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>/<categorymain>_<category>/<longname>"
