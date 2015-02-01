import json
import os
import sys

from datetime import datetime

# Load application-wide definitions
import get_iplayer_downloader

TIMESTAMP_DATETIME_FORMAT = "%Y%m%d%H%M%S"

if os.name == "posix":
    DEFAULT_USER_CACHE_FILENAME = os.path.join(os.path.expanduser("~"), ".cache", get_iplayer_downloader.PROGRAM_NAME, "cache.json")
else:
    DEFAULT_USER_CACHE_FILENAME = os.path.join(os.path.expanduser("~"), get_iplayer_downloader.PROGRAM_NAME, "cache.json")

DEFAULT_CACHE = dict(last_visit_time="")

# Singleton
_cache = None

def get_cache():
    """ Return cache. """
    global _cache
    if _cache is None:
        try:
            cache_filename = DEFAULT_USER_CACHE_FILENAME
            with open(cache_filename, "r") as cache_file:
                _cache = json.load(cache_file)
        #except Exception as exc:
        except OSError as exc:
            #sys.stderr.write("First run or failed to load cache file\n")
            #sys.stderr.write(str(exc) + "\n")
            _cache = DEFAULT_CACHE
        except ValueError as exc:
            sys.stderr.write("Invalid cache file\n")
            sys.stderr.write(str(exc) + "\n")
            _cache = DEFAULT_CACHE
    return _cache

def reload_cache():
    _cache = None
    return get_cache()

def save_cache():
    """ Save cache to file. """
    cache_filename = DEFAULT_USER_CACHE_FILENAME
    cache_pathname = os.path.dirname(cache_filename)
    if not os.path.exists(cache_pathname):
        os.makedirs(cache_pathname)

    try:
        with open(cache_filename, "w") as cache_file:
            #json.dump(_cache, cache_file)
            json.dump(_cache, cache_file, sort_keys=True, indent=4)
    except Exception as exc:
        sys.stderr.write("Failed to create or write to cache file\n")
        sys.stderr.write(str(exc) + "\n")
        sys.exit(exc.errno)

# Convenience cache methods

def get_last_visit_time():
    """ Return datetime object. """
    cache = get_cache()
    try:
        timestamp = cache["last_visit_time"]
        return datetime.strptime(timestamp, TIMESTAMP_DATETIME_FORMAT)
    #except ValueError:
    #except KeyError:
    except Exception:
        return None
    
def save_last_visit_time():
    """ Save current datetime. """
    timestamp = datetime.now().strftime(TIMESTAMP_DATETIME_FORMAT)
    
    #cache = get_cache()
    cache = reload_cache()
    cache["last_visit_time"] = timestamp
    save_cache()
