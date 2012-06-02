#!/usr/bin/env python3

import logging
import os

from datetime import datetime

# Load application-wide definitions
import get_iplayer_downloader

from get_iplayer_downloader import command_util, config_util, settings

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

def main():
    # Exit if run from the interpreter
    #if not sys.argv[0]:
    #    sys.exit(1)

    _init_loggers()

    args = settings.args()
    #if args.list_full_labels and not args.list_channels:
    #    logger.info("--list-full-labels is only used with --list-channels")
    if args.list_categories:
        config_util.list_categories()
    elif args.list_channels:
        config_util.list_channels(compact=args.compact)
    elif args.log:
        print(command_util.download_log(full=args.full))
    elif args.clear_cache:
        command_util.clear_cache()
    elif args.version:
        print(get_iplayer_downloader.PROGRAM_NAME, get_iplayer_downloader.VERSION)
    else:
        from get_iplayer_downloader.ui.get_iplayer_gui import main
        main()

if __name__ == "__main__":
    main()

