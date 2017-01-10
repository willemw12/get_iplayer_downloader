""" Perform get_iplayer commands. """

import ast
import logging
import os

from get_iplayer_downloader import search_cache, settings
from get_iplayer_downloader.tools import command, command_queue, config, string

logger = logging.getLogger(__name__)

####

RADIO_DOWNLOAD_PATH = settings.get_config().get("radio", "download-path")
TV_DOWNLOAD_PATH = settings.get_config().get("tv", "download-path")

# Labels for disabled filters
ALL_CATEGORIES_LABEL = "Categories"
ALL_CHANNELS_LABEL = "Channels"
SINCE_FOREVER_LABEL = "Since"

# Indices of a key-value pair
KEY_INDEX = 0
VALUE_INDEX = 1

####

_GET_IPLAYER_PROG = "get_iplayer"

#_SINCE_HOUR_MARGIN = 6
_SINCE_HOUR_MARGIN = string.str2int(settings.get_config().get(config.NOSECTION, "since-margin-hours", fallback=6))

_COMPACT_TOOLBAR = string.str2bool(settings.get_config().get(config.NOSECTION, "compact-tool-bar"))
_ALL_CATEGORIES_LABEL = ALL_CATEGORIES_LABEL if _COMPACT_TOOLBAR else ""
_ALL_CHANNELS_LABEL = ALL_CHANNELS_LABEL if _COMPACT_TOOLBAR else ""
_SINCE_FOREVER_LABEL = SINCE_FOREVER_LABEL if _COMPACT_TOOLBAR else ""
#_SINCE_FUTURE_LABEL = "Future"

####

# List of key-value pairs
#SINCE_LIST = [[0, _SINCE_FOREVER_LABEL], [1, _SINCE_FUTURE_LABEL],
SINCE_LIST = [[0, _SINCE_FOREVER_LABEL],
#              [  4, "4 hours"], [8, "8 hours"], [12, "12 hours"], [16, "16 hours"], [20, "20 hours"],
#              [ 24 + _SINCE_HOUR_MARGIN, "1 day" ],  [ 48 + _SINCE_HOUR_MARGIN, "2 days"],
              [  2, "2 hours"],  [  4, "4 hours"],  [6, "6 hours"],  [8, "8 hours"], [10, "10 hours"], 
              [ 12, "12 hours"], [14, "14 hours"], [16, "16 hours"], [18, "18 hours"], [20, "20 hours"],
              [ 24 + _SINCE_HOUR_MARGIN, "1 day" ],  [ 48 + _SINCE_HOUR_MARGIN, "2 days"],
              [ 72 + _SINCE_HOUR_MARGIN, "3 days"],  [ 96 + _SINCE_HOUR_MARGIN, "4 days"],
              [120 + _SINCE_HOUR_MARGIN, "5 days"],  [144 + _SINCE_HOUR_MARGIN, "6 days"],
              [168 + _SINCE_HOUR_MARGIN, "7 days"]]

#30 DAYS EPISODE AVAILABILITY
#SINCE_LIST = [[0, _SINCE_FOREVER_LABEL],
#              [  4, "4 hours"], [8, "8 hours"], [12, "12 hours"], [16, "16 hours"], [20, "20 hours"],
#              [ 24 + _SINCE_HOUR_MARGIN, "1 day" ],  [ 48 + _SINCE_HOUR_MARGIN, "2 days"],
#              [ 72 + _SINCE_HOUR_MARGIN, "3 days"],  [ 96 + _SINCE_HOUR_MARGIN, "4 days"],
#              [120 + _SINCE_HOUR_MARGIN, "5 days"],  [144 + _SINCE_HOUR_MARGIN, "6 days"],
#              [168 + _SINCE_HOUR_MARGIN, "1 week"],  [336 + _SINCE_HOUR_MARGIN, "2 weeks"],
#              [504 + _SINCE_HOUR_MARGIN, "3 weeks"], [672 + _SINCE_HOUR_MARGIN, "4 weeks"]]

class Preset:
    # "preset-file": filename in folder ~/.get_iplayer/presets
    RADIO = settings.get_config().get("radio", "preset-file")
    TV = settings.get_config().get("tv", "preset-file")
    
class ProgType:
    ##ALL = "all"
    #ALL = "radio,podcast,tv"
    RADIO = "radio"
    PODCAST = "podcast"
    TV = "tv"
    CH4 = "ch4"
    ITV = "itv"

####

