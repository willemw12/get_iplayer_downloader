#!/usr/bin/env python3

import argparse
import glob
import logging
import os
import sys
import re
import shutil
import tempfile

from datetime import datetime

from get_iplayer_downloader.tools import file

# List is based on based on 'sub genres' in get_iplayer
GENRES = [
    "Children's",
    "Comedy",
    "Drama",
    "Entertainment",
    "Factual",
    "Learning",
    "Weather",
    "Music",
    "News",
    "Religion & Ethics",
    "Sport",
    "Weather",
]

# List is based on based on 'sub subgenres' in get_iplayer
SUBGENRES = [
    # childrens
    "Activities",
    "Drama", 
    "Entertainment & Comedy", 
    "Factual", 
    "Music", 
    "News", 
    "Sport",
    
    # comedy
    "Character", 
    "Impressionists", 
    "Music", 
    "Satire", 
    "Sitcoms", 
    "Sketch", 
    "Spoof", 
    "Standup", 
    "Stunt",
    
    # drama
    "Action & Adventure", 
    "Biographical", 
    "Classic & Period", 
    "Crime", 
    "Historical", 
    "Horror & Supernatural",
    "Legal & Courtroom", 
    "Medical", 
    "Musical", 
    "Political",
    "Psychological",
    "Relationships & Romance",
    "SciFi & Fantasy",
    "Soaps",
    "Spiritual",
    "Thriller",
    "War & Disaster",
    "Western",

    # entertainment
    "Variety Shows",
    
    # factual
    "Antiques",
    # Also including comma
    "Arts Culture & the Media", "Arts, Culture & the Media",
    "Beauty & Style",
    "Cars & Motors",
    "Consumer",
    "Crime & Justice",
    "Disability",
    "Families & Relationships",
    "Food & Drink",
    "Health & Wellbeing",
    "History",
    "Homes & Gardens",
    "Life Stories",
    "Money",
    "Pets & Animals",
    "Politics",
    "Science & Nature",
    "Travel",
    
    # learning
    "Adults",
    "Pre-School",
    "Primary",
    "Secondary",
    
    # music
    "Classic Pop & Rock",
    "Classical",
    "Country",
    "Dance & Electronica",
    "Desi",
    # Also including comma
    "Easy Listening Soundtracks & Musicals", "Easy Listening, Soundtracks & Musicals",
    "Folk",
    # Also including comma
    "Hip Hop RnB & Dancehall", "Hip Hop, RnB & Dancehall",
    "Jazz & Blues",
    "Pop & Chart",
    "Rock & Indie",
    "Soul & Reggae",
    "World",
    
    #news

    #religionandethics
    
    # sport => {
    "Alpine Skiing",
    "American Football",
    "Archery",
    "Athletics",
    "Badminton",
    "Baseball",
    "Basketball",
    "Beach Volleyball",
    "Biathlon",
    "Bobsleigh",
    "Bowls",
    "Boxing",
    "Canoeing",
    "Commonwealth Games",
    "Cricket",
    "Cross Country Skiing",
    "Curling",
    "Cycling",
    "Darts",
    "Disability Sport",
    "Diving",
    "Equestrian",
    "Fencing",
    "Figure Skating",
    "Football",
    "Formula One",
    "Freestyle Skiing",
    "Gaelic Games",
    "Golf",
    "Gymnastics",
    "Handball",
    "Hockey",
    "Horse Racing",
    "Ice Hockey",
    "Judo",
    "Luge",
    "Modern Pentathlon",
    "Motorsport",
    "Netball",
    "Nordic Combined",
    "Olympics",
    "Rowing",
    "Rugby League",
    "Rugby Union",
    "Sailing",
    "Shinty",
    "Shooting",
    "Short Track Skating",
    "Skeleton",
    "Ski Jumping",
    "Snooker",
    "Snowboarding",
    "Softball",
    "Speed Skating",
    "Squash",
    "Swimming",
    "Synchronised Swimming",
    "Table Tennis",
    "Taekwondo",
    "Tennis",
    "Triathlon",
    "Volleyball",
    "Water Polo",
    "Weightlifting",
    "Winter Olympics",
    "Winter Sports",
    "Wrestling",

    # weather
]

