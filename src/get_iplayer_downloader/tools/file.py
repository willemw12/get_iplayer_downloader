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
        #NOTE some timeout exceptions are not caught by URLError:
        #    File "/usr/lib/python3.2/socket.py", line 276, in readinto
        #except urllib.error.URLError as exc:
        except (urllib.error.URLError, socket.timeout): # as exc:
            #sys.stderr.write("%s:load_url(): %s\n" % (__name__, exc))
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
