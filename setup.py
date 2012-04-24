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
setup(name = common.PROGRAM_NAME,
    version = common.VERSION,
    description = common.DESCRIPTION,
    long_description = common.LONG_DESCRIPTION,
    author = common.AUTHORS,
    author_email = common.EMAILS,
    url = common.URL,
    license = common.LICENSE,
    platforms = common.PLATFORMS,

    package_dir = {"get_iplayer_downloader": "src/get_iplayer_downloader"},
    packages = ["get_iplayer_downloader", "get_iplayer_downloader.tools",
                "get_iplayer_downloader.ui", "get_iplayer_downloader.ui.tools"],
    #packages = ["", "get_iplayer_downloader.tools", 
    #            "get_iplayer_downloader.ui", "get_iplayer_downloader.ui.tools"],

    #"ui/*.ui", "ui/*.css"
    package_data = {"get_iplayer_downloader": ["default.conf", "GIT_VERSION", "ui/preferences.ui", "ui/style.css"]},

    # Moving .desktop file: for Debian/Ubuntu and Arch Linux packaging
    data_files = [("share/applications", ["res/get_iplayer_downloader.desktop"]),
                  ("share/get_iplayer_downloader/scripts", ["extra/get_iplayer_post_subdir.py"])],

    scripts = ["bin/get_iplayer_downloader"]
    )

common.cleanup_install()
