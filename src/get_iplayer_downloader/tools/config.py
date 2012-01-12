from ConfigParser import ConfigParser

""" The in-memory section header that contains properties that will not be part of a section in the configuration file. """
NOSECTION = "nosection"

class PropertiesConfigParser(ConfigParser):
    
    """ Add support to config parsers for Linux config / Java properties files, 
        i.e. properties not inside a section.
    """    
    class NoSectionHeader(object):
    
        def __init__(self, fp):
            self.fp = fp
            self.no_section_header = "[" + NOSECTION + "]\n"
    
        def readline(self):
            if self.no_section_header:
                try:
                    # Insert NOSECTION header
                    return self.no_section_header
                finally:
                    self.no_section_header = None
            else:
                return self.fp.readline()
         
        def write(self, string):
            if self.no_section_header and self.no_section_header == string:
                # Skip NOSECTION header
                self.no_section_header = None
                return
            self.fp.write(string)

    ####
    
    def __init__(self, defaults=None, **keywords):
        ConfigParser.__init__(self, **keywords)
        
    #def read(self, filenames):
    #    pass

    def readfp(self, fp, filename=None):
        if filename is None:
            #try:
            filename = fp.name
            #except AttributeError:
            #    filename = "<???>"
        #super(PropertiesConfigParser, self).readfp(NoSectionHeader(open(filename)))
        ConfigParser.readfp(self, PropertiesConfigParser.NoSectionHeader(open(filename)))

    def write(self, fp):
        #super(PropertiesConfigParser, self).write(NoSectionHeader(fp))
        ConfigParser.write(self, PropertiesConfigParser.NoSectionHeader(fp))


#############################################################################
#
#
##ALTERNATIVE without subclassing ConfigParser: allow properties not being inside a header
#
#NOTE File my.props:
#item1 = new_value1
#item2 = value2
#
#[default]
#item1 = new_value1_in_default
#
#
#
#import ConfigParser
#
#NOSECTION = "nosection"
#
#class NoSectionHeader(object):
#    """ Adds support to config parsers for Linux config / Java properties files, 
#        by allowing entries not inside a header
#    """
#    def __init__(self, fp):
#        self.fp = fp
#        self.no_section_header = "[" + NOSECTION + "]\n"
#
#    def readline(self):
#        if self.no_section_header:
#            try:
#                return self.no_section_header
#            finally:
#                self.no_section_header = None
#        else:
#            return self.fp.readline()
#     
#    def write(self, string):
#        if self.no_section_header and self.no_section_header == string:
#            self.no_section_header = None
#            return
#        self.fp.write(string)
#
#config = ConfigParser.ConfigParser()
#config.readfp(NoSectionHeader(open("my.props")))
#
#print config.get(NOSECTION, "item1")
#print config.get("default", "item1")
#
#config.set(NOSECTION, "item1", "new_value1")
#config.set("default", "item1", "new_value1_in_default")
#
## Writing our configuration file to 'example.cfg'
#with open('my.props', 'wb') as configfile:
#    config.write(NoSectionHeader(configfile))
