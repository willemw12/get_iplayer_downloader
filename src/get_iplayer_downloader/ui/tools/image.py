import os

from gi.repository import Gtk

from get_iplayer_downloader import settings
from get_iplayer_downloader.tools import file, markup

def image(url, timeout=0.0):
    """" Load and cache image from @url. """
    
    #TODO url: g_markup_escape_text() or g_markup_printf_escaped()
    url = markup.html2text(url)
    pathname = settings.TEMP_PATHNAME + os.sep + "images"
    if timeout <= 0.0:
        filename = file.load_url(url, pathname)
    else:
        filename = file.load_url(url, pathname, timeout=timeout)
    if filename is None:
        return None
    return Gtk.Image.new_from_file(filename)
