#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import re
import shutil
import tempfile

from datetime import datetime

from get_iplayer_downloader.tools import file

progname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logger = logging.getLogger(progname)

#ALTERNATIVE global declaration: however, it is less obvious in the code that the variable is global
#global args
args = None

#AlTERNATIVE retrieve category name from subdir
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
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                        description="""This is a get_iplayer post-processing script. It is an extension to the
get_iplayer "subdir" output option. In addition to the formatting fields
listed by "get_iplayer --info ...", this script supports:

  <categorysub>         last and most specific category from --categories
  <categorymain>        first and most general category from --categories
  <week>                current week number

Arguments --categories, --dir and --filename are there to transfer values from 
get_iplayer to this script and are usually always specified as:

  --categories="<categories>" --dir="<dir>" --filename="<filename>"

A get_iplayer "command" option example (one line):

  command get_iplayer_post_subdir.py 
                        --categories="<categories>"
                        --dir="<dir>" 
                        --filename="<filename>" 
                        --force
                        --subdir-format=
                            "bbc.<week>/<categorymain>_<categorysub>/<longname>"
""")
    
    #AlTERNATIVE retrieve category name from subdir
    #        subdir 1
    #        subdir-format <categories>
    
    argparser.add_argument("-d", "--debug", dest="debug", action="store_const", const=True, default=False, help="set log level to debug")
    argparser.add_argument("-q", "--quiet", dest="quiet", action="store_const", const=True, default=False, help="set log level to fatal")
    argparser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="set log level to info")
    argparser.add_argument("--categories", dest="categories", metavar="<categories>", nargs=1, default=None, help="programme categories (comma-separated list) of the downloaded file. Expected when <category>, <categorymain> or <categorysub> is in --subdir-format")
    argparser.add_argument("--dir", dest="dir", metavar="<pathname>", nargs=1, default=None, required=True, help="output directory")
    argparser.add_argument("--filename", dest="filename", metavar="<filename>", nargs=1, default=None, required=True, help="downloaded file to be moved")
    argparser.add_argument("--force", dest="force", action="store_const", const=True, default=False, help="overwrite existing destination file")
    argparser.add_argument("--subdir-format", dest="subdir_format", metavar="<format>", nargs=1, default=None, required=True, help="subdirectory path")
    #argparser.add_argument("filename", nargs=1)
    #argparser.add_argument("categories", nargs=1)
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

def _move_file(categories, dirname, filename, force, subdir_format):
    logger.debug("move_file(): filename = \"{0}\", categories = \"{1}\", dirname = \"{2}\", force = {3}, subdir_format = \"{4}\"".format(filename, categories, dirname, force, subdir_format))

    src_dirname = os.path.dirname(filename)

    # Perform additional substitution (field formatting)
    #NOTE Find substring
    if "<week>" in subdir_format:
        week_number = datetime.today().isocalendar()[1]
        subdir_format = subdir_format.replace("<week>", "{0:02}".format(week_number))

    if categories is not None:
        #AlTERNATIVE retrieve category name from the last subdirectory in @filename,
        #    which is formatted with the <categories> property value.
        #categories = os.path.basename(src_dirname)
        #specific_category = last_camel_case(categories)
        category_list = categories.split(",")
        # lstrip(): trim leading whitespaces
        specific_category = category_list[len(category_list) - 1].lstrip()
        main_category = category_list[0].lstrip()
 
        # Perform additional substitutions (field formatting)
        if main_category == specific_category:
            # <category> is the same as <categorymain>
            subdir_format = subdir_format.replace("<category>", "<categorymain>")

            # Merge duplicate string values
            subdir_format = subdir_format.replace("<categorysub><categorymain>", main_category)
            subdir_format = subdir_format.replace("<categorymain><categorysub>", main_category)

            # Merge duplicate string values separated by sanitized separators or
            # other valid separator characters (-)
 
            subdir_format = file.sanitize_path(subdir_format, False)
        
            #NOTE p.sub replaces that whole search string, not just the group in the search string
            #     --> use non-consuming, fixed-length lookaheads (?=...) and lookbehinds (?<=...)
            p = re.compile(r"(?<=<categorysub>)([_-]+)(?=<categorymain>)|(?<=(?<=<categorymain>))([_-]+)(?=<categorysub>)")
            subdir_format = p.sub(r"_", subdir_format)
            #ALTERNATIVE use only one group (the start/end pos won't be correct after the first substitution (field formatting))
            #m = re.search(pattern, str)
            #if m and m.groups() > 0:
            #    str = str[0:m.start(1)] + replacement_str + str[m.end(1):len(str)]
            subdir_format = subdir_format.replace("<categorysub>_<categorymain>", main_category)
            subdir_format = subdir_format.replace("<categorymain>_<categorysub>", main_category)
        subdir_format = subdir_format.replace("<categorysub>", specific_category)
        subdir_format = subdir_format.replace("<categorymain>", main_category)
    else:
        if "<category>" in subdir_format or "<categorymain>" in subdir_format or "<categorysub>" in subdir_format:
            logger.warning("move_file(): --categories expected when <category>, <categorymain>  and/or <categorysub> is in --subdir-format")
            #sys.exit(1)

    # Sanitize everything in subdir again, to sanitize the substituted values and unrecognized substitutions (field formatting)
    subdir_format = file.sanitize_path(subdir_format, True)

    # Move the file
    try:
        dest_dirname = os.path.join(dirname, subdir_format)
        logger.info("move_file(): Move \"{0}\" to \"{1}\"".format(filename, dest_dirname))
        if not os.path.exists(dest_dirname):
            os.makedirs(dest_dirname)
        if force:
            try:
                basename = os.path.basename(filename)
                dest_filename = os.path.join(dest_dirname, basename)
                os.remove(dest_filename)
                logger.info("move_file(): Overwriting destination file \"{0}\"".format(dest_filename))
            except OSError:
                pass
        shutil.move(filename, dest_dirname)
    except (IOError, os.error, shutil.Error) as exc:
        logger.warning("move_file(): Failed to move \"{0}\" to \"{1}\"".format(filename, dest_dirname))
        logger.warning(exc)

    # Remove empty directory
    try:
        os.rmdir(src_dirname)
    except OSError:
        pass

def main():
    _init_argparser()
    _init_loggers()
    
    categories = args.categories[0] if args.categories is not None else None
    _move_file(categories, args.dir[0], args.filename[0], args.force, args.subdir_format[0])

if __name__ == "__main__":
    main()
