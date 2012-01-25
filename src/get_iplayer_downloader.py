#!/usr/bin/env python

import logging
import os
from datetime import datetime

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

def print_categories():
    get_iplayer.refresh()

    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO)
    print "[radio]"
    print "categories-radio =", categories
    print

    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.PODCAST)
    print "categories-podcast =", categories
    print
    
    categories = get_iplayer.categories("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV)
    print "[tv]"
    print "categories =", categories

def print_channels():
    get_iplayer.refresh()

    channels = get_iplayer.channels("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO + "," + get_iplayer.ProgType.PODCAST)
    print "[radio]"
    print "channels =", channels
    print

    channels = get_iplayer.channels("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV)
    print "[tv]"
    print "channels =", channels

def main():
    # Exit if run from the interpreter
    #if not sys.argv[0]:
    #    sys.exit(1)

    _init_loggers()

    if settings.args().print_categories or settings.args().print_channels:
        if settings.args().print_categories:
            print_categories()
        else:
            print_channels()
    else:
        from get_iplayer_downloader.ui.get_iplayer_gui import main
        main()

if __name__ == "__main__":
    main()

