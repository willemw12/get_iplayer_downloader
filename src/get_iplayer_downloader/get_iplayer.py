""" Perform get_iplayer operations. """

import ast
import logging
from datetime import datetime

from get_iplayer_downloader import common, settings
from get_iplayer_downloader.tools import command, command_queue, config, string

RADIO_DOWNLOAD_PATH = settings.config().get("radio", "download-path")
TV_DOWNLOAD_PATH = settings.config().get("tv", "download-path")

# Index of a key-value pair
KEY_INDEX = 0

_GET_IPLAYER_PROG = "get_iplayer"
_TERMINAL_PROG = settings.config().get(config.NOSECTION, "terminal-emulator")

# List of key-value pairs
SINCE_LIST = [[0, "Since"], [4, "4 hours"], [8, "8 hours"], [12, "12 hours"],
              [24, "1 day"], [48, "2 days"], [72, "3 days"], [96, "4 days"],
              [120, "5 days"], [144, "6 days"], [168, "7 days"]]

class Preset:
    # preset-file: filename in folder ~/.get_iplayer/presets
    RADIO = settings.config().get("radio", "preset-file")
    TV = settings.config().get("tv", "preset-file")
    
class ProgType:
    #ALL = "all"
    RADIO = "radio"
    PODCAST = "podcast"
    TV = "tv"
    
class Channel:
    RADIO = settings.config().get("radio", "channels")
    TV = settings.config().get("tv", "channels")

class Category:
    # List of key-value pairs
    
    #NOTE doesn't work: RADIO = [[None, "Genre"]].extend(...)

    #WORKAROUND see get_iplayer_gui.py
    #RADIO = [[None, "Genre"]]
    RADIO = [["", "Genre"]]
    RADIO.extend(ast.literal_eval(settings.config().get("radio", "categories")))
    
    #WORKAROUND see get_iplayer_gui.py
    #TV = [[None, "Genre"]]
    TV = [["", "Genre"]]
    TV.extend(ast.literal_eval(settings.config().get("tv", "categories")))

class SearchResultColumn:
    DOWNLOAD = 0
    PID = 1
    INDEX = 2
    SERIE = 3
    EPISODE = 4

def search(search_text, preset=None, prog_type=None, channel=None, category=None, since=0, search_all=False):
    """ Run get_iplayer (--search).
        Return table with columns: download (False), followed by columns listed in SearchResultColumn.
    """
    cmd = _GET_IPLAYER_PROG
    if preset:
        cmd += " --preset=" + preset
    if search_all:
        cmd += " --type=all"
    elif prog_type:
        cmd += " --type=" + prog_type
    if not search_all and channel:
        cmd += " --channel=\"" + channel + "\""
    if category:
        cmd += " --category=\"" + category + "\""
    if since:
        cmd += " --since=" + str(since)
    cmd += " --long --nocopyright --listformat=\"|<pid>|<index>|<episode> ~ <desc>\" --tree"
    if search_text:
        cmd += " \"" + search_text + "\""
    
    process_output = command.run(cmd, temp_pathname=settings.TEMP_PATHNAME)

    # Convert the process output lines to lists (no dicts, no objects), matching the GtkTreeStore input data
    lines = process_output.splitlines()
    output_lines = []
    l_prev = None
    level = 0
    copy = False
    for line in lines:
        l = line.split("|", 3)
        # Skip empty lines
        if l[0]:
            # Match string containing only spaces
            #ALTERNATIVE
            #1) all(c in " " for c in l)
            #2) CHECK_RE = re.compile('[ -]+$'); CHECK_RE.match(l)
            #3) re.match("^[ ]+$", l)
            if level == 0 and l[0].isspace():
                # Going from root level (0, a serie) to level 1 (an episode)
                level = 1
                copy = True
                if l_prev:
                    # Add serie line. Serie title from the previous line, the parent of the current line
                    # No pid or index available for a serie from the output of get_iplayer --tree
                    output_lines.append([False, None, None, l_prev[0], None])
            if level == 1 and not l[0].isspace():
                # Going from level 1 (an episode) to root level (0, a serie)
                level = 0
                copy = False
            #if level == 1 and copy:
            if copy:
                # Add an episode line. Episode title and description from the current line
                if l[3].startswith("- ~ "):
                    # No episode title
                    output_lines.append([False, l[1], l[2], None, string.decode(l[3][4:])])
                else:
                    output_lines.append([False, l[1], l[2], None, string.decode(l[3])])
            l_prev = l

    return output_lines

