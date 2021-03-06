# This file is also invoked by setup.py, which doesn't have a logger
#import logging

import os
import re
import subprocess

#logger = logging.getLogger(__name__)

# Default value (for the non-git downloaded version)
_GENERAL_VERSION = "0.2-x"

_GIT_VERSION_FILEPATH = os.path.dirname(os.path.realpath(__file__))
_GIT_DOT_DIRNAME = os.path.join(_GIT_VERSION_FILEPATH , ".git")
_GIT_VERSION_FILENAME = os.path.join(_GIT_VERSION_FILEPATH , "GIT_VERSION")

def _version():
    if os.path.exists(_GIT_VERSION_FILENAME):
        # Load the git version
        try:
            file = open(_GIT_VERSION_FILENAME, "r")
            version = file.read().strip()
            file.close()
            if version:
                return version
        except Exception: # as exc:
            #logger.warning(exc)
            pass
    else:
        # Get and save the git version, during installation or when run without being installed
        try:
            # Linux specific
            #version = subprocess.run("echo -n $(git describe --tags | head -1)", shell=True, check=True, capture_output=True).stdout
            
            version = subprocess.run("git describe --tags", shell=True, text=True, check=True, capture_output=True).stdout
            version = version.split("\n", 1)[0].lstrip()
            
            # setup.py stdb (create .deb packages): doesn't like the version to start with a non-digit character
            p = re.compile(r"(^[^0-9]+)")
            version = p.sub("", version)

            if os.path.exists(_GIT_DOT_DIRNAME):
                file = open(_GIT_VERSION_FILENAME, "w")
                file.write(version + "\n")
                file.close()
                #NOTE Sometimes version contains a fatal git error, without exception being raised
                #NOTE Version is a byte string, not a string:
                #if version and not version.startsWith("fatal") and not version.startsWith("error"):
                if version:
                    return version
        except subprocess.CalledProcessError:  # as exc:
            #logger.warning(exc)
            pass

    return _GENERAL_VERSION

#ALTERNATIVE
#try:
#    from get_iplayer_downloader import version_subst
#except ImportError:
#    pass
#else:
#    VERSION = version_subst.VERSION

def cleanup_install():
    #if os.path.exists(_GIT_VERSION_FILENAME):
    if os.path.isfile(_GIT_VERSION_FILENAME):
        os.remove(_GIT_VERSION_FILENAME)

####

# Check if called from the interpreter
#if sys.argv[0]:
#    PROGRAM_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
#else:
PROGRAM_NAME = "get_iplayer_downloader"

DESCRIPTION = "Download BBC programmes"
LONG_DESCRIPTION = "A GUI download utility for BBC get_iplayer"
VERSION = _version()
AUTHORS = "willemw"
EMAILS = "willemw12@gmail.com"
URL = "https://github.com/willemw12/get_iplayer_downloader"
LICENSE = "GPLv3"
# BSD, MacOS, Windows untested
PLATFORMS = "Linux"

####

#NOTE Logging is not fully initialized yet
#import get_iplayer_downloader.get_iplayer
#get_iplayer.check_preset_files()