# List of key-value pairs
#NOTE Cannot extend a constant list: RADIO = [[None, "Genre"]].extend(...)
#WORKAROUND see get_iplayer_gui.py (at least in Python 2.7)
#  RADIO = [[None, "Genre"]]    -->    #RADIO = [["", "Genre"]]

class Channels:
    RADIO = _ALL_CHANNELS_LABEL + "," + settings.get_config().get("radio", "channels")
    TV = _ALL_CHANNELS_LABEL + "," + settings.get_config().get("tv", "channels")
    CH4 = _ALL_CHANNELS_LABEL
    ITV = _ALL_CHANNELS_LABEL

class Categories:
    #@staticmethod
    def _merge_keys(key_value_list):
        key_list = [row[KEY_INDEX] for row in key_value_list]
        keys = ""
        for i, key in enumerate(key_list):
            #if i == 0 or not key:
            if not key:
                # Skip predefined or user-defined "all" filters
                continue
            keys += key
            if (i < len(key_list) - 1):
                keys += ","
                
        # Use set to avoid duplicates
        key_set = set(keys.split(","))
        keys = ",".join(key_set)
        
        return keys
    
    # No filter list
    ALL = [["", _ALL_CATEGORIES_LABEL]]

    # The filter lists below consists of all categories in the first item, followed by the categories separately
    
    RADIO = ast.literal_eval(settings.get_config().get("radio", "categories-radio"))
    # Prepend
    RADIO.insert(0, [_merge_keys(RADIO), _ALL_CATEGORIES_LABEL])
    
    PODCAST = ast.literal_eval(settings.get_config().get("radio", "categories-podcast"))
    # Prepend
    PODCAST.insert(0, [_merge_keys(PODCAST), _ALL_CATEGORIES_LABEL])
    
    TV = ast.literal_eval(settings.get_config().get("tv", "categories"))
    # Prepend
    TV.insert(0, [_merge_keys(TV), _ALL_CATEGORIES_LABEL])

####

class SinceListIndex:
    FOREVER = 0
    #FUTURE = 1

    #30 DAYS EPISODE AVAILABILITY
    ## Initial podcast since filter index (1 week) in the SINCE_LIST
    #PODCAST_DEFAULT = 12

class SearchResultColumn:
    DOWNLOAD = 0
    PID = 1
    INDEX = 2
    SERIES = 3
    EPISODE = 4
    CATEGORIES = 5
    CHANNELS = 6
    THUMBNAIL_SMALL = 7
    AVAILABLE = 8
    DURATION = 9
    
    # Additional data derived from fields above in this class
    LOCATE_SEARCH_TERM = 10

####

def precheck(quiet=False):
    log_output = ""
    
    # Check required program(s)
    # Call get_iplayer directly, instead of wrapping it in "shell code", to check whether it is installed or not    
    process_output =  command.run(_GET_IPLAYER_PROG + " --usage", quiet=True, temp_pathname=settings.TEMP_PATHNAME)
    #TODO not Linux specific ("not found")
    if quiet and "not found" in process_output:
        # command.run() already logs the error (logger.warning())
        log_output += "WARNING:{0}".format(process_output)
        
    # Check get_iplayer preset files
    if not string.str2bool(settings.get_config().get(config.NOSECTION, "disable-presets")):
        pathname = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        for preset in [Preset.RADIO, Preset.TV]:
            filename = os.path.join(pathname, preset)
            if not os.path.exists(filename):
                msg = "preset file {0} does not exist".format(filename)
                logger.warning(msg)
                log_output += "WARNING:{0}".format(msg)

    return log_output

#NOTE Logging is not fully initialized yet
#check_preset_files()

####

def categories(search_text, preset=None, prog_type=None):
    """ Run get_iplayer --list=categories.
        Return table with columns: categories, categories (key-value pair).
    """
    
    cmd = _GET_IPLAYER_PROG
    if preset:
        cmd += " --preset=" + preset
    if prog_type:
        cmd += " --type=" + prog_type
    cmd += " --list=categories --nocopyright"
    if search_text:
        cmd += " \"" + search_text + "\""
    
    process_output = command.run(cmd, quiet=True)

    lines = process_output.splitlines()
    output_lines = []
    for line in lines:
        # Skip empty or message lines
        if line and line[0] and not line.startswith("INFO:") and not line.startswith("Matches:"):
            # Strip the count number from the categories name
            categories_key = line.rsplit(" ", 1)[0].rstrip()
            categories_value = categories_key
            output_lines.append([categories_key, categories_value])

    return output_lines

