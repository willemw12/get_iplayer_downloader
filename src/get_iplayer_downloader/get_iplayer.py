""" Perform get_iplayer operations.
"""

import ast
from datetime import datetime

from get_iplayer_downloader import common, settings
from get_iplayer_downloader.tools import command, command_queue, string

#NOTE Linux specific
GET_IPLAYER_CMD = "/usr/bin/get_iplayer"

RADIO_DOWNLOAD_PATH = settings.config().get("radio", "download-path")
TV_DOWNLOAD_PATH = settings.config().get("tv", "download-path")

SINCE_LIST = [[0, "Since"], [4, "4 hours"], [8, "8 hours"], [12, "12 hours"],
              [24, "1 day"], [48, "2 days"], [72, "3 days"], [96, "4 days"],
              [120, "5 days"], [144, "6 days"], [168, "7 days"]]

class Preset:
    RADIO = "radio"
    TV = "tv"
    
class Type:
    #ALL = "all"
    RADIO = "radio"
    PODCAST = "podcast"
    TV = "tv"
    
class Channel:
    RADIO = settings.config().get("radio", "channels")
    TV = settings.config().get("tv", "channels")

class Category:
    #NOTE doesn't work: RADIO = [[None, "Genre"]].extend(...)
    RADIO = [[None, "Genre"]]
    RADIO.extend(ast.literal_eval(settings.config().get("radio", "categories")))
    
    TV = [[None, "Genre"]]
    TV.extend(ast.literal_eval(settings.config().get("tv", "categories")))

def search(search_text, preset=Preset.RADIO, prog_type=Type.RADIO, channel=Channel.RADIO,
           category=None, since=0, search_all=False):
    cmd = GET_IPLAYER_CMD
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
    cmd += " --nocopyright --listformat=\"|<index>|<episode> ~ <desc>\" --tree"
    if search_text:
        cmd += " \"" + search_text + "\""
    
    process_output = command.run(cmd)

    # Convert the process output lines to lists (not dicts), matching the GtkTreeStore input data
    
    lines = process_output.splitlines()

    output_lines = []
    l_prev = None
    level = 0
    copy = False
    for line in lines:
        l = line.split("|", 2)
        # Skip empty lines
        if l[0]:
            # Match string containing only spaces
            #ALTERNATIVE
            #1) all(c in " " for c in l)
            #2) CHECK_RE = re.compile('[ -]+$'); CHECK_RE.match(l)
            #3) re.match("^[ ]+$", l)
            if level == 0 and l[0].isspace():
                # Going from root level (0) to level 1
                level = 1
                copy = True
                if l_prev:
                    # Add a field (Serie) of the parent on the previous line
                    output_lines.append([False, None, l_prev[0], None])
            if level == 1 and not l[0].isspace():
                # Going from level 1 to root level (0)
                level = 0
                copy = False
            #if level == 1 and copy:
            if copy:
                # Add two fields (Episode and Description) of the child/leave, the current line
                if l[2].startswith("- ~ "):
                    # No episode title
                    output_lines.append([False, string.decode(l[1]), None, string.decode(l[2][4:])])
                else:
                    output_lines.append([False, string.decode(l[1]), None, string.decode(l[2])])
            l_prev = l

    return output_lines

def get(search_text, preset=Preset.RADIO, hd_tv_mode=False, force_download=False, output_path=None):
    if preset == Preset.RADIO:
        week_number = datetime.today().isocalendar()[1]
        ##ALTERNATIVE Week number
        #dldate = <iplayer download date attribute "dldate">
        #date = datetime.strptime(dldate, "%Y-%m-%d")
        #week_number = date(date).isocalendar()[1]
        #week_number = <Python formatted print equivalent of `date +%V`>

        output_path = RADIO_DOWNLOAD_PATH + "/bbc." + str.format("{0:02}", week_number)
    elif preset == Preset.TV:
        output_path = TV_DOWNLOAD_PATH

    cmd = GET_IPLAYER_CMD
    if preset:
        cmd += " --preset=" + preset
    if hd_tv_mode:
        cmd += " --tvmode=\"flashhigh,flashhd,flashvhigh\""
    if force_download:
        cmd += " --force"
    cmd += " --output=" + output_path
    cmd += " --nocopyright --hash --get "
    if search_text:
        # search_text is a set of program indices, so don't surround them with quotes
        cmd += search_text

    run_in_terminal_window = string.str2bool(settings.config().get(preset, "run-in-terminal"))

    # One-liner: terminal_title = common.__program_name__ if run_in_terminal_window else None
    terminal_title = None
    if run_in_terminal_window:
        terminal_title = common.__program_name__
        
    #return CommandQueue.CommandQueue().run(cmd, run_in_terminal_window=run_in_terminal_window, terminal_title=terminal_title)
    return command_queue.run(cmd, run_in_terminal_window=run_in_terminal_window, terminal_title=terminal_title)
        
def info(preset, search_text, proxy_enabled=False):
    # Only from outside the UK and partial_proxy enabled in get_iplayer(?):
    #     If proxy_enabled is false then info retrieval will be faster but the info 
    #     will not contain proper values for "modes" and "tvmodes" (the available tv download file sizes).
    cmd = GET_IPLAYER_CMD + " --info --nocopyright" 
    if preset:
        cmd += " --preset=" + preset
    if not proxy_enabled:
        cmd += " --proxy=0"
    if search_text:
        cmd += " \"" + search_text + "\""

    process_output = command.run(cmd)

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
    if not preset:
        #preset = Preset.RADIO + "," + Preset.TV
        preset = "all"
    cmd = GET_IPLAYER_CMD + " --refresh --preset=" + preset    
    return command.run(cmd)

