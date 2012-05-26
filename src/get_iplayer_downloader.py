#!/usr/bin/env python3

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

def list_categories():
    # Avoid refresh messages in the print statements below
    get_iplayer.refresh()
    print()

    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.PODCAST)
    print("[radio]")
    print("categories-podcast =", categories)
    
    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO)
    print("categories-radio =", categories)
    print()

    categories = get_iplayer.categories("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV)
    print("[tv]")
    print("categories =", categories)

def list_channels(full_labels):
    # Avoid refresh messages in the print statements below
    get_iplayer.refresh()
    print()

    channels = get_iplayer.channels("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO + "," + get_iplayer.ProgType.PODCAST, 
                                    full_labels=full_labels)
    print("[radio]")
    print("channels =", channels)
    print()

    channels = get_iplayer.channels("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV, 
                                    full_labels=full_labels)
    print("[tv]")
    print("channels =", channels)

def clear_cache():
    shutil.rmtree(settings.TEMP_PATHNAME)
    
def main():
    # Exit if run from the interpreter
    #if not sys.argv[0]:
    #    sys.exit(1)

    _init_loggers()

    args = settings.args()
    #if args.list_full_labels and not args.list_channels:
    #    logger.info("--list-full-labels is only used with --list-channels")
    if args.list_categories:
        list_categories()
    elif args.list_channels:
        list_channels(args.list_full_labels)
    elif args.clear_cache:
        clear_cache()
    elif args.version:
        print(get_iplayer_downloader.PROGRAM_NAME, get_iplayer_downloader.VERSION)
    else:
        from get_iplayer_downloader.ui.get_iplayer_gui import main
        main()

if __name__ == "__main__":
    main()

