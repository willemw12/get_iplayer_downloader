import logging
import os
import subprocess

logger = logging.getLogger(__name__)

#def run(cmd, run_in_terminal_window=False, terminal_title=None, quiet=False, **keywords):
def run(cmd, run_in_terminal_window=False, terminal_title=None, quiet=False,
        log_level=logging.DEBUG, temp_pathname=None):
    if not quiet:
        logger.log(log_level, "run(cmd): cmd=%s", cmd)
        if log_level == logging.DEBUG:
            #temp_pathname = keywords["temp_pathname"] if "temp_pathname" in keywords else None
            if temp_pathname is not None:
                # Add commands to log to file
                if not os.path.exists(temp_pathname):
                    os.makedirs(temp_pathname)
                #cmd += " 2>&1 | tee $(mktemp " + temp_pathname + "/cmd-XXXXXXXXXX.log)"
                cmd += " 2>&1 | tee " + temp_pathname + "/$(date +\"%Y%m%d%H%M%S\")-cmd.log"

    if run_in_terminal_window:
        # Add commands to run in a terminal window
        #NOTE Linux specific
        #NOTE x-terminal-emulator doesn't take arguments
        #cmd = "gnome-terminal --geometry=132x43 --title=\"" + str(terminal_title) + "\" --command=\"bash -c '" + cmd + " ; cd ; $SHELL'\" ; exit 0"
        cmd = "gnome-terminal --geometry=132x43 --title=\"" + str(terminal_title) + "\" --command=\"bash -c '" + cmd + " ; cd ; $SHELL'\" ; exit 0"

    process_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

    if not quiet:
        logger.log(log_level, "run(cmd): process_output=%s\n", process_output)
        #print "Ready"

    return process_output
