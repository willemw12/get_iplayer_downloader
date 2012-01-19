#!/usr/bin/env python

""" get_iplayer post-processing script.
    Arguments: @filename and @categories
    Move @filename to directory which name is the last category in @categories
    Configuration: for example, put in ~/.get_iplayer/presets/tv:
        command get_iplayer_tv_post.py "<filename>" "<categories>"
"""
#AlTERNATIVE retrieve category from subdir
#        subdir 1
#        subdir-format <categories>

import argparse
import logging
import os
import sys
import re
import shutil
import tempfile

progname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logger = logging.getLogger(progname)

#ALTERNATIVE global declaration: however it is less obvious in the code that the variable is global
#global args
args = None

#AlTERNATIVE retrieve category from subdir
#TODO match multiple camel case strings separated by underscore
#
#def first_camel_case(str):
#    if str is None:
#        return None
#    # Match any string, non-greedy, until upper-case character
#    match = re.match("(.+?[^_])[A-Z]", str)
#    return match.group(1) if match is not None else None
#
#def last_camel_case(str):
#    if str is None:
#        return None
#    # Match a single camel case string. Last + : repeat match and match the last occurrence
#    match = re.match("([A-Z][a-z,0-9_]+)+", str)
#    #return match.group(1) if match is not None else None
#    return match.group(1) if match is not None else str

####

def _init_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-d", "--debug", dest="debug", action="store_const", const=True, default=False, help="set log level to debug")
    argparser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="set log level to info")    
    argparser.add_argument("-q", "--quiet", dest="quiet", action="store_const", const=True, default=False, help="set log level to fatal")
    argparser.add_argument("filename", nargs=1)
    argparser.add_argument("categories", nargs=1)
    global args
    args = argparser.parse_args()

def _init_loggers():
    logging.basicConfig(level=logging.WARNING)

    log_pathname = tempfile.gettempdir()
    log_filename = os.path.join(log_pathname, progname + ".log")
    if not os.path.exists(log_pathname):
        os.mkdir(log_pathname)
    handler = logging.FileHandler(log_filename)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)
    elif args.quiet:
        logger.setLevel(logging.FATAL)

def _move_file(filename, categories):
    src_dirname = os.path.dirname(filename)
    basedirname = os.path.dirname(src_dirname)
    #AlTERNATIVE retrieve category from subdir
    #categories = os.path.basename(src_dirname)
    #specific_category = last_camel_case(categories)
    category_list = categories.split(",")
    # lstrip(): trim leading whitespaces
    specific_category = category_list[len(category_list) - 1].lstrip()

    # Sanitize directory name. \s means whitespace
    p = re.compile("([\s;<>\*\|&\$!#\(\)\[\]\{\}:'\"]+)")
    specific_category = p.sub("_", specific_category)
    
    dest_dirname = os.path.join(basedirname, specific_category)
    if not os.path.exists(dest_dirname):
        os.mkdir(dest_dirname)

    try:
        shutil.move(filename, dest_dirname)
        logger.info("Moved {0} to {1}".format(filename, dest_dirname))
    #NOTE combined exception handling
    except (IOError, os.error, shutil.Error), why:
        logger.warning("Failed to move {0} to {1}".format(filename, dest_dirname))
        logger.debug(str(why))

    # Remove empty directory
    try:
        os.rmdir(src_dirname)
    except OSError:
        pass

def main():
    _init_argparser()
    _init_loggers()
    
    _move_file(args.filename[0], args.categories[0])

if __name__ == "__main__":
    main()
