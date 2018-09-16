# """ Precache episode search results for get_iplayer_downloader. Uses only web pages as information source. """
# """ This is a slow and inefficient method of programme data retrieval. """

#ISSUE subcategories
# The only purpose of the _search_results_main_category() method was to collect the subcategories (or the first subcategory)
# The subcategories under 'Filter by' are not all the subcategories. Besides genre and subgenres, there is also formats (Comedy,Games & Quizes)

import logging
import os
import pickle
import re
#import sys
import traceback
import urllib.parse     #, urllib.error

from datetime import datetime, timedelta
from enum import Enum
from get_iplayer_downloader.tools import command

#TODO circular import
#from get_iplayer_downloader.get_iplayer import SearchResultColumn
class SearchResultColumn:
    DOWNLOAD = 0
    PID = 1
    INDEX = 2
    SERIES = 3
    EPISODE = 4
    CATEGORIES = 5
    CHANNELS = 6
    THUMBNAIL_SMALL = 7
    AVAILABLE = 8
    DURATION = 9
    LOCATE_SEARCH_TERM = 10

from random import randrange
from time import sleep

# Load application-wide definitions
import get_iplayer_downloader

logger = logging.getLogger(__name__)

if os.name == "posix":
    SEARCH_RESULT_CACHE_PATHNAME = os.path.join(os.path.expanduser("~"), ".cache", get_iplayer_downloader.PROGRAM_NAME)
else:
    SEARCH_RESULT_CACHE_PATHNAME = os.path.join(os.path.expanduser("~"), get_iplayer_downloader.PROGRAM_NAME)

#PICKLE_PROTOCOL_HUMAN_READABLE=0

MIN_TIMEOUT_MS=1000
MAX_TIMEOUT_MS=6000

RETRY_COUNT=3

PROG_TYPE_LIST = ["radio", "tv"]

#LYNX_DUMP_CMD = "lynx -dump -list_inline -width=1024 -useragent='Mozilla/5.0 (X11; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0' "
LYNX_DUMP_CMD = "lynx -dump -list_inline -width=1024 "

#class ParseState:            # Python < 3.4
class ParseState(Enum):
    READY = 0
    BUSY = 1
    STOPPED = 2

def _find(f, seq):
    """ Return first item in sequence where f(item) == True. """
    for item in seq:
        if f(item): 
            return item

def _index(f, seq):
    """ Return first item index in sequence where f(item) == True. """
    for item in seq:
        if f(item): 
            return seq.index(item)
    return -1

#def _lsubstring(s, sep):
#    return s if s.find(sep) == -1 else s.split(sep, 1)[0]

def _rsubstring(s, sep):
    return "" if s.find(sep) == -1 else s.split(sep, 1)[1]

# def _regex_matches(regex, string):
#     return re.search(regex, string) is not None

def _regex_substring(regex, string):
    #pattern = re.compile(regex)
    #result = pattern.search(string)
    result = re.search(regex, string)
    return result.group(1) if result is not None else None

def _http_dump(url):
    process_output = None
    for unused_retry in range(RETRY_COUNT):
        process_output = command.run(LYNX_DUMP_CMD + url, ignore_returncode=True)
        if process_output is not None and (
                    "Error 500 - Internal Error" not in process_output or
                    "Sorry, the server encountered a problem" not in process_output):
            break
        logger.debug("Retry command")
        sleep(randrange(MAX_TIMEOUT_MS, MAX_TIMEOUT_MS * 2) / 1000.0)
        process_output = None
    return process_output

# #TEMP use of SearchResultColumn.LOCATE_SEARCH_TERM
# def _keyfunc(line):
#     series = line[SearchResultColumn.SERIES] if line[SearchResultColumn.SERIES] is not None else ""
#     if series is not None:
#         # Top / series level
#         episode = line[10] if line[10] is not None else ""
#         key = "1" + series + episode
#     else:
#         # Sub / episode level
#         series = line[SearchResultColumn.LOCATE_SEARCH_TERM] if line[SearchResultColumn.LOCATE_SEARCH_TERM] is not None else ""
#         episode = line[SearchResultColumn.EPISODE] if line[SearchResultColumn.EPISODE] is not None else ""
#         key = "2" + series + episode
#     return key

#DOUBLE
def _split(string, sep):
    """ Split at @sep, except if split string starts with a space character, i.e. is part of a split string containing @sep. @sep is a single character """
    if string is None:
        pass
    l = string.split(sep)
    r = []
    for i, e in enumerate(l):
        if i > 0 and i < len(l) -1 and l[i].startswith(" "):
            r[len(r) -1] += sep + e
        else:
            r.append(e)
    return r
    