# # List is based on based on 'sub formats' in get_iplayer
# FORMATS = [
#     "Animation",
#     "Appeals",
#     "Bulletins",
#     "Discussion & Talk",
#     "Docudramas",
#     "Documentaries",
#     "Films",
#     "Games & Quizzes",
#     "Magazines & Reviews",
#     "Makeovers",
#     "Performances & Events",
#     "Phone-ins",
#     "Readings",
#     "Reality",
#     "Talent Shows",
# ]

PROGNAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logger = logging.getLogger(PROGNAME)

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
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""This is a get_iplayer post-processing script. It is an extension to the
get_iplayer "subdir" output option. In addition to the formatting fields
listed by "get_iplayer --info ...", this script supports:

  <categorysub>         last category from --categories
  <categorymain>        first category from --categories
  <week>                current week number

Arguments --categories, --dir and --filename are there to transfer values from 
get_iplayer to this script and are usually always specified as:

  --categories="<categories>" --dir="<dir>" --filename="<filename>"

Forward-slashes in --subdir need to be escaped by an extra forward-slash.

A get_iplayer "command" option example (one line):

  command get_iplayer_post_subdir.py 
                        --categories="<categories>"
                        --dir="<dir>" 
                        --filename="<filename>" 
                        --force
                        --subdir-format=
                            "bbc.<week>//<categorymain>_<categorysub>//<longname>"
