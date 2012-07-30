import os
import socket
import sys
import traceback
import urllib.request, urllib.parse     #, urllib.error

def load_url(url, pathname, **urlopen_keywords):
    """ Download file @url to folder @pathname. @urlopen_keywords are for urllib.request.urlopen(): "timeout" keyword in seconds """

    if not os.path.exists(pathname):
        os.makedirs(pathname)
    
    filename = pathname + os.sep + os.path.basename(urllib.parse.urlsplit(url).path)
    if not os.path.isfile(filename):
        stream = None
        try:
            stream = urllib.request.urlopen(url, **urlopen_keywords)
        #NOTE Some timeout exceptions are not caught by URLError:
        #    File "/usr/lib/python3.2/socket.py", line 276, in readinto
        #NOTE Combined exception handling
        except (urllib.error.URLError, socket.timeout): # as exc:
            #sys.stderr.write("{0}:load_url(): {1}\n".format(__name__, exc))
            traceback.print_exc(file=sys.stderr)
            return None
        #except ValueError: invalid URL
            
        #NOTE Do not add "os." at the beginning of these I/O methods
        with open(filename, "wb") as file:
            file.write(stream.read())
        #ALTERNATIVE
        #file = open(filename, "wb")
        #file.write(stream.read())
        #file.close()

        if stream is not None:
            stream.close()

    return filename

def files2urls(filepath):
    """ Return a string containing a url to the folder @filepath and the filenames inside @filepath (one level deep), sorted by file name. """

    basename = os.path.basename(filepath)
    url = "<a href=\"file://" + filepath + "\" title=\"get_iplayer " + basename + " configuration folder\">" + basename + "</a>"
    for dirpath, unused_dirnames, filenames in os.walk(filepath):
        # Skip empty and subfolders
        if len(filenames) > 0 and filepath == dirpath:
            filenames.sort()
            url += " ("
            for i, filename in enumerate(filenames):
                # Skip filenames created by get_iplayer --pvrqueue
                if not filename.startswith("ONCE_"):
                    url += "<a href=\"file://" + os.path.join(filepath, filename) + "\" title=\"get_iplayer " + basename + " configuration file\">" + filename + "</a>"
                    if (i < len(filenames) - 1):
                        url += ", "
            url += ")"
    return url
    #ALTERNATIVE ways of sorting a list of filenames in a folder: glob(<filename filter>); listdir()
