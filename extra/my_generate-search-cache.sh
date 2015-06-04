#!/bin/sh

if [ $# -lt 1 ]; then
  echo "$(basename $0): number of days missing"
  echo "usage: $(basename $0) <days>"
  exit 1
fi

DAYS="$1"

#/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=radio,tv --categories="childrens;comedy;drama;entertainment;factual;learning" --days="$DAYS" --verbose
/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=radio --categories="childrens;comedy;drama;factual;learning" --days="$DAYS" --verbose
/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=tv    --categories="childrens;comedy;drama;entertainment;factual;learning" --days="$DAYS" --verbose

