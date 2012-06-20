import os

from datetime import datetime

#from get_iplayer_downloader.tools import markup as Markup
from . import markup as Markup

_first_log_file = True

def _log_text(string, markup):
    if markup:
        return Markup.text2html(string)
    return string
    
def _log_file(dirpath, filename, full=False, markup=False):
    log_output = ""
    filepathname = os.path.join(dirpath, filename)

    #WORKAROUND non-UTF-8 command output from BBC Alba programmes: encoding "LATIN-1"
    #with open(filepathname, "r", encoding="UTF-8") as file:
    with open(filepathname, "r", encoding="LATIN-1") as file:
        #NOTE readline() reads one character
        lines = file.readlines()
        for i, line in enumerate(lines):
            if "get_iplayer " in line:
                if "--get" not in line and "--pid" not in line:
                    # Skip log file if not a get_iplayer "get" command.
                    # Assumption: if the first get_iplayer command is not a "get" command,
                    # then other get_iplayer commands in the same file are also not "get" commands
                    return ""
            if full:
                #NOTE Join all lines at once (list2string): log_output = "".join(lines)
                log_output += line
            elif line == "Matches:\n":
                log_output += _log_text(lines[i + 1], markup)
            #elif line == "Download complete\n" or line.startswith("INFO:get_iplayer_post_subdir:move_file(): Move")
            #    log_output += _log_text(line, markup)
            elif line.startswith("FATAL") or line.startswith("ERROR") or line.startswith("WARNING"):
                #for j in range(2, 0, -1):
                try:
                    prev_line = lines[i - 1]
                    if prev_line and prev_line != "\n" and not prev_line.startswith("FATAL") and not prev_line.startswith("ERROR") and not prev_line.startswith("WARNING"):
                        log_output += _log_text(prev_line, markup)
                except IndexError:
                    pass

                if markup:
                    log_output += "<b>" + _log_text(line, markup) + "</b>"
                else:
                    log_output += line
                    
    if not log_output:
        return ""

    # Log header: filename (started at hour:minutes)
    log_header = "%s (started at %s:%s):\n" % (filepathname, filename[8:10], filename[10:12])
    if full:
        log_header += "\n"
        global _first_log_file
        if _first_log_file:
            _first_log_file = False
        else:
            log_header = "======================================================================\n\n" + log_header

    #return (log_header + log_output + "\n", first_time)
    return log_header + log_output + "\n"

def download_log(temp_pathname, full=False, markup=False, sort_by_mtime=False):
    """ Return full download log if @full is true, otherwise return summary download log. """
    
    log_output = ""
    # Restrict to today's download log
    timestamp = datetime.now().strftime("%Y%m%d")
    for dirpath, unused_dirnames, filenames in os.walk(temp_pathname):
        if sort_by_mtime:
            mtime = lambda filename: os.stat(os.path.join(dirpath, filename)).st_mtime
            #sorted(filenames, key=mtime)
            filenames.sort(key=mtime)
        else:
            filenames.sort()

        global _first_log_file
        _first_log_file = True
        for filename in filenames:
            if filename.endswith("-cmd.log") and timestamp in filename:
                log_output += _log_file(dirpath, filename, full=full, markup=markup)
                
    return log_output

def download_errors(temp_pathname):
    """ Return the number of today's FATAL, ERROR and WARNING download log messages found in command log files. """
    
    errors = 0
    # Restrict to today's download log
    timestamp = datetime.now().strftime("%Y%m%d")
    for dirpath, unused_dirnames, filenames in os.walk(temp_pathname):
        for filename in filenames:
            if filename.endswith("-cmd.log") and timestamp in filename:
                #with open(os.path.join(dirpath, filename), "r", encoding="UTF-8") as file:
                with open(os.path.join(dirpath, filename), "r", encoding="latin1") as file:
                    lines = file.readlines()
                    for line in lines:
                        if "get_iplayer " in line:
                            if "--get" not in line and "--pid" not in line:
                                # Skip log file if not a get_iplayer "get" command.
                                # Assumption: if the first get_iplayer command is not a "get" command,
                                # then other get_iplayer commands in the same file are also not "get" commands
                                break
                        elif line.startswith("FATAL") or line.startswith("ERROR") or line.startswith("WARNING"):
                            errors += 1
                            
    return errors
                            