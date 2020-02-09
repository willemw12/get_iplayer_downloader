get\_iplayer\_downloader
========================

get\_iplayer\_downloader is a GUI download utility for the BBC get\_iplayer program. It displays episodes in a large tree view with three text columns: series title, series categories and episode title plus episode description.

Features:

* Find episodes. Filter on categories, channels, recently cached episodes
* Download episodes or queue episodes for download
* Visit the episode's "BBC iPlayer" web page
* View episode properties
* View download logs and errors

Screenshots:

* [tree view](https://github.com/willemw12/get_iplayer_downloader/wiki/images/tree_view.jpg)
* [properties](https://github.com/willemw12/get_iplayer_downloader/wiki/images/properties.jpg)
* [preferences](https://github.com/willemw12/get_iplayer_downloader/wiki/images/preferences.jpg)

About:

This is a small utility program for me to try and find out the capabilities of the standard Python libraries and GTK+ 3. This is after I tried creating a version of the downloader with zenity in bash, which was far too slow.

This program works best on a high resolution screen. You can continue using the program, while get\_iplayer is downloading in the background. There is also an option to run get\_iplayer in a terminal emulator window when it is downloading episodes.

For the latest version, go to:

* [https://github.com/willemw12/get\_iplayer\_downloader](https://github.com/willemw12/get_iplayer_downloader)

For other news, go to:

* [https://github.com/willemw12/get\_iplayer\_downloader/wiki](https://github.com/willemw12/get_iplayer_downloader/wiki)

This program is licensed under GPLv3 (see included COPYING file).

Disclaimer: this program does not perform any downloading itself. It relies on the get\_iplayer program to perform the actual downloading.



Dependencies
------------

The dependencies are:

* get\_iplayer and its dependencies  
  [http://www.infradead.org/get\_iplayer/html/get\_iplayer.html](http://www.infradead.org/get_iplayer/html/get_iplayer.html)
* Python 3 (3.2 or higher)
* Python 3 setuptools for Distutils, used to install get\_iplayer\_downloader. On Debian/Ubuntu, package: python3-setuptools
* Python 3 GI/GIR (GObject Introspection Repository) libraries. On Debian/Ubuntu, packages: python3-gi, python3-gi-cairo
* GTK+ 3 libraries (3.14 or higher). On Debian/Ubuntu, package: gir\*-gtk-3\* (\* is a wildcard character)
* Linux. This program may work on other platforms with a few minor changes, however, that has not been tested



Configuration
-------------

In short:

* The get\_iplayer\_downloader preset names should refer to existing get\_iplayer presets (by default, files "tv" and "radio" in ~/.get\_iplayer/presets/)
* The get\_iplayer "info" property needs to be disabled by default (in the preset files)
* To modify the category or channel filters, the configuration file needs to be edited manually

### get\_iplayer

get\_iplayer\_downloader's default configuration has two get\_iplayer presets defined:

* radio - for radio episodes
* tv - for television episodes

The preset names are configurable. There is also an option in get\_iplayer\_downloader to disable the use of get\_iplayer presets.

To configure get\_iplayer for use with two presets, either reuse existing preset files or create new preset files. To create new preset files, run `get_iplayer --preset=radio --prefs-add ...`, etc., or create and edit the preset files ~/.get\_iplayer/presets/radio and ~/.get\_iplayer/presets/tv directly.

Here are two preset file examples. Lines starting with # are commented out. The "info" property should not be set or should be disabled by default, otherwise displaying episode search results will take a very long time.

File ~/.get\_iplayer/presets/radio:

    #command /usr/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>//<categorymain>_<categorysub>//<longname>" --force
    info 0
    output /home/willemw12/Music/bbc
    #radiomode better

File ~/.get\_iplayer/presets/tv:

    #command /usr/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --subdir-format="bbc.<week>//<categorymain>_<categorysub>//<longname>" --force
    info 0
    output /home/willemw12/Videos/bbc
    #tvmode good,better

Verify that `get_iplayer --preset=radio ...` and `get_iplayer --preset=tv ...` work properly from the command line.

Optionally, setup a get\_iplayer pvr scheduler (a cron job) to download queued episodes. Check the get\_iplayer documentation on how to do that.


### get\_iplayer\_downloader

Most configuration options can be managed from the GUI. Other options can be found in the configuration file (~/.config/get\_iplayer\_downloader/config), which will be created after running the program for the first time. Make sure the program is not running, before editing the configuration file.

Leave options, such as Channels and Download folder, empty in Preferences to use the default value specified in get\_iplayer.

Before downloading episodes for the first time, verify the download paths and, optionally, the terminal emulator program name and program arguments.

When searching for episodes, add a minus sign in front of the whole search term to exclude it from the search.

If the program crashes immediately on startup or when the mouse cursor moves over the first column in the episode list, disable the "show-tooltip" option or update GNOME 3 (or just update the GTK+ 3 and GI/GIR libraries).


#### Categories and channels

The radio and tv category lists and the radio channel list are very long and have been reduced to what is on the BBC iPlayer Radio and TV web pages. You can define your own search categories by editing the configuration file (they are lists of key-value pairs, i.e. lists of "search term"-"GUI label" pairs). File ./extra/my\_default.config is an example of that. To generate lists containing all the available categories and channels, which can be put in the configuration file, run from this directory:

    $ ./get_iplayer_downloader.py --list-categories --quiet
    $ ./get_iplayer_downloader.py --list-channels --quiet

Add a minus sign in front of a channel or a category to exclude it from the search and cache refresh.



Installation
------------

There are several ways to install the program. See below.

To execute without installing, run:

    $ <path to this directory>/src/get_iplayer_downloader.py

Or create a symbolic link of get\_iplayer\_downloader.py to a directory in $PATH. From this directory, run:

    $ ln -s $(pwd)/src/get_iplayer_downloader.py ~/bin/gipd

and then run:

    $ gipd


### Installation script

This should work on any Linux distribution. Run from this directory:

    $ ./install.sh

To uninstall, run from this directory:

    $ ./uninstall.sh

When python has been upgraded to a newer minor version, then uninstall and install again.


### Arch Linux package

To install the latest git version:

    $ ./install-pkg-git.sh

To install the latest version:

    $ ./install-pkg.sh

### Debian/Ubuntu package

__Warning: this may not work. Distutils command "bdist_deb" in package "python-stdeb" is required for Python 3.__

Install build and package tools (run as root)

    # apt-get install python-stdeb

Then

    $ ./install-deb.sh



Keyboard shortcuts
------------------

The keyboard shortcuts are:

    Shortcut                Command       Description

    alt+enter               Properties    View properties of the highlighted episode
    ctrl+c                  Clear         Clear episode download selection
    ctrl+d                  Download      Download selected episodes
    ctrl+f                  Find          Go to search entry field on the tool bar
    ctrl+l                  Log           View download log
    ctrl+p                  Play          Go to BBC iPlayer web page of the highlighted episode
    ctrl+q                  Queue         Queue selected episodes for one-off downloading
    ctrl+r                  Refresh       Refresh episode cache, limited of the selected programme type (radio or TV)
    ctrl+s, ctrl+shift+s    Since         Select since episodes were added to the search cache
    ctrl+t                  Type          Select programme type (radio or TV)
    f1                      Help          View keyboard shortcuts

    ctrl+1                  Type
    ctrl+2                  Category
    ctrl+3                  Channel
    ctrl+4, ctrl+5          Since

    down-arrow                            Go from tool bar to episode list
    space or enter                        Toggle selection in the episode list



Extra
-----

Q: How to have episodes in separate subfolders, grouped by main category and subcategories or by week?

A: Use the get\_iplayer\_post\_subdir.py script.

File ./extra/get\_iplayer\_post\_subdir.py is a get\_iplayer post-processing script. It is an extension to the get\_iplayer "subdir" output option. It requires get\_iplayer\_downloader to be installed and it does not update the download location recorded in the (localfiles) download history. The script supports additional formatting fields (categorymain, categorysub, week) in the subdirectory names. Field \<categorymain\> is the same as field \<category\> from get\_iplayer. For more information, run:

    $ ./extra/get_iplayer_post_subdir.py --help 

The script is installed in /usr/share/get\_iplayer\_downloader/scripts or in /usr/local/share/get\_iplayer\_downloader/scripts.

To configure get\_iplayer to use this script, put for example in ~/.get\_iplayer/presets/tv:

    command /usr/share/get_iplayer_downloader/scripts/get_iplayer_post_subdir.py --categories="<categories>" --dir="<dir>" --filename="<filename>" --force --subdir-format="bbc.<week>//<categorymain>_<categorysub>//<longname>"

