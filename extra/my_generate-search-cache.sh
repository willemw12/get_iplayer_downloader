#!/bin/sh

if [ $# -lt 1 ]; then
  echo "$(basename $0): number of days missing"
  echo "usage: $(basename $0) <days>"
  exit 1
fi

DAYS="$1"

#/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=radio,tv --categories=Childrens,Comedy,Drama,Entertainment,Factual,Learning --days="$DAYS" --verbose
/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=radio --categories=Childrens,Comedy,Drama,Factual,Learning --days="$DAYS" --verbose
/usr/share/get_iplayer_downloader/scripts/generate_search_cache.py --type=tv    --categories=Childrens,Comedy,Drama,Entertainment,Factual,Learning --days="$DAYS" --verbose