def get(search_term_list, pid=True, pvr_queue=False, preset=None, hd_tv_mode=False, force_download=False, output_path=None):
    """ Run get_iplayer --get, get_iplayer --pid or get_iplayer --pvrqueue.
        Return table with columns: download (False), followed by columns listed in SearchResultColumn.
    """
    if preset == Preset.RADIO:
        output_path = RADIO_DOWNLOAD_PATH
    elif preset == Preset.TV:
        output_path = TV_DOWNLOAD_PATH

    subdir_format = settings.config().get(preset, "subdir-format").lower()
    if subdir_format:
        # Perform additional substitutions
        #NOTE find substring
        if "week" in subdir_format:
            week_number = datetime.today().isocalendar()[1]
            subdir_format = subdir_format.replace("<week>", "{0:02}".format(week_number))
    run_in_terminal_window = string.str2bool(preset and settings.config().get(preset, "run-in-terminal"))

    #cmd = "( for i in"
    #for search_term in search_term_list:
    #    cmd += " " + search_term
    #cmd += "; do " + _GET_IPLAYER_PROG
    cmd = ""
    for i, search_term in enumerate(search_term_list):
        cmd += _GET_IPLAYER_PROG
        
        if preset:
            cmd += " --preset=" + preset
            if hd_tv_mode and preset == Preset.TV:
                cmd += " --tvmode=\"" + settings.config().get(preset, "hd-mode") + "\""
        if force_download:
            cmd += " --force"
        cmd += " --nocopyright --hash --output=\"" + output_path + "\""
        if subdir_format:
            if pvr_queue:
                cmd += " --subdir --subdir-format=\"" + subdir_format + "\""
            else:
                cmd += " --subdir --subdir-format=\\\"" + subdir_format + "\\\""
        if pvr_queue:
            if not preset:
                return False
            # Output will be displayed in a dialog window
            run_in_terminal_window = False
            # Must explicitly specify type and pid on the command line
            cmd += " --pvrqueue --type " + preset + " --pid "
        elif pid:
            cmd += " --pid "
        else:
            cmd += " --get "        
    
    ##cmd += "\"$i\" ; done"
    #cmd += "$i; done )"
        if search_term:
            # search_term_list could be a set of programme indices, so don't surround them with quotes
            cmd += search_term
        
        if (i < len(search_term_list) - 1):
            cmd += "; "

    if pvr_queue:
        launched = True
        process_output = command.run(cmd, log_level=logging.DEBUG, temp_pathname=settings.TEMP_PATHNAME)
    else:    
        #CommandQueue.CommandQueue().run(...)
        launched = command_queue.run(cmd, log_level=logging.DEBUG, temp_pathname=settings.TEMP_PATHNAME,
                                     terminal_prog=_TERMINAL_PROG)
        process_output = None

    return (launched, process_output)

def info(search_term, preset=None, proxy_enabled=False):
    """ Run get_iplayer --info.
        Return table with columns: serie title, episode title plus description.
    """
    # Cannot do a search on pid
    # Only from outside the UK and partial_proxy enabled in get_iplayer(?):
    #     If proxy_enabled is false then info retrieval will be faster but the info 
    #     will not contain proper values for "modes" and "tvmodes" (the available tv download file sizes)
    cmd = _GET_IPLAYER_PROG + " --info --nocopyright" 
    if preset:
        cmd += " --preset=" + preset
    if not proxy_enabled:
        # Disable proxy setting
        cmd += " --proxy=0"
    if search_term:
        cmd += " \"" + search_term + "\""

    process_output = command.run(cmd, temp_pathname=settings.TEMP_PATHNAME)

    lines = process_output.splitlines()
    output_lines = []
    for line in lines:
        # Skip empty lines
        if line and line[0] and not line.startswith("INFO:") and not line.startswith("Matches:"):
            l = line.split(":", 1)
            # Match key-value pairs
            if len(l) == 2 and l[1]:
                output_lines.append([l[0], l[1].lstrip()])

    return output_lines

def refresh(preset=None):
    """ Run get_iplayer --refresh. """
    if not preset:
        #preset = Preset.RADIO + "," + Preset.TV
        preset = "all"
    cmd = _GET_IPLAYER_PROG + " --refresh --preset=" + preset    
    return command.run(cmd, temp_pathname=settings.TEMP_PATHNAME)

