""" Perform command utility functions. """

import shutil

from get_iplayer_downloader import get_iplayer, settings
from get_iplayer_downloader.tools import command_log

#def download_log(**keywords):
#    """ Return today's download log. """
#    return command_log.download_log(settings.TEMP_PATHNAME, **keywords)

def download_log(**keywords):
    """ Return today's download log. """

    # Add some useful session log messages
    log_output = get_iplayer.precheck(quiet=True)
    if log_output:
        log_output += "\n======================================================================\n\n"
    
    log_output += command_log.download_log(settings.TEMP_PATHNAME, **keywords)

    return log_output

def download_errors():
    """ Return the number of today's FATAL, ERROR and WARNING download log messages. """
    return command_log.download_errors(settings.TEMP_PATHNAME)

def clear_cache():
    """ Remove all temporary files (download log files and image cache files). """
    #try:
    #    shutil.rmtree(settings.TEMP_PATHNAME)
    #except OSError:
    #    # [Errno 2] No such file or directory: '/tmp/get_iplayer_downloader'
    #    pass
    shutil.rmtree(settings.TEMP_PATHNAME, ignore_errors=True)
