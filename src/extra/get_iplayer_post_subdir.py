#!/usr/bin/env python

import argparse
import logging
import os
import sys
import re
import shutil
import tempfile
from datetime import datetime

progname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logger = logging.getLogger(progname)

#ALTERNATIVE global declaration: however it is less obvious in the code that the variable is global
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
get_iplayer subdir output option. In addition to the substitution of the
standard properties listed by "get_iplayer --info ...", this script supports:

  <category>            last and most specific category from --categories
  <categorymain>        first and most general category from --categories
  <week>                current week number

get_iplayer command option example (one line):

  command get_iplayer_post_subdir.py 
                        --categories="<categories>"
                        --dir="<dir>" 
                        --filename="<filename>" 
                        --subdir-format=
                            "bbc.<week>/<categorymain>_<category>/<longname>"
""")
    #AlTERNATIVE retrieve category name from subdir
    #        subdir 1
    #        subdir-format <categories>
    
    argparser.add_argument("-d", "--debug", dest="debug", action="store_const", const=True, default=False, help="set log level to debug")
    argparser.add_argument("-q", "--quiet", dest="quiet", action="store_const", const=True, default=False, help="set log level to fatal")
    argparser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="set log level to info")
    argparser.add_argument("--categories", dest="categories", metavar="<categories>", nargs=1, default=None, help="programme categories (comma-separated list) of the downloaded file")
    argparser.add_argument("--dir", dest="dir", metavar="<pathname>", nargs=1, default=None, required=True, help="output directory. Usually --dir=<dir>, which is the get_iplayer output directory plus the get_iplayer subdir directory, if enabled")
    argparser.add_argument("--filename", dest="filename", metavar="<filename>", nargs=1, default=None, required=True, help="downloaded file to be moved")
    argparser.add_argument("--subdir-format", dest="subdir_format", metavar="<format>", nargs=1, default=None, required=True, help="subdirectory path, optionally containing property substitution strings.")
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

def _sanitize_path(path, include_substition_markers):
    # Sanitize directory path, optionally including substition marker 
    # characters < and >, i.e. collapse adjacent invalid characters into a 
    # single _ character or remove invalid characters

    # Match ! and perhaps other characters, which as program arguments have
    # been translated by Python or get_iplayer into \! and this would otherwise
    # result in an _ in the sanitized path
    p = re.compile(r"(\\\!+)")
    path = p.sub("", path)

    #PERL get_iplayer
    #sub StringUtils::sanitize_path {
    # Remove fwd slash if reqd
    #$string =~ s/\//_/g if ! $allow_fwd_slash;
    # Replace backslashes with _ regardless
    #$string =~ s/\\/_/g;
    # Sanitize by default
    #$string =~ s/\s+/_/g if (! $opt->{whitespace}) && (! $allow_fwd_slash);
    #
    # Similar to Perl code, however exclude matching forward slash
    # \s means whitespace
    if os.name == "posix":
        p = re.compile(r"([\\\s]+)")
    else:
        p = re.compile(r"([\s]+)")
    path = p.sub("_", path)

    #PERL get_iplayer
    #$string =~ s/[^\w_\-\.\/\s]//gi if ! $opt->{whitespace};
    #
    # Similar to Perl code, however also exclude matching substition marker
    # characters < and >
    p = re.compile(r"([^\w_\-\.\/\s<>]+)")
    path = p.sub("", path)

    #PERL get_iplayer
    #$string =~ s/[\|\\\?\*\<\"\:\>\+\[\]\/]//gi if $opt->{fatfilename};
    #
    # Similar to Perl code, however exclude matching forward slash and 
    # substition marker characters < and >
    p = re.compile(r"([\|\\\?\*\"\:\+\[\]]+)")
    path = p.sub("", path)

    # Replace substitution marker characters < and >
    if include_substition_markers:
        p = re.compile(r"([<>]+)")
        path = p.sub("_", path)

    #PERL get_iplayer
    # Truncate multiple '_'
    #$string =~ s/_+/_/g;
    p = re.compile(r"([_]+)")
    path = p.sub("_", path)

    return path

def _move_file(categories, dirname, filename, subdir_format):
    logger.debug("Move \"{0}\" (categories = \"{1}\", dirname = \"{2}\", subdir_format = \"{3}\"".format(filename, categories, dirname, subdir_format))

    src_dirname = os.path.dirname(filename)

    # Perform additional substitution
    #NOTE Find substring
    if "<week>" in subdir_format:
        week_number = datetime.today().isocalendar()[1]
        subdir_format = subdir_format.replace("<week>", "{0:02}".format(week_number))

    if args.categories is not None:
        #AlTERNATIVE retrieve category name from the last subdirectory in @filename,
        #    which is formatted with the <categories> property value.
        #categories = os.path.basename(src_dirname)
        #specific_category = last_camel_case(categories)
        category_list = categories.split(",")
        # lstrip(): trim leading whitespaces
        specific_category = category_list[len(category_list) - 1].lstrip()
        main_category = category_list[0].lstrip()
 
        # Perform additional substitutions
        if main_category == specific_category:
            # Merge duplicate string values
            subdir_format = subdir_format.replace("<category><categorymain>", main_category)
            subdir_format = subdir_format.replace("<categorymain><category>", main_category)

            # Merge duplicate string values separated by sanitized separators or
            # other valid separator characters (-)
 
            subdir_format = _sanitize_path(subdir_format, False)
        
            #NOTE p.sub replaces that whole search string, not just the group in the search string
            #     --> use non-consuming, fixed-length lookaheads (?=...) and lookbehinds (?<=...)
            p = re.compile(r"(?<=<category>)([_-]+)(?=<categorymain>)|(?<=(?<=<categorymain>))([_-]+)(?=<category>)")
            subdir_format = p.sub(r"_", subdir_format)
            #ALTERNATIVE use only one group (the start/end pos won't be correct after the first substitution)
            #m = re.search(pattern, str)
            #if m and m.groups() > 0:
            #    str = str[0:m.start(1)] + replacement_str + str[m.end(1):len(str)]
            subdir_format = subdir_format.replace("<category>_<categorymain>", main_category)
            subdir_format = subdir_format.replace("<categorymain>_<category>", main_category)
        subdir_format = subdir_format.replace("<category>", specific_category)
        subdir_format = subdir_format.replace("<categorymain>", main_category)

    # Sanitize everything again, to sanitize the substituted values and unrecognized substitutions
    subdir_format = _sanitize_path(subdir_format, True)

    # Move the file
    try:
        dest_dirname = os.path.join(dirname, subdir_format)
        if not os.path.exists(dest_dirname):
            os.makedirs(dest_dirname)
        shutil.move(filename, dest_dirname)
        logger.info("Moved \"{0}\" to \"{1}\"".format(filename, dest_dirname))
    #NOTE Combined exception handling
    except (IOError, os.error, shutil.Error), why:
        logger.warning("Failed to move \"{0}\" to \"{1}\"".format(filename, dest_dirname))
        logger.debug(str(why))

    # Remove empty directory
    try:
        os.rmdir(src_dirname)
    except OSError:
        pass

def main():
    _init_argparser()
    _init_loggers()
    
    #NOTE If arg not required, then check e.g. args.filename is not None
    _move_file(args.categories[0], args.dir[0], args.filename[0], args.subdir_format[0])

if __name__ == "__main__":
    main()
