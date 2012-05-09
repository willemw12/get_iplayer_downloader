#!/usr/bin/env python

import logging
import os
import shutil

from datetime import datetime

# Load application-wide definitions
import get_iplayer_downloader

from get_iplayer_downloader import get_iplayer, settings

def _init_loggers():
    level = settings.get_log_level()
    logging.basicConfig(level=level)
    #root_logger = logging.getLogger()

    # Log to file
    if not os.path.exists(settings.TEMP_PATHNAME):
        os.mkdir(settings.TEMP_PATHNAME)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    #ALTERNATIVE timestamp/number generation: 
    #    pid = str(os.getpgid(0)), Linux specific; datetime.now().strftime("%s"); mkstemp()
    log_filename = os.path.join(settings.TEMP_PATHNAME, timestamp + ".log")
    handler = logging.FileHandler(log_filename)
    logging.getLogger().addHandler(handler)

def list_categories(long_labels):
    get_iplayer.refresh()

    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO, 
                                        long_labels=long_labels)
    print "[radio]"
    print
    print "categories-radio =", categories
    print

    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.PODCAST, 
                                        long_labels=long_labels)
    print "categories-podcast =", categories
    print
    
    categories = get_iplayer.categories("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV, 
                                        long_labels=long_labels)
    print "[tv]"
    print
    print "categories =", categories

def list_channels():
    get_iplayer.refresh()

    channels = get_iplayer.channels("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO + "," + get_iplayer.ProgType.PODCAST)
    print "[radio]"
    print "channels =", channels
    print

    channels = get_iplayer.channels("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV)
    print "[tv]"
    print "channels =", channels

def clear_cache():
    shutil.rmtree(settings.TEMP_PATHNAME)
    
def main():
    # Exit if run from the interpreter
    #if not sys.argv[0]:
    #    sys.exit(1)

    _init_loggers()

    if settings.args().list_categories:
        list_categories(settings.args().list_long_labels)
    elif settings.args().list_channels:
        list_channels()
    elif settings.args().clear_cache:
        clear_cache()
    elif settings.args().version:
        print get_iplayer_downloader.PROGRAM_NAME, get_iplayer_downloader.VERSION
    else:
        from get_iplayer_downloader.ui.get_iplayer_gui import main
        main()

if __name__ == "__main__":
    main()