def _merge_categories(categories1, categories2):
    category_list1 = _split(categories1, ',')
    category_list2 = _split(categories2, ',')
    subcategory_list1 = category_list1[1:]
    subcategory_list2 = category_list2[1:]
    subcategory_list1.extend(subcategory_list2)
    #NOTE Cannot perform "[:1]" and "extend()" in one statement
    #category_list1[:1].extend(sorted(set(subcategory_list1)))
    category_list1 = category_list1[:1]
    category_list1.extend(sorted(set(subcategory_list1)))
    return ",".join(category_list1)

#DOUBLE Partly with _search_results_category()
def _search_results_all_available_episodes(url, categories, series, search_result_lines, is_format_url=False, fast=False):
    """ Collect episode search results of a series. """
    
    #search_result_lines = []

    skip_lines = 0

    next_page_url = url
    while next_page_url is not None:
        url = next_page_url
        next_page_url = None

        episodes_parse_state = ParseState.READY
        next_page_parse_state = ParseState.READY

        process_output = _http_dump(url)
        if process_output is None:
            break

        lines = process_output.splitlines()
        for i, line in enumerate(lines):
            if skip_lines > 0:
                skip_lines -= 1
                continue
            #if not line:
            #    # Skip empty lines
            #    continue
     
            #line_stripped = line.strip()
            
            # Check for "start read" triggers
            #if episodes_parse_state == ParseState.READY and line.endswith("Episodes Available now"):
            if episodes_parse_state == ParseState.READY and line.endswith("Available now"):
                # Found start of episode list ("^[")
                episodes_parse_state = ParseState.BUSY
                continue
    
            # Check for "end read" triggers (in case of lists)
            if episodes_parse_state == ParseState.BUSY and len(search_result_lines) > 0 and re.search("4\. .*Next$", line) is not None:    # re.compile()
                # Found previous/next page link list
                #       4. [https://www.bbc.co.uk/programmes/xxxxxxxx/episodes/player?page=2]Next
                #       4. Next
                episodes_parse_state = ParseState.STOPPED
                next_page_parse_state = ParseState.BUSY
                #NOT continue
            elif next_page_parse_state == ParseState.BUSY and line == "":
                # Found empty line after previous/next page link list
                next_page_parse_state = ParseState.STOPPED
                continue
            
            # Read data 
            if episodes_parse_state == ParseState.BUSY:
                if line.startswith("["):
                    pid = _regex_substring("^\[(.*)\]", line)
                    
                    # Convert url pid to pid. If pid is a url, get the last part of the url path
                    # This is done in order to detect if an episode is already in the download history, when queuing an episode
                    pid = os.path.basename(urllib.parse.urlsplit(pid).path)
                
                    if series is not None:
                       episode = _regex_substring("\](.*)$", line)
                    else:
                       series = _regex_substring("\](.*)$", lines)
                       episode = series

                    #TODO Episode description: concatenate all lines, up to the first line starting with a link ("^[ ]*\[")
                    episode = episode + " ~ " + lines[i + 1].strip()

                    #TODO Get channel name from the next line staring with a link ("^[ ]*\[")
                    #TODO Strip "except ..."
                    channel = ""

                    # Skip duplicate episodes
                    #if pid not in [line[SearchResultColumn.PID] for line in search_result_lines]:
                    #found_line = None
                    #for l in search_result_lines:
                    #    if l[SearchResultColumn.PID] == pid:
                    #        found_line = l
                    #        break
                    found_line = _find(lambda line: line[SearchResultColumn.PID] == pid, search_result_lines)
                    if found_line:
                        logger.info("episode = %s|%s|%s|%s|%s (episode already found)" % (series, episode, categories, channel, pid))
                        # Add subcategory to existing episode categories
                        #logger.debug(...)
                        #found_line[SearchResultColumn.CATEGORIES] += ",%s" % category2
                        #
                        #subcategories = _rsubstring(categories, ',')
                        #if subcategories:
                        #    found_line[SearchResultColumn.CATEGORIES] += ",%s" % subcategories
                        found_line[SearchResultColumn.CATEGORIES] = _merge_categories(found_line[SearchResultColumn.CATEGORIES], categories)
                    else:
                        # Add episode
                        # Don't add if url is a format url

                        #ISSUE in case of subcategory support:
                        # when episode is in 'format', but episode not in one of the 'Filter by' filters
                        # For example, "Act your age": Games & Quizes --> Comedy,Games & Quizes

                        if not is_format_url:
                            found_index = _index(lambda line: line[SearchResultColumn.SERIES] == series, search_result_lines)
                            if found_index >= 0:
                                search_result_lines.insert(found_index + 1,
                                   [False, 
                                    pid, 
                                    None, 
                                    None, 
                                    episode, 
                                    categories,
                                    channel, 
                                    None,
                                    None, 
                                    None, 
                                    None])
                                    #series])    #TEMP
                            else:
                                logger.info("episode = %s|%s|%s|%s|%s" % (series, episode, categories, channel, pid))
                                search_result_lines.append(
                                   [False, 
                                    None, 
                                    None, 
                                    series, 
                                    None, 
                                    categories, 
                                    None, 
                                    None, 
                                    None,
                                    None, 
                                    None])
                                    #episode])   #TEMP
                                search_result_lines.append(
                                   [False, 
                                    pid, 
                                    None, 
                                    None, 
                                    episode, 
                                    categories,
                                    channel, 
                                    None,
                                    None, 
                                    None, 
                                    None])
                                    #series])    #TEMP
                    skip_lines = 3
                #continue
            elif next_page_parse_state == ParseState.BUSY:
                next_page_url = _regex_substring("\[(.*)\]Next", line)
                next_page_parse_state = ParseState.STOPPED
                break

        if not fast:
            sleep(randrange(MIN_TIMEOUT_MS, MAX_TIMEOUT_MS) / 1000.0)

        # Reached end of single page
        if next_page_parse_state == ParseState.READY:
            next_page_url = None
            episodes_parse_state = ParseState.STOPPED
            next_page_parse_state = ParseState.STOPPED

    ####

    if episodes_parse_state != ParseState.STOPPED:
        logger.error("Episodes not found in %s" % url)
        #sys.exit(1)
    if next_page_parse_state != ParseState.STOPPED:
        logger.error("Next page link not found in %s" % url)
        #sys.exit(1)

    ####
    
    ###keyfunc = lambda items: items[3] + items[4]
    ##return sorted(search_result_lines, key=_keyfunc)
    
    #return search_result_lines

