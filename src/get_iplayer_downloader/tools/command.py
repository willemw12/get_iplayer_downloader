import logging
import os
import subprocess

from datetime import datetime

logger = logging.getLogger(__name__)

#def run(cmd, terminal_prog=None, terminal_title=None, quiet=False, **keywords):
def run(cmd, terminal_prog=None, terminal_title=None, quiet=False, temp_pathname=None):
    """ @terminal_prog is a terminal emulator program name, compatible with xterm options (-geometry instead of --geometry). """
    
    # The command string that will be executed
    cmd_exec = cmd
    
    log_level = logging.getLogger().level

    if not quiet:
        #temp_pathname = keywords["temp_pathname"] if "temp_pathname" in keywords else None
        if temp_pathname is not None:
            # Log commands
            
            if not os.path.exists(temp_pathname):
                os.makedirs(temp_pathname)
        
            ##cmd_exec += " 2>&1 | tee $(mktemp " + temp_pathname + "/cmd_exec-XXXXXXXXXX.log)"
            #cmd_exec = "(" + cmd_exec + ") 2>&1 | tee " + temp_pathname + "/$(date +\"%Y%m%d%H%M%S\")-cmd_exec.log"
        
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            cmd_logname = os.path.join(temp_pathname, timestamp + "-cmd.log")
            #with open(cmd_logname, "w") as file:
            #    file.write("%s\n\n" % cmd)
            #cmd_exec = "( " + cmd_exec + " ) 2>&1 | tee -a " + cmd_logname
            cmd_exec = "( set -x ; " + cmd_exec + " ) 2>&1 | tee  " + cmd_logname

    if terminal_prog:
        # terminal_prog is not None and not empty string
        
        # Add commands to run in a terminal window
        if os.name == "posix":
            if log_level == logging.DEBUG:
                # Linux specific
                #cmd_exec = "gnome-terminal --geometry=131x41 --title=\"" + str(terminal_title) + "\" --command=\"sh -c '" + cmd_exec + " ; cd ; sh'\" ; exit 0"
                cmd_exec = terminal_prog + " -e \"$SHELL -c '" + cmd_exec + " ; RET=$? ; cd ; $SHELL'\" ; exit $RET"
            else:
                # Linux specific
                cmd_exec = terminal_prog + " -e \"$SHELL -c '( set -x ; " + cmd_exec + " ) ; RET=$? ; cd ; $SHELL'\" ; exit $RET"
                
    if not quiet:
        logger.debug("run(): cmd_exec=%s", cmd_exec)
        logger.info("run(): cmd=%s", cmd)

        if terminal_prog:
            # Log this now. Log statements after subprocess.check_output() will
            # only be printed after the terminal window has been closed
            logger.debug("run(): process_output logged to %s", cmd_logname)

    process_output = ""
    try:
        process_output = subprocess.check_output(cmd_exec, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        #logger.warning("(return code " + str(exc.returncode) + ") " + exc.output)
        logger.warning(exc.output)
        
        # Write log message also to the command log file, so the message will show up in the download log viewer
        with open(cmd_logname, "a") as file:
            file.write("WARNING:%s" % exc.output)

    if not quiet:
        logger.debug("run(): process_output=%s", process_output)
        #print "Ready"

    return process_output
                            