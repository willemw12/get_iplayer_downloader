""" Perform command utility functions. """

import shutil

from get_iplayer_downloader import settings
from get_iplayer_downloader.tools import command_log

def download_log(**keywords):
    """ Return today's download log. """
    return command_log.download_log(settings.TEMP_PATHNAME, **keywords)

def download_errors():
    """ Return the number of today's FATAL, ERROR and WARNING download log messages. """
    return command_log.download_errors(settings.TEMP_PATHNAME)

def clear_cache():
    """ Remove all temporary files (download log files and image cache files). """
    try:
        shutil.rmtree(settings.TEMP_PATHNAME)
    except OSError:
        # [Errno 2] No such file or directory: '/tmp/get_iplayer_downloader'
        pass
