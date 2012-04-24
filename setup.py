import os
import sys
from distutils.core import setup

# Add "src" to Python search paths
sys.path.insert(0, "src")

# Application-wide constants
import get_iplayer_downloader.common as common

####

if os.path.exists(os.path.join(os.getcwd(), "MANIFEST")):
    os.remove(os.path.join(os.getcwd(), "MANIFEST"))

## Linux specific
#if os.geteuid() == 0:
#    # Root user
#    # Install desktop menu item
#    echo "Installing desktop menu item..."
#    subprocess.call(["xdg-desktop-menu install --novendor res/get_iplayer_downloader.desktop"], shell=True)

#NOTE name can be anything. It is the folder name in /usr/local/lib/python*/dist-packages
setup(name = common.__program_name__,
    version = common.__version__,
    description = common.__description__,
    long_description = common.__long_description__,
    author = common.__authors__,
    author_email = common.__emails__,
    url = common.__url__,
    license = common.__license__,
    platforms = common.__platforms__,

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
