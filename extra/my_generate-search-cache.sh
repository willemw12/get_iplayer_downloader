#!/bin/sh

#/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=radio,tv --categories="childrens;comedy;drama;entertainment;factual;learning" --verbose
/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=radio --categories="comedy;drama;factual;learning" --verbose
/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=tv    --categories="comedy;drama;entertainment;factual;learning" --verbose