def channels(search_text, preset=None, prog_type=None, compact=False):
    """ Run get_iplayer --list=channel. @compact is False: strip leading "BBC " substring.
        Return comma-separated list of channels.
    """
    
    cmd = _GET_IPLAYER_PROG
    if preset:
        cmd += " --preset=" + preset
    if prog_type:
        cmd += " --type=" + prog_type
    cmd += " --list=channel --nocopyright"
    if search_text:
        cmd += " \"" + search_text + "\""
    
    process_output = command.run(cmd, quiet=True)

    lines = process_output.splitlines()
    first_value = True
    output_line = ""
    for line in lines:
        # Skip empty or message lines
        if line and line[0] and not line.startswith("INFO:") and not line.startswith("Matches:"):
            if first_value:
                first_value = False
            else:
                output_line += ","
            if compact and line.startswith("BBC "):
                # Remove leading "BBC " substring
                line = line[len("BBC "):]
            # Strip the count number from the channel name
            output_line += line.rsplit(" ", 1)[0].rstrip()

    return output_line

def search(search_text, preset=None, prog_type=None,
           channels=None, exclude_channels=None,
           categories=None, exclude_categories=None,
           since=0, future=False):
    """ Run get_iplayer (--search).
        Return search result in a table with columns listed in SearchResultColumn.
        If cached search results are present, return that instead.
    """

    output_lines = search_cache.get(prog_type)
    if output_lines is not None:
        # Skip 'get_iplayer --search' when search results have been cached
        return output_lines

    ####

    # PERL_UNICODE=S : avoid "Wide character in print" warning/error messages
    #cmd = _GET_IPLAYER_PROG
    cmd = "PERL_UNICODE=S " + _GET_IPLAYER_PROG
    #if not preset:
    #    #cmd += " --type=all"
    #    cmd += " --type=" + ProgType.ALL
    #else:
    if preset:
        cmd += " --preset=" + preset
    if prog_type:
        cmd += " --type=" + prog_type
    if channels:
        cmd += " --channel=\"" + channels + "\""
    if exclude_channels:
        cmd += " --exclude-channel=\"" + exclude_channels + "\""
    if categories:
        cmd += " --category=\"" + categories + "\""
    if exclude_categories:
        cmd += " --exclude-category=\"" + exclude_categories + "\""
    if since:
        cmd += " --since=" + str(since)
    if future:
        cmd += " --future"
    cmd += " --listformat=\"<pid>|<index>|<name>|<episode> ~ <desc>|<categories>|<channel>|<thumbnail>|<available>|<duration>\""
    # --fields: perform the same search as with "--long" plus on "pid"
    cmd += " --fields=\"name,episode,desc,pid\" --nocopyright"
    if search_text:
        # Simple exclude search option
        if search_text.startswith("-"):
            cmd += " --exclude=\"" + search_text[1:] + "\""
        else:
            cmd += " \"" + search_text + "\""
    
    process_output = command.run(cmd)

    # Convert the process output lines directly to lists, matching the GtkTreeStore model data. Do not create intermediate data/interfaces
    lines = process_output.splitlines()
    output_lines = []
    title_prev = None
    level = 0
    copy = False
    for line in lines:
        if not "|" in line:
            # Skip (log) message lines
            continue;

        #NOTE with "def __len__()" in a metaclass: l = line.split("|", len(SearchResultColumn) - 1)
        l = line.split("|", 11 - 1)     # , len(SearchResultColumn) - 1)

        # Make sure the line array contains at least 11 items (avoid IndexError exception)
        # This better than catching IndexError exceptions below, which currently will discard the whole episode line
        # TODO sanitize process_output.
        #      An episode description sometimes contain a newline character or a | character.
        #      Split() will only split the first line
        for unused in range(len(l), 11):     # , len(SearchResultColumn.attributes))
            l.extend([''])
        #ALTERNATIVE catch exceptions 

        # Skip empty lines
        if l[0]:
            # Match string containing only spaces
            #ALTERNATIVE
            #1) all(c in " " for c in l)
            #2) p = re.compile('[ -]+$'); p.match(l)
            #3) re.match("^[ ]+$", l)
            if level == 0 and l[2] != title_prev:
                # Going from series level (parent/root/level 0) to episode level (child/leave/level 1)
                level = 1
                copy = True
