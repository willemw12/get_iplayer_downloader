#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import tempfile

from get_iplayer_downloader import search_cache

PROGNAME = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logger = logging.getLogger(PROGNAME)

DEFAULT_PROG_TYPE = "tv"
#NOTE Categories for radio and tv are the same
#DEFAULT_CATEGORIES = "childrens,comedy,drama,entertainment,learning,music,news,religionandethics,sport,weather"
DEFAULT_CATEGORIES = "news"
#DEFAULT_DAYS = 1
#DEFAULT_DAYS_OFFSET = 0

def _init_argparser():
    parser = argparse.ArgumentParser(description="Generate search result cache for get_iplayer_downloader from BBC web pages. Today's programmes may include programmes which are not yet available. Requires the 'lynx' command line web browser.")
    
    parser.add_argument("-d", "--debug", dest="debug", action="store_const", const=True, default=False, help="set log level to debug")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_const", const=True, default=False, help="set log level to fatal")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="set log level to info")
    #parser.add_argument("--debug-log-file", action="store_const", const=True, default=False, help="set log level to debug (log file only)")
    #parser.add_argument("--quiet-log-file", action="store_const", const=True, default=False, help="set log level to fatal (log file only)")
    #parser.add_argument("--verbose-log-file", action="store_const", const=True, default=False, help="set log level to info (log file only)")
    
    parser.add_argument("--categories", default=DEFAULT_CATEGORIES, help="<genre>,<subgenre>,...;<genre>.... For example, comedy,sitcoms;drama,crime;factual. Default: " + DEFAULT_CATEGORIES)
    #parser.add_argument("--channels", default="", help="")
    parser.add_argument("--clear-cache", action="store_const", const=True, default=False, help="clear cache instead of generating cache. See also --type")
    parser.add_argument("--fast", action="store_const", const=True, default=False, help="do not 'sleep' before downloading a web page (not recommended)")
    #parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="number of days to cache. 0 days is 'all available on iPlayer'. Default: %d" % DEFAULT_DAYS)
    #parser.add_argument("--days-offset", type=int, default=DEFAULT_DAYS_OFFSET, help="number of days from today to exclude from the cache. Default: %d" % DEFAULT_DAYS_OFFSET)
    parser.add_argument("--type", dest="prog_type", metavar="TYPE", default=DEFAULT_PROG_TYPE, help="programme types ('radio', 'tv', 'radio,tv', 'all'). Default: " + DEFAULT_PROG_TYPE)
    
    global args
    args = parser.parse_args()

# def _init_loggers():
#     logging.basicConfig(level=logging.WARNING)
#      
#     #formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
#     root_logger = logging.getLogger()
#  
#     ####
#     
#     file_logger = logging.getLogger("FILE")
#     log_pathname = tempfile.gettempdir()
#     log_filename = os.path.join(log_pathname, PROGNAME + ".log")
#     if not os.path.exists(log_pathname):
#         os.mkdir(log_pathname)
#     file_handler = logging.FileHandler(log_filename)
#      
#     # Set log level (log file only)
#     if args.debug_log_file:
#         file_handler.setLevel(logging.DEBUG)
#     elif args.verbose_log_file:
#         file_handler.setLevel(logging.INFO)
#     elif args.quiet_log_file:
#         file_handler.setLevel(logging.FATAL)        
#     
#     #TEST
#     file_handler.setLevel(logging.DEBUG)
#     
#     formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
#     file_handler.setFormatter(formatter)
#     root_logger.addHandler(file_handler)
#      
#     ####
#      
#     stream_logger = logging.getLogger("CONSOLE")
#     stream_handler = logging.StreamHandler()
#      
#     # Set log level (console only)
#     if args.debug:
#         stream_handler.setLevel(logging.DEBUG)
#     elif args.verbose:
#         stream_handler.setLevel(logging.INFO)
#     elif args.quiet:
#         stream_handler.setLevel(logging.FATAL)
#     
#     #TEST
#     stream_handler.setLevel(logging.INFO)
#     
#     #stream_handler.setFormatter(formatter)
#     root_logger.addHandler(stream_handler)

# def _init_loggers():
#     logging.basicConfig(level=logging.DEBUG)
#     
#     #formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
#     root_logger = logging.getLogger()
# 
#     ####
#     
#     log_pathname = tempfile.gettempdir()
#     log_filename = os.path.join(log_pathname, PROGNAME + ".log")
#     if not os.path.exists(log_pathname):
#         os.mkdir(log_pathname)
#     file_handler = logging.FileHandler(log_filename)
#     
#     # Set log level (log file only)
#     if args.debug_log_file:
#         file_handler.setLevel(logging.DEBUG)
#     elif args.verbose_log_file:
#         file_handler.setLevel(logging.INFO)
#     elif args.quiet_log_file:
#         file_handler.setLevel(logging.FATAL)        
#     
#     formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
#     file_handler.setFormatter(formatter)
#     root_logger.addHandler(file_handler)
#     
#     ####
#     
#     stream_handler = logging.StreamHandler()
#     
#     # Set log level (console only)
#     if args.debug:
#         stream_handler.setLevel(logging.DEBUG)
#     elif args.verbose:
#         stream_handler.setLevel(logging.INFO)
#     elif args.quiet:
#         stream_handler.setLevel(logging.FATAL)
#     
#     #stream_handler.setFormatter(formatter)
#     root_logger.addHandler(stream_handler)

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

def _main():
    _init_argparser()
    _init_loggers()
    
    if args.clear_cache:
        search_cache.clear_cache(args.prog_type)
    else:
        #search_cache.write_cache(args.prog_type, args.categories, args.days, args.days_offset, fast=args.fast)
        search_cache.write_cache(args.prog_type, args.categories, fast=args.fast)

if __name__ == "__main__":
    _main()
