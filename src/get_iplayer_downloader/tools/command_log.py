import os

from datetime import datetime

#from get_iplayer_downloader.tools import markup as Markup
from . import markup as Markup

_first_log_file = True

def _log_text(string, markup):
    if markup:
        return Markup.text2html(string)
    return string
    
def _log_cmd_file(dirpath, filename, full=False, markup=False):
    """ Return log messages from single command log file @dirpath/@filename.
        Return all download logs (get_iplayer --get or --pid), plus any command log file containing errors (FATAL, ERROR or WARNING log messages).
        If @full is true, return the whole command log file, otherwise return only error and episode download messages.
        If @markup is true, then error messages will be in bold.
    """
    
    log_output = ""
    filepathname = os.path.join(dirpath, filename)

    is_download_cmd = False
    is_error = False
    #is_error_cmd = False

    #WORKAROUND Non-UTF-8 command output from BBC Alba programmes: encoding "LATIN-1".
    #           However, the copyright character (c) in rtmpdump/flvstreamer output is preceded by ^A.
    #with open(filepathname, "r", encoding="UTF-8") as file:
    with open(filepathname, "r", encoding="LATIN-1") as file:
        #NOTE To join all lines at once (list2string): log_output = "".join(lines)
        #NOTE readline() reads one character
        lines = file.readlines()
        prev_line_index = -99
        for i, line in enumerate(lines):
            if line.startswith("FATAL") or line.startswith("ERROR") or line.startswith("WARNING"):
                is_error = True
                if is_download_cmd:
                    is_error_cmd = True
                
                if not full:
                    #for j in range(2, 0, -1):
                    try:
                        prev_line = lines[i - 1]
                        if prev_line_index != i - 1 and prev_line and prev_line != "\n" and not prev_line.startswith("#"):
                            # prev_line has not yet been added to log_output. Skip empty lines and download progress lines (#)
                            log_output += _log_text(prev_line, markup)
                    except IndexError:
                        pass

                if markup:
                    log_output += "<b>" + _log_text(line, markup) + "</b>"
                else:
                    log_output += line
                prev_line_index = i
            else:
                if "get_iplayer " in line:
                    is_error_cmd = False
                    if "--get" in line or "--pid" in line:
                        is_download_cmd = True

                if full:
                    log_output += line
                    prev_line_index = i
                else:
                    if is_download_cmd:
                        if line == "Matches:\n":
                            log_output += _log_text(lines[i + 1], markup)
                            prev_line_index = i
                        elif line.startswith("INFO: No specified modes") or \
                             (is_error_cmd and (line == "Download complete\n" or line.startswith("Resuming download") or line.startswith("INFO: Command exit code"))):
                            # Log additional messages when current command has an error
                            if markup:
                                log_output += "<b>" + _log_text(line, markup) + "</b>"
                            else:
                                log_output += line
                            prev_line_index = i
                        #elif line.startswith("INFO:get_iplayer_post_subdir:move_file(): Move")
                        #    log_output += _log_text(line, markup)
                        #    prev_line_index = i

    if not log_output or (not is_download_cmd and not is_error):
        # Nothing to log
        return ""

    # Log header: filename (started at hour:minutes)
    log_header = "{0} (started at {1}:{2}):\n".format(filepathname, filename[8:10], filename[10:12])
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
                log_output += _log_cmd_file(dirpath, filename, full=full, markup=markup)
                
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
                with open(os.path.join(dirpath, filename), "r", encoding="LATIN-1") as file:
                    lines = file.readlines()
                    for line in lines:
                        if line.startswith("FATAL") or line.startswith("ERROR") or line.startswith("WARNING"):
                            errors += 1
    return errors