def _search_results_category(url, search_result_lines, is_format_url=False, fast=False):
    """ Collect episode search results of a single category (either main or subcategory). """
    
    #search_result_lines = []

    skip_lines = 0

    next_page_url = url
    while next_page_url is not None:
        url = next_page_url
        next_page_url = None
        categories = None

        categories_parse_state = ParseState.READY
        episodes_parse_state = ParseState.READY
        next_page_parse_state = ParseState.READY

        process_output = _http_dump(url)
        if process_output is None:
            break

        lines = process_output.splitlines()
        for i, line in enumerate(lines):
            if skip_lines > 0:
                skip_lines -= 1
                continue
            #if not line:
            #    # Skip empty lines
            #    continue
     
            #line_stripped = line.strip()
            
            # Check for "start read" triggers
            if categories_parse_state == ParseState.READY and line and not line.startswith(" ") and line.strip() != "Accessibility links":
                # Found header of main category section
                categories_parse_state = ParseState.BUSY
                #NOT continue
            #elif categories_parse_state == ParseState.STOPPED and episodes_parse_state == ParseState.READY and _regex_substring("^\[http://www.bbc.co.uk/iplayer/episode/.*\]", lines) is not None:
            #    # Found start of episode list ("^[")
            #    episodes_parse_state = ParseState.BUSY
            #    continue
            elif categories_parse_state == ParseState.STOPPED and episodes_parse_state == ParseState.READY and line.startswith("["):
                # Found start of episode list ("^[")
                episodes_parse_state = ParseState.BUSY
                #NOT continue
    
            # Check for "end read" triggers (in case of lists)
            if episodes_parse_state == ParseState.BUSY and len(search_result_lines) > 0 and re.search("4\. .*Next$", line) is not None:    # re.compile()
                # Found previous/next page link list ("1.")
                #       4. [https://www.bbc.co.uk/programmes/xxxxxxxx/episodes/player?page=2]Next
                #       4. Next
                episodes_parse_state = ParseState.STOPPED
                next_page_parse_state = ParseState.BUSY
                #NOT continue
            elif next_page_parse_state == ParseState.BUSY and line == "":
                # Found empty line after previous/next page link list
                next_page_parse_state = ParseState.STOPPED
                continue
            
            # Read data 
            if categories_parse_state == ParseState.BUSY and line != "":
                # Found first non-empty line
                
                # Get the category name(s) from, for example:
                #     [http://www.bbc.co.uk/radio/categories]Categories: Comedy
                #     [http://www.bbc.co.uk/radio/categories]Categories: [http://www.bbc.co.uk/radio/categories/comedy?sort=-available_from_date]Comedy: Sitcoms             
                result = re.search("^\[.*\](.*): (.*)", line)
                if result is None:
                    break
                category1 = result.group(1) if result is not None else None
                category2 = result.group(2) if result is not None else None
                if category1 is None or category2 is None:
                    #logger.fatal("Categories not found in %s" % url)
                    #sys.exit(1)
                    break

                # Get the category name from, for example:
                #     Comedy
                #if result is None:
                #    category1 = None
                #    category2 = line

                if category1 is None or category1 == "Categories":
                    # There are no subcategories
                    categories = "%s" % (category2)
                else:
                    categories = "%s,%s" % (category1, category2)
                logger.info("categories = %s" % categories)
                categories_parse_state = ParseState.STOPPED
                #continue
            elif episodes_parse_state == ParseState.BUSY:
                if line.startswith("["):
                    # Found an episode ("^[")
                    series = _regex_substring("\](.*)", line)
                else:
                    #if line.startswith("   [http://www.bbc.co.uk/programmes/") and ...
                    result = re.search("\[http://www.bbc.co.uk/programmes/.*/episodes\]", line)
                    if result is not None:
                        # Found link to episodes
                        available_episodes_url = _regex_substring("\[(.*)\]", line)
                        if available_episodes_url is not None:
                            _search_results_all_available_episodes(available_episodes_url, categories, series, search_result_lines, is_format_url=False, fast=False)
            elif next_page_parse_state == ParseState.BUSY:
                next_page_url = _regex_substring("\[(.*)\]Next", line)
                next_page_parse_state = ParseState.STOPPED
                break

        # Reached end of single page
        if next_page_parse_state == ParseState.READY:
            next_page_url = None
            episodes_parse_state = ParseState.STOPPED
            next_page_parse_state = ParseState.STOPPED

    ####

    if categories_parse_state != ParseState.STOPPED:
        logger.error("Categories not found in %s" % url)
        #sys.exit(1)
    if episodes_parse_state != ParseState.STOPPED:
        logger.error("Episodes not found in %s" % url)
        #sys.exit(1)
    if next_page_parse_state != ParseState.STOPPED:
        logger.error("Next page link not found in %s" % url)
        #sys.exit(1)

    ####
    
    ###keyfunc = lambda items: items[3] + items[4]
    ##return sorted(search_result_lines, key=_keyfunc)
    
    #return search_result_lines