#                if title_prev:
                # Add series line
                try:
                    output_lines.append([False, None, None, l[2], None, l[4], l[5], l[6], l[7], l[8], l[2]])
                except IndexError:    # as exc:
                    pass
            elif level == 1 and l[2] != title_prev:
               # Going from episode level (child/leave/level 1) to series level (parent/root/level 0)
               level = 0
               copy = False

            if level == 1 and copy:
                # Add an episode line
                try:
                    if l[3].startswith(" ~ "):
                        # No episode title
                        output_lines.append([False, l[0], l[1], None, l[3][len(" ~ "):], l[4], l[5], l[6], l[7], l[8], None])
                    elif l[3].endswith(" ~ "):
                        # No episode description
                        output_lines.append([False, l[0], l[1], None, l[3][:len(l[3])-len(" ~ ")], l[4], l[5], l[6], l[7], l[8], None])
                    else:
                        output_lines.append([False, l[0], l[1], None, l[3], l[4], l[5], l[6], l[7], l[8], None])
                except IndexError:    # as exc:
                    pass

            title_prev = l[2]

    return output_lines

def get(search_term_list, pid=True, pvr_queue=False, preset=None, prog_type=None,
        alt_recording_mode=False, dry_run=False, force=False, output_path=None,
        categories=None, future=False):
    """ Run get_iplayer --get, get_iplayer --pid or get_iplayer --pvrqueue.
        If @pid is true, then @search_term_list contains pids.
        Return tuple: launched boolean, process output string.
    """
    
    if preset == Preset.RADIO:
        output_path = RADIO_DOWNLOAD_PATH
    elif preset == Preset.TV:
        output_path = TV_DOWNLOAD_PATH
    else:
        output_path = None
        
    #WORKAROUND Preset can be None: disable-presets is true AND data models and configuration are based on presets, not on programme types
    #if preset and string.str2bool(settings.get_config().get(preset, "run-in-terminal")):
    #    terminal_prog = settings.get_config().get(config.NOSECTION, "terminal-emulator")
    #else:
    #    terminal_prog = None
    preset_fallback = None
    if preset:
        preset_fallback = preset
    else:
        # Determine preset from programme type
        if prog_type == ProgType.RADIO or prog_type == ProgType.PODCAST:
            preset_fallback = Preset.RADIO
        elif prog_type == ProgType.TV:
            preset_fallback = Preset.RADIO
    if prog_type and string.str2bool(settings.get_config().get(preset_fallback, "run-in-terminal")):
            terminal_prog = settings.get_config().get(config.NOSECTION, "terminal-emulator")
    else:
        terminal_prog = None

    if alt_recording_mode:
        if prog_type == ProgType.CH4:
            alt_radio_modes = ""
            alt_tv_modes = "flashnormal"
        elif prog_type == ProgType.ITV:
            alt_radio_modes = ""
            alt_tv_modes = "itvnormal,itvhigh,itvlow"
        else:
            alt_radio_modes = settings.get_config().get(Preset.RADIO, "recording-modes")
            alt_tv_modes = settings.get_config().get(Preset.TV, "recording-modes")
    
    #cmd = "( for i in"
    #for search_term_row in search_term_list:
    #    cmd += " " + search_term_row[SearchTermColumn.PID_OR_INDEX]
    #cmd += "; do " + _GET_IPLAYER_PROG
    cmd = ""
    for i, search_term in enumerate(search_term_list):
        cmd += _GET_IPLAYER_PROG + " --hash"
        if preset:
            cmd += " --preset=" + preset
        #WORKAROUND Preset can be None: disable-presets is true AND models and configuration are based on presets, not on programme types
        #    if alt_recording_mode:
        #        if preset == Preset.RADIO and alt_radio_modes:
        #            #cmd += " --modes=\"" + alt_radio_modes + "\""
        #            cmd += " --radiomode=\"" + alt_radio_modes + "\""
        #        elif preset == Preset.TV and alt_tv_modes:
        #            #cmd += " --modes=\"" + alt_tv_modes + "\""
        #            cmd += " --tvmode=\"" + alt_tv_modes + "\""
        if alt_recording_mode:
            if preset_fallback == Preset.RADIO and alt_radio_modes:
                #cmd += " --modes=\"" + alt_radio_modes + "\""
                cmd += " --radiomode=\"" + alt_radio_modes + "\""
            elif preset_fallback == Preset.TV and alt_tv_modes:
                #cmd += " --modes=\"" + alt_tv_modes + "\""
                cmd += " --tvmode=\"" + alt_tv_modes + "\""

        if prog_type:
            cmd += " --type=" + prog_type
        cmd += " --nocopyright"
        if force:
            cmd += " --force --overwrite"
        if output_path:
            cmd += " --output=\"" + output_path + "\""
    
        #if pvr_queue or future:
        if pvr_queue:
            if not preset:
                return False
            # Must explicitly specify programme type and PID on the command line when in pvr queue mode
            cmd += " --pvrqueue --pid="
            #cmd += " --pvr-exclude=" + ",".join(exclude_search_term_list)
        elif pid:
            cmd += " --pid="
        else:
            cmd += " --get "        
        ##cmd += "\"$i\" ; done"
        #cmd += "$i; done )"
        if search_term:
            #TEMP if search_term is a PID and the PID is numeric,
            #     then add a leading non-digit character to the PID
            #     so that get_iplayer will not assume the search_term to be an index
            if " " not in search_term and prog_type in [Channels.CH4, Channels.ITV]:
                search_term = " " + search_term

            # search_term_list could be a set of episode indices, so don't surround them with quotes
            cmd += search_term
        
        if (i < len(search_term_list) - 1):
            #cmd += "; "
            cmd += "; echo '----'; "

    if pvr_queue or dry_run:
        launched = True
        process_output = command.run(cmd, dry_run=dry_run, temp_pathname=settings.TEMP_PATHNAME)
    else:
        #CommandQueue.CommandQueue().run(...)
        launched = command_queue.run(cmd, temp_pathname=settings.TEMP_PATHNAME,
                                     terminal_prog=terminal_prog, terminal_title="get_iplayer get")
        process_output = None

    return (launched, process_output)

