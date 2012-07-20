import os
import shutil
import sys
from distutils.core import setup

# Add "src" to the Python search paths
sys.path.insert(0, "src")

# Load application-wide definitions
import get_iplayer_downloader

if os.path.exists(os.path.join(os.getcwd(), "MANIFEST")):
    os.remove(os.path.join(os.getcwd(), "MANIFEST"))

#shutil.copy("res/get_iplayer_downloader.svg", "src/get_iplayer_downloader/")

## Linux specific
#if os.geteuid() == 0:
#    # Running as root
#    echo "Installing desktop menu item and icon..."
#    subprocess.call(["xdg-desktop-menu install --novendor res/get_iplayer_downloader.desktop"], shell=True)
#    subprocess.call(["xdg-desktop-icon install --novendor res/get_iplayer_downloader.svg"], shell=True)

#NOTE "name" can be anything. It is the folder name in /usr/local/lib/python*/dist-packages or /usr/lib/python*/dist-packages
setup(name = get_iplayer_downloader.PROGRAM_NAME,
    version = get_iplayer_downloader.VERSION,
    description = get_iplayer_downloader.DESCRIPTION,
    long_description = get_iplayer_downloader.LONG_DESCRIPTION,
    author = get_iplayer_downloader.AUTHORS,
    author_email = get_iplayer_downloader.EMAILS,
    url = get_iplayer_downloader.URL,
    license = get_iplayer_downloader.LICENSE,
    platforms = get_iplayer_downloader.PLATFORMS,

    package_dir = {"get_iplayer_downloader": "src/get_iplayer_downloader"},
    packages = ["get_iplayer_downloader", "get_iplayer_downloader.tools",
                "get_iplayer_downloader.ui", "get_iplayer_downloader.ui.tools"],
    #packages = ["", "get_iplayer_downloader.tools", 
    #            "get_iplayer_downloader.ui", "get_iplayer_downloader.ui.tools"],

    #"ui/*.ui", "ui/*.css"
    package_data = {"get_iplayer_downloader": 
                        ["default.conf", "get_iplayer_downloader.svg", "GIT_VERSION", 
                         "ui/preferences.ui", "ui/style.css"]},

    # Moving .desktop and .svg file: for Arch Linux and Debian/Ubuntu packaging
    # Linux specific
    data_files = [("share/applications", ["res/get_iplayer_downloader.desktop"]),
                  ("share/get_iplayer_downloader/scripts", ["extra/get_iplayer_post_subdir.py"]),
                  #("share/icons/scalable/apps", ["res/get_iplayer_downloader.svg"]),
                  ("share/pixmaps", ["res/get_iplayer_downloader.svg"])],

    # Linux specific
    scripts = ["bin/get_iplayer_downloader"]
    )

#os.remove("src/get_iplayer_downloader/get_iplayer_downloader.svg")

get_iplayer_downloader.cleanup_install()