def clear_cache(prog_type):
    if prog_type == "all":
        prog_type_list = PROG_TYPE_LIST
    else:
        prog_type_list = prog_type.split()
    for prog_type in prog_type_list:
        try:
            cache_file = os.path.join(SEARCH_RESULT_CACHE_PATHNAME, prog_type + ".pickle")
            os.remove(cache_file)
        except FileNotFoundError:
            pass
        except:
            traceback.print_exc()
    
#def write_cache(prog_type, categories, days, days_offset, fast=False):
def write_cache(prog_type, categories, fast=False):
    if prog_type == "all":
        prog_type_list = PROG_TYPE_LIST
    else:
        prog_type_list = prog_type.split()
    for prog_type in prog_type_list:
        url_genre_template = "http://www.bbc.co.uk/%(prog_type)s/categories/%(subgenre)s?sort=-available_from_date"
        url_subgenre_template = "http://www.bbc.co.uk/%(prog_type)s/categories/%(genre)s-%(subgenre)s?sort=-available_from_date"

        search_result_lines = []
        
        categories_list = categories.split(";")
        for categories2 in categories_list:
            category_list = categories2.split(",")

            main_category = category_list[0]
            subcategories = category_list[1:]
            if len(subcategories) > 0:
                # Main category with subcategories
                for subcategory in subcategories:
                    url_dict = dict(prog_type=prog_type, genre=main_category.lower(), subgenre=subcategory.lower())
                    url = url_subgenre_template % url_dict
                    _search_results_category(url, search_result_lines)
            else:
                # Main category without subcategories
                url_dict = dict(prog_type=prog_type, genre=main_category.lower())
                url = url_genre_template % url_dict
                _search_results_category(url, search_result_lines)

        if not os.path.exists(SEARCH_RESULT_CACHE_PATHNAME):
            os.mkdir(SEARCH_RESULT_CACHE_PATHNAME)
            
        cache_file = os.path.join(SEARCH_RESULT_CACHE_PATHNAME, prog_type + ".pickle")
        with open(cache_file, "wb") as f:
            #pickle.dump(search_result_lines, f, pickle=pickle.HIGHEST_PROTOCOL)
            pickle.dump(search_result_lines, f)

def has_cache(prog_type):
    cache_file = os.path.join(SEARCH_RESULT_CACHE_PATHNAME, prog_type + ".pickle")
    return os.path.exists(cache_file)

def get(prog_type):
    """ Return cached search result for type @prog_type. """
    
    cache_file = os.path.join(SEARCH_RESULT_CACHE_PATHNAME, prog_type + ".pickle")
    if not os.path.exists(cache_file):
        return None
    
    with open(cache_file, "rb") as f:
        return pickle.load(f)

