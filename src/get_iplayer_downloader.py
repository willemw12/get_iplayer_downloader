#!/usr/bin/env python

import logging
import os
from datetime import datetime

from get_iplayer_downloader import settings

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
  
    from get_iplayer_downloader.ui.get_iplayer_gui import main
    main()

if __name__ == "__main__":
    main()

