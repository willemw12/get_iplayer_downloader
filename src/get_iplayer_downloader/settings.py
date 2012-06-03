import argparse
import os
import sys
import tempfile

# Load application-wide definitions
import get_iplayer_downloader
# "as Config": to avoid conflict with package method config() (and local variable config)
from get_iplayer_downloader.tools import config as Config

# The default config file serves as a, per property, factory setting fallback
#NOTE __file__ is not defined when run from the interpreter
DEFAULT_CONFIG_FILENAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default.conf")

if os.name == "posix":
    DEFAULT_USER_CONFIG_FILENAME = os.path.join(os.path.expanduser("~"), ".config", get_iplayer_downloader.PROGRAM_NAME, "config")
else:
    DEFAULT_USER_CONFIG_FILENAME = os.path.join(os.path.expanduser("~"), get_iplayer_downloader.PROGRAM_NAME, "config")
    
TEMP_PATHNAME = tempfile.gettempdir() + os.sep + get_iplayer_downloader.PROGRAM_NAME

#### "Stateless" utility configuration methods

def _revert_config(config):
    # Properties not defined in the user configuration file will still be created 
    # and have the default value from the default configuration file
    config.read_file(open(DEFAULT_CONFIG_FILENAME))

def _reload_config(config):
    """ Reload configuration. Create user's configuration file (copy of the default configuration file)
        if it did not exist.
    """
    config_filename = args().config[0]
    if os.path.isfile(config_filename):
        #config.read(config_filename)
        config.read_file(open(config_filename))
        
        #ALTERNATIVE read from string
        #    default_config = """
        #notify = True
        #debug-level = DEBUG
        #...
        #"""
        #config.read_file(io.BytesIO(default_config))
    else:
        _save_config(config, config_filename)

def _save_config(config, config_filename):
    if config_filename == DEFAULT_USER_CONFIG_FILENAME:
        config_pathname = os.path.dirname(config_filename)
        if not os.path.exists(config_pathname):
            os.makedirs(config_pathname)

    try:
        # Create a configuration file
        with open(config_filename, "wb") as config_file:
            config.write(config_file)
    except IOError as exc:
        sys.stderr.write("Failed to create or write to configuration file\n")
        sys.stderr.write(str(exc) + "\n")
        sys.exit(exc.errno)

def _create_args():
    #NOTE argparse() does an implicit auto-complete: --list-ch --> --list-channels
    #NOTE add_argument(): dest="clean_cache", etc. are generated automatically. "-" are replaced by "_"
    parser = argparse.ArgumentParser(description=get_iplayer_downloader.LONG_DESCRIPTION)
    parser.add_argument("-c", "--config", nargs=1, default=[DEFAULT_USER_CONFIG_FILENAME], help="configuration file, which will be created if it does not exist")
    parser.add_argument("-d", "--debug", action="store_const", const=True, default=False, help="set log level to debug")
    parser.add_argument("-l", "--log", action="store_const", const=True, default=False, help="list download log")
    parser.add_argument("-q", "--quiet", action="store_const", const=True, default=False, help="set log level to fatal")
    parser.add_argument("-v", "--verbose", action="store_const", const=True, default=False, help="set log level to info")    
    parser.add_argument("--clear-cache", action="store_const", const=True, default=False, help="delete log files and image cache files")
    parser.add_argument("--compact", action="store_const", const=True, default=False, help="used with --list-channels: remove \"BBC\" from labels")
    parser.add_argument("--full", action="store_const", const=True, default=False, help="used with --log: print detailed download log")
    parser.add_argument("--list-categories", action="store_const", const=True, default=False, help="list all available categories (key-value pairs or \"substring search term\"-\"GUI label\" pairs)")
    parser.add_argument("--list-channels", action="store_const", const=True, default=False, help="list all available channels")
    parser.add_argument("--version", action="store_const", const=True, default=False, help="print version")
    return parser.parse_args()

####

# "Alternative" initialization method
def revert():
    """ Revert configuration to the default values. """
    conf = config(load_values=False)
    _revert_config(conf)

# "Alternative" initialization method
def reload():
    """ Reload configuration from file. """
    conf = config(load_values=False)
    _reload_config(conf)

def save():
    """ Save configuration to file. """
    _save_config(config(), args().config[0])

# Convenience methods for properties that are both in _args and in _config

def get_log_level():
    """ Return the log level. """
    if args().debug:
        #level = logging.DEBUG
        level = "DEBUG"
    elif args().verbose:
        #level = logging.INFO
        level = "INFO"
    elif args().quiet:
        #level = logging.WARNING
        level = "WARNING"
    else:
        #NOTE ConfigParser already trims spaces
        level = config().get(Config.NOSECTION, "debug-level")
        if not level:
            level = None
    return level

# Convenience config methods

#def get_download_path(section):
#    # @section is ignored
#    download_path = config().get(section, "download-path")
#    if not download_path:
#        # None or empty string path
#        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
#        if not os.path.exists(download_path):
#            download_path = os.path.expanduser("~")
#    return download_path

def revert_option(section, option):
    default_value = default_config().get(section, option)
    config().set(section, option, default_value)

# Singletons

_default_config = None
_config = None
_args = None

def default_config(load_values=True):
    """ Return default configuration. """
    global _default_config
    if _default_config is None:
        # Create an empty config
        _default_config = Config.PropertiesConfigParser(allow_no_value=True)
        if load_values:
            # Load default values
            _revert_config(_default_config)
    return _default_config

def config(load_values=True):
    """ Return configuration. """
    global _config
    if _config is None:
        # Create an empty config
        _config = Config.PropertiesConfigParser(allow_no_value=True)
        if load_values:
            # Load default values and merge with values from user's configuration file
            _revert_config(_config)
            _reload_config(_config)
    return _config

def args():
    """ Return program arguments. """
    global _args
    #if _args is None:
    if not _args:
        _args = _create_args()
    return _args

####

#class Settings(object):
#    def __new__(cls, *arguments, **keywords):
#        if not hasattr(cls, '_inst'):
#            cls._inst = super(Settings, cls).__new__(cls, *arguments, **keywords)
#        return cls._inst

#class Settings(object):
#    _shared_state = { "args": _create_args(), "config": _create_init() }
#    def __new__(cls, *arguments, **keywords):
#        obj = super(Settings, cls).__new__(cls, *arguments, **keywords)
#        obj.__dict__ = cls._shared_state
#        return obj
