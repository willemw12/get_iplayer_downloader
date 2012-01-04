import logging
import subprocess

logger = logging.getLogger(__name__)

def run(cmd, run_in_terminal_window=False, terminal_title=None, quiet=False):
    if run_in_terminal_window:
        #NOTE Linux specific
        #NOTE x-terminal-emulator doesn't take arguments
        cmd = "gnome-terminal --geometry=132x43 --title=\"" + str(terminal_title) + "\" --command=\"bash -c '" + cmd + " 2>&1 | tee $(mktemp /tmp/get_iplayer_downloader/cmd-XXXXXXXXXX.log); cd ; $SHELL'\" ; exit 0"
        
    if not quiet:
        logger.info("run(cmd): cmd=%s", cmd)

    process_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

    if not quiet:
        logger.info("run(cmd): process_output=%s\n", process_output)
        print "Ready"

    return process_output
