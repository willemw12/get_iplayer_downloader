import os

from gi.repository import Gtk, Pango

# Load application-wide definitions
import get_iplayer_downloader

#NOTE Import module, not symbol names inside a module, to avoid circular import
import get_iplayer_downloader.ui.main_window

from get_iplayer_downloader import settings
from get_iplayer_downloader.tools import config, file, markup, string
from get_iplayer_downloader.ui.tools import image as Image

class PropertiesWindow(Gtk.Window):

    def __init__(self, get_iplayer_output_lines):
        Gtk.Window.__init__(self, title="properties - " + get_iplayer_downloader.PROGRAM_NAME)
        self.set_default_size(get_iplayer_downloader.ui.main_window.WINDOW_LARGE_WIDTH, get_iplayer_downloader.ui.main_window.WINDOW_LARGE_HEIGHT)
        self.set_border_width(get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH)
        #self.set_resizable(False)
        
        self._init_grid(get_iplayer_output_lines)

    def _init_grid(self, prop_table):
        ##min_content_height=600, min_content_width=600
        ##visible=True, can_focus=True, hscrollbar_policy=Gtk.Policy.AUTOMATIC, 
        #                               vscrollbar_policy=Gtk.Policy.AUTOMATIC
        scrolled_window = Gtk.ScrolledWindow()
        ##scrolled_window.min_content_height(700)
        ##scrolled_window.min_content_width(800)
        #scrolled_window.set_property("min-content-height", 5800)
        #scrolled_window.set_property("min-content-width", 400)
        ##self.set_default_size(400, 400)
        #scrolled_window.set_hexpand(True)
        #scrolled_window.set_vexpand(True)
        self.add(scrolled_window)

        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, margin=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH)
        ##self.grid.set_row_homogeneous(False)
        ##self.grid.set_column_homogeneous(False)
        scrolled_window.add_with_viewport(self.grid)

        #### Thumbnail
        
        image_url = None
        for prop_label, prop_value in prop_table:
            if prop_label == "thumbnail" or prop_label == "thumbnail4":
                image_url = prop_value
        ##ALTERNATIVE
        #for i in range(len(prop_table)):
        #    if prop_table[i][InfoResultColumn.PROP_LABEL /* 0 */] == "thumbnail4":
        #        break
        #if i < len(prop_table):
        #    image_url = prop_table[i][InfoResultColumn.PROP_VALUE /* 1 */]

        if image_url is not None:
            if string.str2bool(settings.config().get(config.NOSECTION, "show-images")):
                timeout = string.str2float(settings.config().get(config.NOSECTION, "load-image-timeout-seconds"))
                image = Image.image(image_url, timeout=timeout)
                if image is not None:
                    self.grid.add(image)

        #### Property table
        
        #NOTE To expand the grid, expand one of its child widgets
        frame = Gtk.Frame(label="Properties", label_xalign=0.01, margin=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH, hexpand=True)
        self.grid.add(frame)

        ####
        
        PROP_LABEL_LIST = ["available", "categories", "channel", "desc", "dir",
                           "duration", "episode", "expiry", "expiryrel",
                           "firstbcast", "firstbcastrel", "index", "lastbcast",
                           "lastbcastrel", "longname", "modes", "modesizes",
                           "pid", "player", "senum", "timeadded", "title",
                           "type", "versions", "web"]

        prop_grid = Gtk.Grid(column_homogeneous=False, row_homogeneous=False,
                             margin_top=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH, margin_bottom=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH)
        frame.add(prop_grid)
        
        focused_label = None
        #for prop_row in prop_table:
        #for i, prop_row in enumerate(prop_table):
        for i, (prop_label, prop_value) in enumerate(prop_table):
            if prop_label in PROP_LABEL_LIST:
                if prop_label == "duration":
                    try:
                        # Convert into hours and minutes
                        #NOTE // is the integer division operator
                        duration_mins = int(prop_value) // 60
                        prop_value = "{0:2}".format(duration_mins // 60) + ":" + \
                                     "{0:02}".format(duration_mins % 60)
                        prop_value = prop_value.strip()
                    except ValueError:
                        #NOTE prop_value still has its original value
                        pass
                
                label1 = Gtk.Label(prop_label, valign=Gtk.Align.START, halign=Gtk.Align.START)
                label1.set_padding(get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH, 0)
                label1.set_line_wrap(True)
                #label1.set_selectable(False)
                prop_grid.attach(label1, 0, i, 1, 1)

                label2 = Gtk.Label(markup.text2html(prop_value), margin_left=40,
                                   valign=Gtk.Align.START, halign=Gtk.Align.START, use_markup=True)
                label2.set_padding(get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH, 0)
                label2.set_line_wrap(True)
                label2.set_selectable(True)
                label2.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                # Avoid centering of text, when line wrap warps at word boundaries (WORD, WORD_CHAR)
                label2.set_alignment(0, 0)
                prop_grid.attach(label2, 1, i, 1, 1)

                if prop_label == "index" or prop_label == "title":
                    focused_label = label2

        if focused_label:
            focused_label.grab_focus()
            # Avoid highlighted text
            focused_label.select_region(0, 0)
        
        ####

        ##ALTERNATIVE array indexing and populating Gtk.Grid
        #self.table = Gtk.Table()
        #self.add(self.table)
        #for y in range((len(prop_list)):
        #    for x in range(len(prop_list[y])):
        #        label = Gtk.Label()
        #        ...
        #        self.table.attach(label, x, x+1, y, y+1)

        ####
        
        ##ALTERNATIVE however, Gtk.Grid has better geometry management
        #prop_table = Gtk.Table(len(prop_list), len(prop_list[0]), False)
        #frame.add(prop_table)
        #
        #i = 0
        #for prop_row in prop_list:
        #    label = Gtk.Label(prop_row[InfoResultColumn.PROP_LABEL /* 0 */], valign=Gtk.Align.START, halign=Gtk.Align.START)
        #    label.set_padding(4, 0)
        #    label.set_line_wrap(True)
        #    prop_table.attach(label, 0, 1, i, i+1)
        #
        #    #, use_markup=True
        #    label = Gtk.Label(prop_row[InfoResultColumn.PROP_VALUE /* 1 */], valign=Gtk.Align.START, halign=Gtk.Align.START)
        #    label.set_padding(4, 0)
        #    label.set_line_wrap(True)
        #    prop_table.attach(label, 1, 2, i, i+1)
        #    
        #    i += 1

        ####

        frame = Gtk.Frame(label="Additional links", label_xalign=0.01, margin=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH)
        self.grid.add(frame)

        url = "<a href=\"http://www.bbc.co.uk/iplayer\" title=\"BBC iPlayer\">BBC iPlayer</a>"
        url += "      "

        # Add URLs to get_iplayer's pvr configuration folder and filenames
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url += file.files2urls(filepath)
        url += "      "

        # Add URLs to get_iplayer's presets configuration folder and filenames
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += file.files2urls(filepath)

        label1 = Gtk.Label(url, valign=Gtk.Align.START, halign=Gtk.Align.START, use_markup=True,
                           margin_top=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH, margin_bottom=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH)
        label1.set_padding(get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH, 0)
        label1.set_line_wrap(True)
        #WORD_CHAR
        label1.set_line_wrap_mode(Pango.WrapMode.CHAR)
        #label1.set_selectable(False)
        frame.add(label1)

        ####
        
        box = Gtk.Box(spacing=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH)
        self.grid.add(box)
        
        button = Gtk.Button(stock=Gtk.STOCK_CLOSE, margin=get_iplayer_downloader.ui.main_window.WIDGET_BORDER_WIDTH)
        button.connect("clicked", lambda user_data: self.destroy())
        box.pack_end(button, False, False, 0)