""")
    
    #AlTERNATIVE retrieve category name from subdir
    #        subdir 1
    #        subdir-format <categories>
    
    parser.add_argument("-d", "--debug", dest="debug", action="store_const", const=True, default=False, help="set log level to debug")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_const", const=True, default=False, help="set log level to fatal")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="set log level to info")
    parser.add_argument("--categories", dest="categories", metavar="<categories>", nargs=1, default=None, help="programme categories (comma-separated list) of the downloaded file. Expected when <category>, <categorymain> or <categorysub> is in --subdir-format")
    parser.add_argument("--dir", dest="dir", metavar="<pathname>", nargs=1, default=None, required=True, help="output directory")
    parser.add_argument("--filename", dest="filename", metavar="<filename>", nargs=1, default=None, required=True, help="downloaded file to be moved")
    parser.add_argument("--force", dest="force", action="store_const", const=True, default=False, help="overwrite existing destination file")
    parser.add_argument("--subdir-format", dest="subdir_format", metavar="<format>", nargs=1, default=None, required=True, help="subdirectory path")
    #parser.add_argument("filename", nargs=1)
    #parser.add_argument("categories", nargs=1)
    global args
    args = parser.parse_args()

def _init_loggers():
    logging.basicConfig(level=logging.WARNING)

    log_pathname = tempfile.gettempdir()
    log_filename = os.path.join(log_pathname, PROGNAME + ".log")
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

def _split(string, sep):
    """ Split at @sep, except if split string starts with a space character, i.e. is part of a split string containing @sep. @sep is a single character """
    l = string.split(sep)
    r = []
    for i, e in enumerate(l):
        if i > 0 and i < len(l) -1 and l[i].startswith(" "):
            #r[i - 1] += e
            r[i - 1] += sep + e
        else:
            r.append(e)
    return r
        
def _main_categories(category_list):
    main_categories_list = []
    #if len(category_list) > 1:
    for category in category_list:
        #if category in FORMATS:
        #    # Skip format
        #    continue
        if category in GENRES:
            main_categories_list.append(category)
    ##return ",".join(sorted(main_categories_list))
    #main_categories_list.sort()
    #return "_".join(main_categories_list)

    return sorted(main_categories_list)

def _sub_categories(category_list):
    sub_categories_list = []
    #if len(category_list) > 1:
    for category in category_list:
        #if category in FORMATS:
        #    # Skip format
        #    continue
        if category in SUBGENRES:
            sub_categories_list.append(category)
            
    ##return ",".join(sorted(sub_categories_list))
    #sub_categories_list.sort()
    #return "_".join(sub_categories_list)

    return sorted(sub_categories_list)

def _move_file(categories, dirname, filename, force, subdir_format):
    logger.debug("move_file(): filename = \"{0}\", categories = \"{1}\", dirname = \"{2}\", force = {3}, subdir_format = \"{4}\"".format(filename, categories, dirname, force, subdir_format))

    src_dirname = os.path.dirname(filename)

    # Perform additional substitution (field formatting)
    
    # Path separators are escaped ('//').
    # For example <longname> in '--subdir-format="...<longname>"' can contain '/' characters
    subdir_format = subdir_format.replace("//", "/")
    
    #NOTE Find substring
    if "<week>" in subdir_format:
        week_number = datetime.today().isocalendar()[1]
        subdir_format = subdir_format.replace("<week>", "{0:02}".format(week_number))

    if categories is not None:
        #AlTERNATIVE retrieve category name from the last subdirectory in @filename,
        #    which is formatted with the <categories> property value.
        #categories = os.path.basename(src_dirname)
        #sub_category = last_camel_case(categories)
        #
        #category_list = categories.split(",")
        category_list = _split(categories, ",")
        # lstrip(): trim leading whitespaces
        #sub_category = category_list[len(category_list) - 1].lstrip()         # Last in the list

        main_category_list = _main_categories(category_list)
        # Some main categories names are also subcategory names.
        # Remove all main categories to avoid repeating them in the subcategories
        category_list = list(set(category_list) - set(main_category_list))
        sub_category_list = _sub_categories(category_list)

        main_categories = "_".join(main_category_list)
        sub_categories = "_".join(sub_category_list)
 
        # Perform additional substitutions (field formatting)
        if main_categories == sub_categories or sub_categories == "":
            # <category> is the same as <categorymain>
            subdir_format = subdir_format.replace("<category>", "<categorymain>")

            # Merge duplicate string values
            subdir_format = subdir_format.replace("<categorysub><categorymain>", main_categories)
            subdir_format = subdir_format.replace("<categorymain><categorysub>", main_categories)

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
            subdir_format = subdir_format.replace("<categorysub>_<categorymain>", main_categories)
            subdir_format = subdir_format.replace("<categorymain>_<categorysub>", main_categories)
        subdir_format = subdir_format.replace("<categorysub>", sub_categories)
        subdir_format = subdir_format.replace("<categorymain>", main_categories)
    else:
        if "<category>" in subdir_format or "<categorymain>" in subdir_format or "<categorysub>" in subdir_format:
            logger.warning("move_file(): --categories expected when <category>, <categorymain>  and/or <categorysub> is in --subdir-format")
            #sys.exit(1)

    # Sanitize everything in subdir again, to sanitize the substituted values and unrecognized substitutions (field formatting)
    subdir_format = file.sanitize_path(subdir_format, True)

    try:
        if filename.endswith(".wma"):
            # Get all wma part filenames
            pathname_wma = filename[:len(filename)-4] + "_part*.wma"    # "_part??.wma"
            filenames = glob.glob(pathname_wma)
            if len(filenames) == 1:
                # Rename <filename>_part01.wma to <filename> if there is only one wma part file
                filename_wma = filenames[0]
                logger.info("move_file(): Move \"{0}\" to \"{1}\"".format(filename_wma, filename))
                shutil.move(filename_wma, filename)
                
                filenames = [filename]
        else:
            filenames = [filename]

        # Move file(s)
        dest_dirname = os.path.join(dirname, subdir_format)
        for filename in filenames:
            logger.info("move_file(): Move \"{0}\" to \"{1}\"".format(filename, dest_dirname))
            if not os.path.exists(dest_dirname):
                os.makedirs(dest_dirname)
            if force:
                try:
                    basename = os.path.basename(filename)
                    dest_filename = os.path.join(dest_dirname, basename)
                    os.remove(dest_filename)
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
