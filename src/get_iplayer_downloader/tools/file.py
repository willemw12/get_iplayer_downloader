import os
import urllib.request, urllib.parse     #, urllib.error

def load_url(url, pathname):
    """ Download file @url to folder @pathname """
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    
    filename = pathname + os.sep + os.path.basename(urllib.parse.urlsplit(url).path)
    if not os.path.isfile(filename):
        stream = urllib.request.urlopen(url)
    
        #NOTE Do not add "os." at the beginning of these I/O methods
        fp = open(filename, "wb")
        fp.write(stream.read())
        fp.close()
        #ALTERNATIVE
        #with open(filename, "w") as fp:
        #    fp.write(stream.read())
        #b = fp.closed()
        
        stream.close()
    return filename
