import cgi
import re

_re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S | re.M | re.I)

def text2html(text, tabstop=4):
    """ Return HTML for Gtk widgets. """
    
    def do_sub(m):
        c = m.groupdict()
        if c['htmlchars']:
            return cgi.escape(c['htmlchars'])
        if c['lineend']:
            #return '<br/>'
            return '\n'
        elif c['space']:
            t = m.group().replace('\t', '&nbsp;' * tabstop)
            t = t.replace(' ', '&nbsp;')
            return t
        elif c['space'] == '\t':
            return ' ' * tabstop;
        else:
            url = m.group('protocal')
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                #last = '<br/>'
                last = '\n'
            return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)

    if text is None:
        return ""
    return re.sub(_re_string, do_sub, text)

def html2text(markup_text):
    # markup is None allowed
    return re.sub("<[^<]+?>", "", markup_text)

    #ALTERNATIVE
    #HTMLParser

    #ALTERNATIVE
    #from BeautifulSoup import BeautifulSoup
    #''.join(BeautifulSoup(page).findAll(text=True))
    
