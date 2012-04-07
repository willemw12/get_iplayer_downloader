import os
import subprocess
import sys
from distutils.core import setup

# Add "src" to Python search paths
sys.path.insert(0, "src")

# Application-wide constants
import get_iplayer_downloader.common

if os.path.exists(os.path.join(os.getcwd(), "MANIFEST")):
    os.remove(os.path.join(os.getcwd(), "MANIFEST"))

## Linux specific
#if os.geteuid() == 0:
#    # Root user
#    # Install desktop menu item
#    echo "Installing desktop menu item..."
#    subprocess.call(["xdg-desktop-menu install --novendor res/get_iplayer_downloader.desktop"], shell=True)

#NOTE name can be anything. It is the folder name in /usr/local/lib/python*/dist-packages
setup(name = get_iplayer_downloader.common.__program_name__,
    version = get_iplayer_downloader.common.__version__ ,
    description = get_iplayer_downloader.common.__description__,
    long_description = get_iplayer_downloader.common.__long_description__,
    author = get_iplayer_downloader.common.__authors__,
    author_email = get_iplayer_downloader.common.__emails__,
    url = get_iplayer_downloader.common.__url__,
    license = get_iplayer_downloader.common.__license__,
    platforms = get_iplayer_downloader.common.__platforms__,

    package_dir = {"get_iplayer_downloader": "src/get_iplayer_downloader"},
    packages = ["get_iplayer_downloader", "get_iplayer_downloader.tools",
                "get_iplayer_downloader.ui", "get_iplayer_downloader.ui.tools"],
    #packages = ["", "get_iplayer_downloader.tools", 
    #            "get_iplayer_downloader.ui", "get_iplayer_downloader.ui.tools"],

    #"ui/*.ui", "ui/*.css"
    package_data = {"get_iplayer_downloader": ["default.conf", "ui/preferences.ui", "ui/style.css"]},

    # Moving .desktop file: for Debian/Ubuntu and Arch Linux packaging
    data_files = [("share/applications", ["res/get_iplayer_downloader.desktop"]),
                  ("share/get_iplayer_downloader/scripts", ["extra/get_iplayer_post_subdir.py"])],

    scripts = ["bin/get_iplayer_downloader"]
    )
