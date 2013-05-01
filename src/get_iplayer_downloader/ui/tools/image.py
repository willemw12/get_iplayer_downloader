import os

from gi.repository import Gtk

from get_iplayer_downloader import settings
from get_iplayer_downloader.tools import file, markup

def image(url, timeout=0.0, max_width=-1, max_height=-1):
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
    image = Gtk.Image.new_from_file(filename)

    pixbuf = image.get_pixbuf()
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    if width > max_width or height > max_height:
        #TODO rescale/resize image
        return None

    return image
