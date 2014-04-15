import os
import re
import socket
import sys
import traceback
import urllib.request, urllib.parse     #, urllib.error

def load_url(url, pathname, **urlopen_keywords):
    """ Download file @url to folder @pathname. 
        @urlopen_keywords are for urllib.request.urlopen(): "timeout" keyword in seconds    
    """

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
    """ Return a string containing a url to the folder @filepath and 
        the filenames inside @filepath (one level deep), sorted by file name.
    """

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

def sanitize_path(path, include_substitution_markers):
    """ Sanitize file name path @path, similar to the get_iplayer rules.
        @include_substitution_markers: include substitution marker characters < and > in the sanitization process    
    """

    # Partly based on 'sub StringUtils::sanitize_path' in get_iplayer
    r"""
    sub StringUtils::sanitize_path {
        my $string = shift;
        my $is_path = shift || 0;
        # (1) Replace leading/trailing ellipsis with _
        $string =~ s/(^\.+|\.+$)/_/g;
        # (2) Replace forward slashes with _ if not path
        $string =~ s/\//_/g unless $is_path;
        # (3) Replace backslashes with _ if not Windows path
        $string =~ s/\\/_/g unless $^O eq "MSWin32" && $is_path;
        # (4) Remove extra/leading/trailing whitespace
        $string =~ s/\s+/ /g;
        $string =~ s/(^\s+|\s+$)//g;
        # (5) Replace whitespace with _ unless --whitespace
        $string =~ s/\s+/_/g unless $opt->{whitespace};
        # (6) Truncate multiple replacement chars
        $string =~ s/_+/_/g;
        # (7) Remove non-ASCII and most punctuation unless --whitespace
        $string =~ s/[^a-zA-Z0-9_\-\.\/\s]//gi unless $opt->{whitespace};
        # (8) Remove FAT forbidden chars if --fatfilename
        $string =~ s/[\|\?\*\+\"\:\<\>\[\]]//g if $opt->{fatfilename};
        # (9) Remove non-ASCII if --fatfilename
        $string =~ s/[^\x{20}-\x{7E}]//g if $opt->{fatfilename};
        return $string;
    }
    """
 
    # Sanitize directory path, optionally including substitution marker 
    # characters < and >, i.e. collapse adjacent invalid characters into a 
    # single _ character or remove invalid characters

    # Match and replace ! and perhaps other characters, which as program
    # arguments have been translated by Python or get_iplayer into \! and 
    # which would otherwise result in an _ in the sanitized path
    p = re.compile(r"(\\\!+)")
    path = p.sub("", path)

    # PERL comment: NOT (2) Replace forward slashes with _ if not path
    # PERL comment: (3) Replace backslashes with _ if not Windows path
    # PERL comment: (4) Remove extra/leading/trailing whitespace
    # PERL comment: (5) Replace whitespace with _ unless --whitespace
    #
    # Similar to Perl code, however, exclude matching forward slash
    # \s means whitespace
    if os.name == "posix":
        p = re.compile(r"([\\\s]+)")
    else:
        p = re.compile(r"([\s]+)")
    path = p.sub("_", path)

    # PERL comment: NOT (1) Replace leading/trailing ellipsis with _
    # PERL comment: (7) Remove non-ASCII and most punctuation unless --whitespace
    #
    # Similar to Perl code, however, also exclude matching substitution marker
    # characters < and >
    p = re.compile(r"([^\w_\-\.\/\s<>]+)")
    path = p.sub("", path)

    # PERL comment: (8) Remove FAT forbidden chars if --fatfilename
    # PERL comment: NOT (9) Remove non-ASCII if --fatfilename
    #
    # Similar to Perl code, however, exclude matching forward slash and 
    # substitution marker characters < and >
    p = re.compile(r"([\|\?\*\+\"\:\[\]]+)")
    path = p.sub("", path)

    # Replace substitution marker characters < and >
    if include_substitution_markers:
        p = re.compile(r"([<>]+)")
        path = p.sub("_", path)

    # PERL comment: (6) Truncate multiple ('_') replacement chars
    p = re.compile(r"([_]+)")
    path = p.sub("_", path)

    return path

