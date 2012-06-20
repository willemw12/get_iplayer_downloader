import io
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
    
    #log_level = logging.getLogger().level

    if not quiet:
        #temp_pathname = keywords["temp_pathname"] if "temp_pathname" in keywords else None
        if temp_pathname is not None:
            # Log commands
            if not os.path.exists(temp_pathname):
                os.makedirs(temp_pathname)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            cmd_logname = os.path.join(temp_pathname, timestamp + "-cmd.log")
            cmd_exec = "( set -x ; " + cmd_exec + " ) 2>&1 | tee " + cmd_logname

    if terminal_prog:
        # terminal_prog is not None and not empty string
        # Add commands to run in a terminal window
        if os.name == "posix":
            # Linux specific
            #cmd_exec = "gnome-terminal --geometry=131x41 --title=\"" + str(terminal_title) + "\" --command=\"sh -c '" + cmd_exec + " ; cd ; sh'\" ; exit 0"
            cmd_exec = terminal_prog + " -e \"$SHELL -c '" + cmd_exec + " ; RET=$? ; cd ; $SHELL'\" ; exit $RET"
                
    if not quiet:
        # If not a silent process, e.g. command to update the progress bar
        logger.debug("run(): cmd_exec=%s", cmd_exec)
        logger.info("run(): cmd=%s", cmd)
        if terminal_prog:
            # Log this now. Log statements after subprocess.check_output() will
            # only be printed after the terminal window has been closed
            logger.debug("run(): process_output logged to %s", cmd_logname)

    process_output = ""

    #### Run command
    
    # Run command. Command output is expected to be UTF-8
    #try:
    #    #NOTE check_output() and Popen() expect a UTF-8 text output and uses the "strict" encoding option (string.decode("utf8", "strict"))
    #    process_output = subprocess.check_output(cmd_exec, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
    #    #
    #    #ALTERNATIVE subprocess.Popen() instead of subprocess.check_output() 
    #    #text_output = io.StringIO()
    #    #with subprocess.Popen(cmd_exec, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
    #    #    text_output.write(proc.stdout.read())
    #    #process_output = text_output.getvalue()
    #except UnicodeDecodeError as exc:
    #    logger.warning(exc)
    #except subprocess.CalledProcessError as exc:
    #    ...

    # Run command. Command output can be non-UTF-8
    try:
        #NOTE universal_newlines=True turns proc.stdout into a TextIOWrapper, i.e. a buffer interface, which the encode method in text_input.read() does not support
        #with subprocess.Popen(..., stdout=file, ...
        with subprocess.Popen(cmd_exec, shell=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
            # Cannot seek a pipe (proc.stdout) to retry another encoding on the command/process output
            # Copy pipe content into memory
            bytes_buffer = proc.stdout.read()
            #proc.stdout.close()            
            try:
                process_output = bytes_buffer.decode("UTF-8", "strict")
            except (UnicodeDecodeError, ValueError) as exc:
                try:
                    #WORKAROUND non-UTF-8 command output from BBC Alba programmes
                    #NOTE encoding="LATIN-1" (and errors="replace"?) seems OK with non-LATIN-1 characters (from BBC Alba) in get_iplayer.get(),
                    #     but won't always work properly in get_iplayer.get(): not enough columns returned in |-separated string
                    #NOTE Trying LATIN-1 first, to try to avoid unreadable characters (i.e. replacement marker '?' in a diamond shape) in the GUI
                    logger.warning(exc)
                    logger.warning("trying 'latin-1' codec")
                    process_output = bytes_buffer.decode("LATIN-1", "strict")
                except (UnicodeDecodeError, ValueError) as exc:
                    try:
                        logger.warning(exc)
                        logger.warning("trying 'utf-8' codec and replacing non-utf-8 characters")
                        process_output = bytes_buffer.decode("UTF-8", "replace")
                    except (UnicodeDecodeError, ValueError) as exc:
                        # Should not happen
                        logger.warning(exc)
                        #return ""
    except subprocess.CalledProcessError as exc:
        #logger.warning("(return code " + str(exc.returncode) + ") " + exc.text_output)
        logger.warning(exc.output)
        
        # Write log message also to the command log file, so the message will show up in the download log viewer
        with open(cmd_logname, "a") as file:
            file.write("WARNING:%s" % exc.output)

    ####
    
    if not quiet and not terminal_prog:
        # If not a silent process, e.g. command to update the progress bar
        # If running inside a terminal window then the log message was already generated before command execution
        logger.debug("run(): process_output=%s", process_output)
        #print "Ready"

    return process_output




##############################################################################

#    #ALTERNATIVE using buffer = io.BytesIO() and io.TextIOWrapper(buffer, ...)
#    # Run command. Command output can be non-UTF-8
#    try:
#        with subprocess.Popen(cmd_exec, shell=True, universal_newlines=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
#            bytes_input = io.BytesIO()
#            bytes_input.write(proc.stdout.read())
#            bytes_input.seek(0)
#            #proc.stdout.close()
#            
#            # Get command/process output
#            text_output = io.StringIO()
#            
#            try:
#                text_input = io.TextIOWrapper(proc.stdout, bufsize=-1, encoding="UTF-8", errors="strict")
#                bytes_input2 = _copy_bytes_io(bytes_input)
#                bytes_input2.seek(0)
#                text_input = io.TextIOWrapper(bytes_input2, bufsize=-1, encoding="UTF-8", errors="strict")
#                text_output.write(text_input.read())
#                process_output = text_output.getvalue()
#            except (UnicodeDecodeError, ValueError) as exc:
#                try:
#                    logger.warning(exc)
#                    logger.warning("trying 'latin-1' codec")
#
#                    bytes_input2 = _copy_bytes_io(bytes_input)
#                    bytes_input2.seek(0)
#                    text_input = io.TextIOWrapper(bytes_input2, bufsize=-1, encoding="LATIN-1", errors="strict")
#                    text_output.write(text_input.read())
#                    process_output = text_output.getvalue()            
#                except (UnicodeDecodeError, ValueError) as exc:
#                    try:
#                        logger.warning(exc)
#                        logger.warning("trying 'utf-8' codec and replacing non-utf-8 characters")
#                        
#                        bytes_input2 = _copy_bytes_io(bytes_input)
#                        bytes_input2.seek(0)
#                        text_input = io.TextIOWrapper(bytes_input2, bufsize=-1, encoding="UTF-8", errors="replace")
#                        text_output.write(text_input.read())
#                        process_output = text_output.getvalue()            
#                    except (UnicodeDecodeError, ValueError) as exc:
#                        logger.warning(exc)