def info(pid, search_term, preset=None, prog_type=None, proxy_disabled=False, future=False):
    """ Run 'get_iplayer --info [--pid=<pid>] [<search term>]'.
        Return table with columns: series title, episode title plus description.
    """
    
    #if not pid:
    #    return ""
    
    # Only useful from outside the UK:
    #     If proxy_disabled is true then info retrieval may be faster but the info 
    #     will not contain proper values for "modes" and "tvmodes" (the available TV download file sizes)

    cmd = _GET_IPLAYER_PROG + " --info"
    if preset:
        cmd += " --preset=" + preset
    if prog_type:
        cmd += " --type=" + prog_type
    if proxy_disabled:
        cmd += " --proxy=0"
    if future:
        cmd += " --future"
    cmd += " --nocopyright"
    # index size 4 (width 512)
    cmd += " --thumbsizecache=5"
    
    # --fields: perform the same search as with --long plus on PID
    #cmd += " --fields=\"name,episode,desc,pid\"
    cmd += " --pid=" + pid
    if search_term:
        cmd += " --long" + " \"" + search_term + "\""

    process_output = command.run(cmd)

    lines = process_output.splitlines()
    output_lines = []
    for line in lines:
        # Skip empty or message lines
        if line and line[0] and not line.startswith("INFO:") and not line.startswith("Matches:"):
            l = line.split(":", 1)
            # Match key-value pairs
            if len(l) == 2 and l[1]:
                output_lines.append([l[0], l[1].lstrip()])

    return output_lines

def refresh(preset=None, prog_type=None, channels=None, exclude_channels=None, force=False, future=False):
    """ Run get_iplayer --refresh. Return error code. """

    if search_cache.has_cache(prog_type):
        # Skip 'get_iplayer --refresh' when search results have been cached
        return

    ####
    
    #if not preset:
    #    #preset = Preset.RADIO + "," + Preset.TV
    #    preset = "all"

    cmd = _GET_IPLAYER_PROG + " --refresh"
    if future:
        cmd += " --refresh-future"
    if channels:
        #cmd += " --channel=\"" + channel + "\""
        cmd += " --refresh-include=\"" + channels + "\""
    if exclude_channels:
        #cmd += " --exclude-channel=\"" + exclude_channel + "\""
        cmd += " --refresh-exclude=\"" + exclude_channels + "\""
    #if preset:
    #    cmd += " --preset=" + preset
    if prog_type:
        cmd += " --type=" + prog_type
    if force:
        cmd += " --force"
    cmd += " --nocopyright"
    
    if preset is None:
        ret1 = command.run(cmd + " --preset=" + Preset.RADIO, temp_pathname=settings.TEMP_PATHNAME)
        ret2 = command.run(cmd + " --preset=" + Preset.TV, temp_pathname=settings.TEMP_PATHNAME)
        return ret2 if ret2 != 0 else ret1
    else:
        return command.run(cmd + " --preset=" + preset)

