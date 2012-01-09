import argparse
import os
import tempfile

# Application-wide constants
import common

# "as Config": avoid conflict with package method config() (and local variable config)
from get_iplayer_downloader.tools import config as Config

CONFIG_FILENAME = os.path.join(os.path.expanduser("~"), ".config", common.__program_name__, "config")
TEMP_FILEPATH = tempfile.gettempdir() + os.sep + common.__program_name__

#### "Stateless" util configuration methods

def _revert_config(config):
    #NOTE __file__ is not defined when run from the interpreter
    current_resource_pathname = os.path.dirname(os.path.realpath(__file__))

    #NOTE default_config_filename serves as factory setting fallback per property
    default_config_filename = current_resource_pathname + os.sep + "default.config"

    #NOTE properties not defined in the configuration file will still be created and have the default value
    #     from the default configuration file
    config.readfp(open(default_config_filename))

def _reload_config(config):
    """ Reload configuration. Create user's configuration file (copy of the default configuration file)
        if it did not exist 
    """
    if os.path.isfile(CONFIG_FILENAME):
        #config.read(CONFIG_FILENAME)
        config.readfp(open(CONFIG_FILENAME))
        
        #ALTERNATIVE read from string
        #    default_config = """
        #notify = True
        #debug-level = DEBUG
        #...
        #"""
        #config.readfp(io.BytesIO(default_config))
    else:
        _save_config(config, CONFIG_FILENAME)

def _save_config(config, config_filename):
    config_pathname = os.path.dirname(config_filename)
    if not os.path.exists(config_pathname):
        os.makedirs(config_pathname)
    
    # Create a configuration file for the user
    with open(config_filename, "wb") as config_file:
        config.write(config_file)    

def _create_args():
    parser = argparse.ArgumentParser(description=common.__long_description__)
    parser.add_argument("-d", "--debug", dest="debug", action="store_const", const=True, default=False, help="enable debug log level")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="enable info log level")    
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
    _save_config(config(), CONFIG_FILENAME)

# Convenience methods for properties that are both in _args and in _config

def get_log_level():
    """ Return the log level. """
    if args().debug:
        #level = logging.DEBUG
        level = "DEBUG"
    elif args().verbose:
        #level = logging.INFO
        level = "INFO"
    else:
        #TODO test not exist, empty: return None in that case.
        #NOTE ConfigParser already trims spaces
        level = config().get(Config.NOSECTION, "debug-level")
        if not level:
            # Else level is None: default level logging.WARNING
            level = None
    return level

####

# Singletons
_config = None
_args = None

def config(load_values=True):
    """ Return configuration object. """
    global _config
    #if _config is None:
    if not _config:
        # Create an empty config
        _config = Config.PropertiesConfigParser(allow_no_value=True)
        if load_values:
            # Load default values and merge with values from user's configuration file
            _revert_config(_config)
            _reload_config(_config)
    return _config

def args():
    """ Return program arguments object. """
    global _args
    #if _args is None:
    if not _args:
        _args = _create_args()
    return _args

