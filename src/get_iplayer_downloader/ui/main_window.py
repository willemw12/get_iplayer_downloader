#!/usr/bin/env python3

import os
import signal

from datetime import datetime, timedelta
from gi.repository import Gdk, GObject, Gtk

# Load application-wide definitions
import get_iplayer_downloader

#NOTE Import module, not symbol names inside a module, to avoid circular import
#NOTE Import ... as ... : the "as ..." only works when it is "down" the import hierarchy
import get_iplayer_downloader.ui.main_controller as main_controller
import get_iplayer_downloader.ui.main_menu as main_menu

from get_iplayer_downloader import cache, command_util, get_iplayer, settings
from get_iplayer_downloader.get_iplayer import SinceListIndex, SearchResultColumn
from get_iplayer_downloader.tools import config, markup, string
from get_iplayer_downloader.ui.tools import image as Image

#TOOLTIP_FILE_QUIT

TOOLTIP_VIEW_PLAYER = "View episode's web page or start podcast episode in the web browser"
TOOLTIP_VIEW_PROPERTIES = "View episode properties"
TOOLTIP_VIEW_LOG = "View download log"

#TOOLTIP_EDIT_PREFERENCES

#PVR_CHECK_BUTTON
#TOOLTIP_TOOLS_DOWNLOAD_OR_PRV_QUEUE = "Download selected episodes, or queue episodes if 'PVR' is enabled"
TOOLTIP_TOOLS_DOWNLOAD = "Download selected episodes"
TOOLTIP_TOOLS_CLEAR = "Clear selected episodes"
TOOLTIP_TOOLS_REFRESH = "Refresh episode cache, limited of the selected programme type (radio, podcast or TV)"

TOOLTIP_SEARCH_FIND = "Find episodes"
TOOLTIP_SEARCH_CLEAR = "Clear search text"
TOOLTIP_SEARCH_GO_TO_FIND = "Go to search entry field on the tool bar"
TOOLTIP_SEARCH_LOCATE_SIMILAR = "Find more similar episodes on the file system, using the updatedb \"locate\" command"
TOOLTIP_SEARCH_ROTATE_SINCE = "Select since episodes were added to the cache"
TOOLTIP_SEARCH_ROTATE_PROG_TYPE = "Select programme type (radio, podcast or TV)"
TOOLTIP_SEARCH_ROTATE_CATEGORY = "Select programme category"
TOOLTIP_SEARCH_ROTATE_CHANNEL = "Select channel"

TOOLTIP_FILTER_SEARCH_ENTRY = "Search in series title, episode title and description or on PID. Add a minus sign in front of the whole search term to exclude it from the search. Press 'Enter' to search"
TOOLTIP_FILTER_PROGRAMME_TYPE = "Filter on programme type"
TOOLTIP_FILTER_PROGRAMME_CATEGORIES = "Filter on programme categories. Filter on all listed (configured) categories, when the filter is off. The filter is off when the filter label in the tool bar is 'Categories' or empty"
TOOLTIP_FILTER_PROGRAMME_CHANNELS = "Filter on channels. Filter on all listed (configured) channels, when the filter is off. The filter is off when the filter label in the tool bar is 'Channels' or empty"
TOOLTIP_FILTER_SINCE = "Filter on episodes recently added to the cache. The filter is off when filter label in the tool bar is 'Since' or empty"

TOOLTIP_OPTION_ALT_RECORDING_MODES = "Download or queue episodes with the alternative set of recording modes, instead of the default get_iplayer modes"
TOOLTIP_OPTION_SEARCH_ALL = "Search in all the available categories and/or channels when the filter is off. The filter is off when the filter label in the tool bar is 'Categories', 'Channels' or empty"
TOOLTIP_OPTION_FORCE = "Force download or force refresh of the episode cache"
TOOLTIP_OPTION_FUTURE = "Include or exclude future episodes in the episode list and future episode information in the property list. Click 'Refresh', with 'Future' enabled, to update the list of future episodes in the cache. The category filter is disabled in 'Future' mode"
TOOLTIP_OPTION_DRY_RUN = "Dry-run download and queue commands"

TOOLTIP_OPTION_PVR_QUEUE = "Queue selected episodes for one-off downloading"

TOOLTIP_PROGRESS_BAR = "Downloading / Errors. Click to view the download log, reset the error count or remove log and image cache files"

TOOLTIP_MENU_BUTTON = "Menu. Click here or right-click below the tool bar"

TOOLTIP_HELP_HELP = "Help for this program"
TOOLTIP_HELP_ABOUT = "About this program"

####

WINDOW_MAIN_HEIGHT = 680

WINDOW_LARGE_WIDTH = 800
WINDOW_LARGE_HEIGHT = WINDOW_MAIN_HEIGHT

WINDOW_LARGE_WIDTH_WIDE = 980
WINDOW_LARGE_HEIGHT_WIDE = WINDOW_MAIN_HEIGHT

#WINDOW_MEDIUM_WIDTH = 600
#WINDOW_MEDIUM_HEIGHT = 500

####

WIDGET_BORDER_WIDTH = 4
WIDGET_BORDER_WIDTH_COMPACT = 2

####

ICON_IMAGE_MAX_WIDTH = 600
ICON_IMAGE_MAX_HEIGHT = 600

IMAGE_MAX_WIDTH = 800
IMAGE_MAX_HEIGHT = 800

####

PROGRESS_BAR_TIMEOUT_MILLISECONDS = 4000

#### Main window

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_window_title()
        # Set minimal size: self.set_size_request(...)
        self.set_default_size(-1, WINDOW_MAIN_HEIGHT)
        self.set_border_width(WIDGET_BORDER_WIDTH)
        start_maximized = string.str2bool(settings.get_config().get(config.NOSECTION, "start-maximized"))
        if start_maximized:
            self.maximize()

        self.busy_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.normal_cursor = Gdk.Cursor(Gdk.CursorType.LEFT_PTR)
        
        ####
        
        # Get and update last visited cached timestamp
        last_visit_time_dt = cache.get_last_visit_time()
        cache.save_last_visit_time()

        if last_visit_time_dt is not None:
            last_visit_time_td = datetime.now() - last_visit_time_dt
            if last_visit_time_td.days >= 0:
                # Round up to the nearest hour
                last_visit_time_td += timedelta(hours=1)
                last_visit_hours = last_visit_time_td.seconds // 3600
                TOOLTIP_FILTER_SINCE_LAST_VISIT_TIME = "Last visit: " + \
                        str(last_visit_time_td.days) + " days " + \
                        str(last_visit_hours) + " hours ago"
                global TOOLTIP_FILTER_SINCE
                TOOLTIP_FILTER_SINCE = TOOLTIP_FILTER_SINCE_LAST_VISIT_TIME + "\n" + TOOLTIP_FILTER_SINCE
        
        ####
        
        # Initialize the controller
        self._main_controller = main_controller.MainWindowController(self)
        
        # Initialize the view
        self._init_ui_manager()
        self._init_builder()
        self._init_main_grid()
        self._init_menu_bar()
        self._init_tool_bar_box()
        self._init_main_tree_view()

        # Finalize initialization of the controller
        self._main_controller.init()

        ####
        
        # Initialize the model
        self.main_tree_view.init_store()        

        #if start_maximized:
        #    # Avoid redraw of the right-aligned menu/configuration image/icon 
        #    # to another position on the top tool bar, by forcing the calculation
        #    # of the main window width and therefore also the top tool bar width
        #    self.tool_bar_box.show_all()

    def _init_ui_manager(self):
        self.ui_manager = main_menu.UIManager(self)

    def _init_builder(self):
        self.builder = Builder()

    def _init_main_grid(self):
        self.main_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_grid)

    def _init_menu_bar(self):
        if string.str2bool(settings.get_config().get(config.NOSECTION, "show-menu-bar")):
            self.menu_bar = self.ui_manager.get_menu_bar()
            self.main_grid.add(self.menu_bar)
        
    def _init_tool_bar_box(self):
        self.tool_bar_box = MainToolBarBox(self)
        self.main_grid.add(self.tool_bar_box)
        
    def _init_main_tree_view(self):
        self.main_tree_view_scrollbars = Gtk.ScrolledWindow()
        self.main_tree_view_scrollbars.set_hexpand(True)
        self.main_tree_view_scrollbars.set_vexpand(True)
        #self.main_tree_view_scrollbars.set_policy(Gtk.PolicyType.ALWAYS,
        #                                          Gtk.PolicyType.ALWAYS)
        self.main_grid.attach_next_to(self.main_tree_view_scrollbars, self.tool_bar_box, Gtk.PositionType.BOTTOM, 1, 2)

        self.main_tree_view = MainTreeView(self)
        self.main_tree_view_scrollbars.add(self.main_tree_view)
                
    def controller(self):
        return self._main_controller
    
    def set_window_title(self, prog_type=None):
        if prog_type:
            self.set_title(prog_type + " - " + get_iplayer_downloader.PROGRAM_NAME)
        else:
            self.set_title(get_iplayer_downloader.PROGRAM_NAME)

    def display_busy_mouse_cursor(self, busy):
        #window = self.get_window()
        
        # Get the window of the widget (the second widget in the hierarchy)
        # immediately below the main window widget
        window = self.main_grid.get_window()
        if window is not None:
            if busy:
                Gdk.Window.set_cursor(window, self.busy_cursor)
                # Display the cursor immediately
                #Gdk.Display.get_default().sync()
                #self.get_display().sync()
                window.get_display().sync()
            else:
                Gdk.Window.set_cursor(window, self.normal_cursor)

class MainToolBarBox(Gtk.Box):

    def __init__(self, main_window):
        Gtk.Box.__init__(self, spacing=WIDGET_BORDER_WIDTH)
        self.main_window = main_window

        INDENT_STR = "   "
        
        #disable_presets = string.str2bool(settings.get_config().get(config.NOSECTION, "disable-presets"))

        focus_chain = []
        
        compact_toolbar = string.str2bool(settings.get_config().get(config.NOSECTION, "compact-tool-bar"))
        if compact_toolbar:
            show_button_labels = False
        else:
            show_button_labels = string.str2bool(settings.get_config().get(config.NOSECTION, "show-button-labels"))

        ####
        
        if string.str2bool(settings.get_config().get(config.NOSECTION, "show-button-menu")):

            button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
            button.set_image(Gtk.Image(icon_name=Gtk.STOCK_MEDIA_PLAY))
            if show_button_labels:
                button.set_label("Play")
            button.set_tooltip_text(TOOLTIP_VIEW_PLAYER)
            button.connect("clicked", self.main_window.controller().on_button_play_clicked_by_pid, None)
            self.pack_start(button, False, False, 0)
            focus_chain.append(button)
    
            button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
            button.set_image(Gtk.Image(icon_name=Gtk.STOCK_PROPERTIES))
            if show_button_labels:
                button.set_label("Properties")
            button.set_tooltip_text(TOOLTIP_VIEW_PROPERTIES)
            button.connect("clicked", self.main_window.controller().on_button_properties_clicked)
            self.pack_start(button, False, False, 0)
            focus_chain.append(button)
    
        button = Gtk.Button(use_underline=True, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        #Gtk.STOCK_GO_DOWN
        button.set_image(Gtk.Image(icon_name=Gtk.STOCK_GOTO_BOTTOM))
        if show_button_labels:
            button.set_label("_Download")
        #PVR_CHECK_BUTTON
        #button.set_tooltip_text(TOOLTIP_TOOLS_DOWNLOAD_OR_PRV_QUEUE)
        button.set_tooltip_text(TOOLTIP_TOOLS_DOWNLOAD)
        button.connect("clicked", self.main_window.controller().on_button_download_clicked)
        self.pack_start(button, False, False, 0)
        focus_chain.append(button)

        button = Gtk.Button(use_underline=True, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_image(Gtk.Image(icon_name=Gtk.STOCK_COPY))
        if show_button_labels:
            button.set_label("_Queue")
        button.set_tooltip_text(TOOLTIP_OPTION_PVR_QUEUE)
        button.connect("clicked", self.main_window.controller().on_button_pvr_queue_clicked)
        self.pack_start(button, False, False, 0)
        focus_chain.append(button)

        if string.str2bool(settings.get_config().get(config.NOSECTION, "show-button-menu")):

            button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
            button.set_image(Gtk.Image(icon_name=Gtk.STOCK_CLEAR))
            if show_button_labels:
                button.set_label("Clear")
            button.set_tooltip_text(TOOLTIP_TOOLS_CLEAR)
            button.set_focus_on_click(False)
            button.connect("clicked", self.main_window.controller().on_button_clear_clicked)
            self.pack_start(button, False, False, 0)
            focus_chain.append(button)
    
            button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
            button.set_image(Gtk.Image(icon_name=Gtk.STOCK_REFRESH))
            if show_button_labels:
                button.set_label("Refresh")
            button.set_tooltip_text(TOOLTIP_TOOLS_REFRESH)
            button.set_focus_on_click(False)
            button.connect("clicked", self.main_window.controller().on_button_refresh_clicked)
            self.pack_start(button, False, False, 0)
            focus_chain.append(button)

        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        ####
        
        if show_button_labels:
            button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
            button.set_image(Gtk.Image(icon_name=Gtk.STOCK_FIND))
            button.set_tooltip_text(TOOLTIP_SEARCH_FIND)
            button.connect("clicked", self.main_window.controller().on_button_find_clicked)
            self.pack_start(button, False, False, 0)

        self.search_entry = SearchEntry(compact_toolbar)
        self.search_entry.set_tooltip_text(TOOLTIP_FILTER_SEARCH_ENTRY)
        self.search_entry.connect("activate", self.main_window.controller().on_button_find_clicked)
        self.search_entry.connect("icon-press", self._on_search_entry_find_icon_press)
        self.pack_start(self.search_entry, False, False, 0)
        focus_chain.append(self.search_entry)

        self.search_entry.grab_focus()
        
        ####

        if not compact_toolbar:
            label = Gtk.Label(" Type:")
            self.pack_start(label, False, False, 0)

        #NOTE Preset can be None. However cannot set presets in the model to None: 
        #     the toolbar models and configuration are based on presets, not programme types
        #(TODO Group episodes in programme types (radio, podcasts or TV), not on presets (radio or TV))
        #if disable_presets:
        #    presets = [[None, get_iplayer.ProgType.RADIO, "Radio"],
        #               [None, get_iplayer.ProgType.PODCAST, "Podcast"],
        #               [None, get_iplayer.ProgType.TV, "TV"]]
        #else:
        presets = [[get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO, "Radio"],
                   [get_iplayer.Preset.RADIO, get_iplayer.ProgType.PODCAST, "Podcast"],
                   [get_iplayer.Preset.TV, get_iplayer.ProgType.TV, "TV"]]
        if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-ch4")):
            presets.append([get_iplayer.Preset.TV, get_iplayer.ProgType.CH4, "CH4"])
        if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-itv")):
            presets.append([get_iplayer.Preset.TV, get_iplayer.ProgType.ITV, "ITV"])

        store = Gtk.ListStore(str, str, str)
        for preset in presets:
            store.append(preset)

        self.preset_combo = Gtk.ComboBox.new_with_model(store)
        #self.preset_combo.set_active(-1)
        
        self.preset_combo.set_valign(Gtk.Align.CENTER)
        self.preset_combo.set_tooltip_text(TOOLTIP_FILTER_PROGRAMME_TYPE)
        self.preset_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.preset_combo.pack_start(renderer_text, True)
        # Render third store column 
        self.preset_combo.add_attribute(renderer_text, "text", 2)
        self.preset_combo.connect("changed", self.main_window.controller().on_combo_preset_changed)
        
        #if disable_presets:
        #    self.preset_combo.set_sensitive(False)
        
        self.pack_start(self.preset_combo, False, False, 0)
        focus_chain.append(self.preset_combo)

        ####
        
        if not compact_toolbar:
            label = Gtk.Label(" Categories:")
            self.pack_start(label, False, False, 0)

        self.cat_disabled_store = Gtk.ListStore(str, str)
        for categories in get_iplayer.Categories.ALL:
            self.cat_disabled_store.append(categories)

        self.cat_radio_store = Gtk.ListStore(str, str)
        for i, categories in enumerate(get_iplayer.Categories.RADIO):
            if compact_toolbar and i > 0:
                categories[1] = INDENT_STR + categories[1]
            self.cat_radio_store.append(categories)
        ##if not "ANY" in [row[VALUE_INDEX] for row in get_iplayer.Categories.RADIO[1:]]:
        #self.cat_radio_store.append([None, "ANY"])

        self.cat_podcast_store = Gtk.ListStore(str, str)
        for i, categories in enumerate(get_iplayer.Categories.PODCAST):
            if compact_toolbar and i > 0:
                categories[1] = INDENT_STR + categories[1]
            self.cat_podcast_store.append(categories)
        ##if not "ANY" in [row[VALUE_INDEX] for row in get_iplayer.Categories.PODCAST[1:]]:
        #self.cat_podcast_store.append([None, "ANY"])

        self.cat_tv_store = Gtk.ListStore(str, str)
        for i, categories in enumerate(get_iplayer.Categories.TV):
            if compact_toolbar and i > 0:
                categories[1] = INDENT_STR + categories[1]
            self.cat_tv_store.append(categories)
        ##if not "ANY" in [row[VALUE_INDEX] for row in get_iplayer.Categories.TV[1:]]:
        #self.cat_tv_store.append([None, "ANY"])

        #ALTERNATIVE TreeStore combo box instead of ListStore combo box
        #self.cat_radio_store = Gtk.TreeStore(str, str)
        #root_iter = self.cat_radio_store.append(None, categories)
        #for categories in get_iplayer.Categories.RADIO:
        #    self.cat_radio_store.append(root_iter, categories)
        
        #self.category_combo = Gtk.ComboBox.new_with_model(self.cat_radio_store)
        self.category_combo = Gtk.ComboBox()
        # Mark as unselected, to allow it to be set automatically (by session restore) 
        #WORKAROUND set to 99 (out of bounds) instead of -1 to avoid this error message:
        #    Gtk-CRITICAL **: gtk_cell_view_set_displayed_row: assertion `GTK_IS_TREE_MODEL (cell_view->priv->model)' failed
        #self.category_combo.set_active(-1)
        self.category_combo.set_active(99)
        
        self.category_combo.set_valign(Gtk.Align.CENTER)
        self.category_combo.set_tooltip_text(TOOLTIP_FILTER_PROGRAMME_CATEGORIES)
        self.category_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.category_combo.pack_start(renderer_text, True)
        # Render second store column 
        self.category_combo.add_attribute(renderer_text, "text", 1)

        #if disable_presets:
        #    self.category_combo.set_sensitive(False) 
        
        if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-category-filter")):
            self.pack_start(self.category_combo, False, False, 0)
            focus_chain.append(self.category_combo)

        ####

        if not compact_toolbar:
            label = Gtk.Label(" Channels:")
            self.pack_start(label, False, False, 0)

        # Create radio model list
        channels = get_iplayer.Channels.RADIO
        channel_list = channels.split(",")
        self.chan_radio_store = Gtk.ListStore(str, str)
        first = True
        for channel in channel_list:
            #NOTE assign to two variables in one statement
            key = label = channel.strip()
            if first:
                # The first item in the list represents all configured channels
                #key = settings.get_config().get("radio", "channels")
                key = ",".join(channel_list[1:])
                first = False
            else:
                if key.startswith("-"):
                    # Skip excluded channel
                    continue
                if compact_toolbar:
                    if label.startswith("BBC "):
                        # Remove leading "BBC " substring
                        label = label[len("BBC "):]
                    label = INDENT_STR + label
            self.chan_radio_store.append([key, label])
        ##if channels and not "ALL" in [row[VALUE_INDEX] for row in get_iplayer.Channels.RADIO[1:]]:
        #if channels:
        #    self.chan_radio_store.append([None, "ANY"])
        
        # Create tv model list
        channels = get_iplayer.Channels.TV
        channel_list = channels.split(",")
        self.chan_tv_store = Gtk.ListStore(str, str)
        first = True
        for channel in channel_list:
            key = label = channel.strip()
            if first:
                # The first item in the list represents all configured channels
                #key = settings.get_config().get("tv", "channels")
                key = ",".join(channel_list[1:])
                first = False
            else:
                if key.startswith("-"):
                    # Skip excluded channel
                    continue
                if compact_toolbar:
                    if label.startswith("BBC "):
                        # Remove leading "BBC " substring
                        label = label[len("BBC "):]
                    label = INDENT_STR + label
            self.chan_tv_store.append([key, label])
        ##if channels and not "ALL" in [row[VALUE_INDEX] for row in get_iplayer.Channels.TV[1:]]:
        #if channels:
        #    self.chan_tv_store.append([None, "ANY"])

        self.chan_ch4_store = None
        if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-ch4")):
            # Create ch4 model list
            channels = get_iplayer.Channels.CH4
            channel_list = channels.split(",")
            self.chan_ch4_store = Gtk.ListStore(str, str)
            first = True
            for channel in channel_list:
                key = label = channel.strip()
                if first:
                    # The first item in the list represents all configured channels
                    #key = settings.get_config().get("tv", "channels")
                    key = ",".join(channel_list[1:])
                    first = False
                else:
                    if key.startswith("-"):
                        # Skip excluded channel
                        continue
                    if compact_toolbar:
                        if label.startswith("4oD "):
                            # Remove leading "4oD " string
                            label = label[len("4oD "):]
                        label = INDENT_STR + label
                self.chan_ch4_store.append([key, label])
            ##if channels and not "ALL" in [row[VALUE_INDEX] for row in get_iplayer.Channels.CH4[1:]]:
            #if channels:
            #    self.chan_ch4_store.append([None, "ANY"])

        self.chan_itv_store = None
        if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-itv")):
            # Create itv model list
            channels = get_iplayer.Channels.ITV
            channel_list = channels.split(",")
            self.chan_itv_store = Gtk.ListStore(str, str)
            first = True
            for channel in channel_list:
                key = label = channel.strip()
                if first:
                    # The first item in the list represents all configured channels
                    #key = settings.get_config().get("tv", "channels")
                    key = ",".join(channel_list[1:])
                    first = False
                else:
                    if key.startswith("-"):
                        # Skip excluded channel
                        continue
                    if compact_toolbar:
                        if label.startswith("ITV "):
                            # Remove leading "ITV " string
                            label = label[len("ITV "):]
                        label = INDENT_STR + label
                self.chan_itv_store.append([key, label])
            ##if channels and not "ALL" in [row[VALUE_INDEX] for row in get_iplayer.Channels.ITV[1:]]:
            #if channels:
            #    self.chan_itv_store.append([None, "ANY"])

        #self.channel_combo = Gtk.ComboBox.new_with_model(self.chan_radio_store)
        self.channel_combo = Gtk.ComboBox()
        # Mark as unselected, to allow it to be set automatically (by session restore) 
        #self.category_combo.set_active(-1)
        self.channel_combo.set_active(99)

        self.channel_combo.set_valign(Gtk.Align.CENTER)
        self.channel_combo.set_tooltip_text(TOOLTIP_FILTER_PROGRAMME_CHANNELS)
        self.channel_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.channel_combo.pack_start(renderer_text, True)
        # Render second store column 
        self.channel_combo.add_attribute(renderer_text, "text", 1)

        #if disable_presets:
        #    self.channel_combo.set_sensitive(False)

        if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-channel-filter")):
            self.pack_start(self.channel_combo, False, False, 0)
            focus_chain.append(self.channel_combo)

        ####

        if not compact_toolbar:
            label = Gtk.Label(" Since:")
            self.pack_start(label, False, False, 0)

        store = Gtk.ListStore(int, str)
        for i, since in enumerate(get_iplayer.SINCE_LIST):
            if compact_toolbar and i > 0:
                since[1] = INDENT_STR + since[1]
            store.append(since)

        self.since_combo = Gtk.ComboBox.new_with_model(store)
        self.since_combo.set_active(SinceListIndex.FOREVER)

        self.since_combo.set_valign(Gtk.Align.CENTER)
        self.since_combo.set_tooltip_text(TOOLTIP_FILTER_SINCE)
        self.since_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.since_combo.pack_start(renderer_text, True)
        # Render second store column 
        self.since_combo.add_attribute(renderer_text, "text", 1)

        if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-since-filter")):
            self.pack_start(self.since_combo, False, False, 0)
            focus_chain.append(self.since_combo)

        ####

        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(grid, False, False, 0)
        focus_chain.append(grid)

        self.search_all_check_button = Gtk.CheckButton("All")   # "Any"
        self.search_all_check_button.set_tooltip_text(TOOLTIP_OPTION_SEARCH_ALL)
        self.search_all_check_button.set_focus_on_click(False)
        #if disable_presets:
        #    self.search_all_check_button.set_sensitive(False)
        #    self.search_all_check_button.set_active(True)
        grid.add(self.search_all_check_button)
        
        self.alt_recording_mode_check_button = Gtk.CheckButton("Alt")
        self.alt_recording_mode_check_button.set_tooltip_text(TOOLTIP_OPTION_ALT_RECORDING_MODES)
        self.alt_recording_mode_check_button.set_focus_on_click(False)
        grid.attach_next_to(self.alt_recording_mode_check_button, self.search_all_check_button, Gtk.PositionType.BOTTOM, 1, 1)
        
        self.force_check_button = Gtk.CheckButton("Force")
        self.force_check_button.set_tooltip_text(TOOLTIP_OPTION_FORCE)
        self.force_check_button.set_focus_on_click(False)
        grid.attach_next_to(self.force_check_button, self.search_all_check_button, Gtk.PositionType.RIGHT, 1, 1)

        self.future_check_button = Gtk.CheckButton("Future")
        self.future_check_button.set_tooltip_text(TOOLTIP_OPTION_FUTURE)
        self.future_check_button.set_focus_on_click(False)
        self.future_check_button.connect("clicked", self.main_window.controller().on_check_button_future_clicked)
        grid.attach_next_to(self.future_check_button, self.force_check_button, Gtk.PositionType.BOTTOM, 1, 1)

        ####
        
        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(grid, False, False, 0)
        focus_chain.append(grid)

        ##
        
        #self.processes_label = Gtk.Label("D: 0")
        #self.processes_label.set_tooltip_text("Downloading")
        #grid.add(self.processes_label)
        #
        #self.queue_size_label = Gtk.Label("Q: 0")
        #self.queue_size_label.set_tooltip_text("Waiting to download")
        #grid.addmain_window.main_controller.(self.queue_size_label)

        event_box = Gtk.EventBox()
        event_box.connect("button-press-event", self.main_window.controller().on_progress_bar_button_press_event)
        grid.add(event_box)

        ##halign=Gtk.Align.START, valign=Gtk.Align.START, min_horizontal_bar_width=16
        self.progress_bar = Gtk.ProgressBar()
        # Set minimal size: self.progress_bar.set_size_request(90, -1)
        #self.progress_bar.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_fraction(0.0)
        #self.progress_bar.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        #self.progress_bar.connect("button-press-event", self.main_window.controller().on_progress_bar_button_press_event)
        #self.progress_bar.set_tooltip_text("D (downloading), Q (waiting to download)")
        self.progress_bar.set_tooltip_text(TOOLTIP_PROGRESS_BAR)
        #grid.attach_next_to(self.progress_bar, self.pvr_queue_check_button, Gtk.PositionType.RIGHT, 1, 1)
        event_box.add(self.progress_bar)


        self.dry_run_check_button = Gtk.CheckButton("Preview")
        self.dry_run_check_button.set_tooltip_text(TOOLTIP_OPTION_DRY_RUN)
        self.dry_run_check_button.set_focus_on_click(False)
        grid.add(self.dry_run_check_button)

        ##
        
        #PVR_CHECK_BUTTON
        #self.pvr_queue_check_button = Gtk.CheckButton("PVR")
        #self.pvr_queue_check_button.set_tooltip_text("Queue mode. " + TOOLTIP_OPTION_PVR_QUEUE + ", when clicking on the download button in the tool bar")
        #self.pvr_queue_check_button.set_focus_on_click(False)
        #grid.attach_next_to(self.pvr_queue_check_button, event_box, Gtk.PositionType.BOTTOM, 1, 1)

        ##

        ## Load css file
        ##ALTERNATIVE set style for one widget, instead for the whole program on a screen
        #style_context = self.progress_bar.get_style_context()
        #css_provider = Gtk.CssProvider()
        #package_pathname = os.path.dirname(os.path.realpath(__file__))
        #css_filename = os.path.join(package_pathname, "style.css")
        #css_provider.load_from_file(Gio.File.new_for_path(css_filename))
        #style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        
        ##

        # Timeout in milliseconds
        self.timeout_id = GObject.timeout_add(PROGRESS_BAR_TIMEOUT_MILLISECONDS, self.main_window.controller().on_progress_bar_update, None)
        
        # Initialize label text
        #self.main_window.controller().on_progress_bar_update(None)

        ####

        #if not compact_toolbar:
        #KEYBOARD FOCUS:
        #event_box = Gtk.EventBox(can_focus=True)
        event_box = Gtk.EventBox(hexpand_set=True, halign=Gtk.Align.END, valign=Gtk.Align.START)
        event_box.connect("button-press-event", self._on_menu_button_press_event)
        #KEYBOARD FOCUS:
        #event_box.connect("key-release-event", self._on_menu_button_key_release_event)
        self.pack_end(event_box, False, False, 0)

        image = Gtk.Image(icon_name=Gtk.STOCK_PREFERENCES)
        image.set_tooltip_text(TOOLTIP_MENU_BUTTON)
        event_box.add(image)
        
        ####

        #self.spinner = Gtk.Spinner()
        ##self.spinner_stop()
        #self.pack_start(self.spinner, False, False, 0)
        
        #self.progress_bar = Gtk.ProgressBar()
        #self.progress_bar.set_valign(Gtk.Align.CENTER)
        #self.progress_bar.set_pulse_step(0.01)
        #self.pack_start(self.progress_bar, False, False, 0)

        ####

        # Set tab key traversal order
        self.set_focus_chain(focus_chain)
    
    def _on_search_entry_find_icon_press(self, entry, icon_pos, event):
        if icon_pos == Gtk.EntryIconPosition.PRIMARY:
            self.main_window.controller().on_button_find_clicked(None)

    def _on_menu_button_press_event(self, widget, event):
        if event.button == 1:
            # Left mouse click
            self.main_window.controller().ui_manager.get_popup_menu().popup(None, None, None, None, event.button, event.time)
        #return True

    #KEYBOARD FOCUS:
    #def _on_menu_button_key_release_event(self, widget, event):
    #    if event.string == "\r":        #NOTE deprecated (see GdkEventKey documentation) 
    #        # Enter key released
    #        self.main_window.controller().ui_manager.get_popup_menu().popup(None, None, None, None, 0, event.time)
    #    #return True

    ##### Spinner

    #def spinner_start(self):
    #    #self.spinner.set_visible(True)
    #    self.spinner.start()
    # 
    #def spinner_stop(self):
    #    self.spinner.stop()
    #    #self.spinner.set_visible(False)
    
    ##### Progressbar

    #def set_progressbar_pulse(self, pulse):
    #    self.progressbar_pulse = pulse
    #    if (pulse):
    #        self.progressbar_timeout_id = GObject.timeout_add(25, self.do_progressbar_pulse, None)
    #    # Else on the next pulse, do_progressbar_pulse() will return False and 
    #    # the timeout object will be automatically destroyed
    #
    #def do_progressbar_pulse(self, user_data):
    #    #if self.progressbar_pulse:
    #    self.progress_bar.pulse()
    #    return self.progressbar_pulse

class MainTreeView(Gtk.TreeView):

    def __init__(self, main_window):
        #super(MainTreeView, self). __init__()
        Gtk.TreeView.__init__(self)
        
        #self.set_property("fixed-height-mode", True)
        self.main_window = main_window
        self.button_pressed = False
        self.load_image_timeout_seconds = string.str2float(settings.get_config().get(config.NOSECTION, "load-image-timeout-seconds"))
        self.show_images = string.str2bool(settings.get_config().get(config.NOSECTION, "show-images"))

        #selection = self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        ##self.set_style(allow_rules=True)
        #self.set_rules_hint(True)
        self.set_grid_lines(Gtk.TreeViewGridLines.VERTICAL)

        # Interactive search
        self.set_enable_search(True)
        self.set_search_equal_func(self._search_equal_func, None)
        #self.set_search_column(SearchResultColumn.EPISODE)
        self.set_search_column(-1)
        
        self.connect("button-press-event", self._on_button_press_event)
        self.connect("button-release-event", self._on_button_release_event)
        self.connect("key-press-event", self._on_key_press_event)
        self.connect("key-release-event", self._on_key_release_event)
        self.connect("popup-menu", self._on_popup_menu_event)
        self.connect("row-activated", self._on_row_activated)

        if string.str2bool(settings.get_config().get(config.NOSECTION, "show-tooltip")):
            #self.set_tooltip_column(3)
            #self.get_tooltip_window().set_default_size(200, -1)
            self.set_has_tooltip(True)

            #TODO if prog_type not in [get_iplayer.Channels.CH4, get_iplayer.Channels.ITV]:
            #self._on_query_tooltip_path = None
            self.connect("query-tooltip", self._on_query_tooltip)

        # First column
        self.set_show_expanders(False)
        self.set_level_indentation(10)
        if string.str2bool(settings.get_config().get(config.NOSECTION, "show-tree-lines")):
            self.set_enable_tree_lines(True)
            ##self.set_property("grid-line-pattern", "\000\001")
            ##self.set_style(grid_line_pattern="\000\001")

        self._init_columns()

    def init_store(self):
        self.main_window.controller().session_restore()
        
        #if string.str2bool(settings.get_config().get(config.NOSECTION, "start-treeview-populated")):
        #    self.main_window.controller().on_button_find_clicked(None)
        
        # Lazy treeview initialization
        #self.connect("event", self._on_event)
        self.connect("visibility-notify-event", self._on_visibility_notify_event)

    def _init_columns(self):
        compact_treeview = string.str2bool(settings.get_config().get(config.NOSECTION, "compact-tree-view"))
        
        #WORKAROUND. TODO get text label height
        row_height = 20
        #widget = Gtk.Label()
        #(unused_minimum_height, natural_height) = widget.get_preferred_height()
        #row_height = natural_height + WIDGET_BORDER_WIDTH_COMPACT

        #### First column
        
        renderer = Gtk.CellRendererToggle(indicator_size=11)
        renderer.set_alignment(0, 0.5)
        renderer.set_property("height", row_height)
        if compact_treeview:
            renderer.set_property("ypad", 0)
        renderer.connect("toggled", self._on_cell_row_toggled)

        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn(None, renderer, active=SearchResultColumn.DOWNLOAD)
        self.append_column(column)

        ##tooltip = Gtk.Tooltip()
        ##tooltip.set_text(tooltip_text)
        ##self.set_tooltip_cell(tooltip, None, column, renderer)

        #### Second column

        #max_width_chars=256
        # Initial size when column is not resizable
        #renderer = Gtk.CellRendererText(width=256)
        renderer = Gtk.CellRendererText()
        renderer.set_property("height", row_height)
        if compact_treeview:
            renderer.set_property("ypad", 0)
        column = Gtk.TreeViewColumn("Series", renderer, text=SearchResultColumn.SERIES)
        #column.set_expand(True)
        column.set_min_width(100)
        column.set_max_width(600)

        # Resizable column
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        # Initial size when column is resizable
        column.set_fixed_width(256)

        self.append_column(column)
        
        #### Third column

        # Initial size when column is not resizable
        #renderer = Gtk.CellRendererText(width=192)
        renderer = Gtk.CellRendererText()
        renderer.set_property("height", row_height)
        if compact_treeview:
            renderer.set_property("ypad", 0)
        column = Gtk.TreeViewColumn("Categories", renderer, text=SearchResultColumn.CATEGORIES)
        #column.set_expand(True)
        column.set_min_width(100)
        column.set_max_width(600)
        
        # Resizable column
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        # Initial size when column is resizable
        column.set_fixed_width(192)

        self.append_column(column)

        #### Fourth column

        renderer = Gtk.CellRendererText()
        renderer.set_property("height", row_height)
        if compact_treeview:
            renderer.set_property("ypad", 0)
        column = Gtk.TreeViewColumn("Episode ~ Description", renderer, text=SearchResultColumn.EPISODE)
        #column.set_expand(True)
        column.set_min_width(40)
        #column.set_max_width(600)

        # Resizable column
        column.set_resizable(True)
        #TODO? Horizontal scrollbar instead resizable last column.
        #      Horizontal scrollbar appears when the following line and the same line of one of the other resizable columns are commented out
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        #column.set_fixed_width(-1)
        
        self.append_column(column)

    def _get_column_width(self, n):
        return self.get_column(n).get_width()

    #def _search_equal_func(self, model, column, key, tree_iter, search_data):
    #    """ Return false if key matches, i.e. is a substring of cell_text, case-insensitive match). """
    #    cell_text = model.get_value(tree_iter, column)
    #    return not (cell_text and key.lower() in cell_text.lower())
        
    def _search_equal_func(self, model, column, key, tree_iter, search_data):
        """ Return false if key matches, i.e. is a substring in a text cell, case-insensitive match). """
        
        # Get all cell text
        series = model.get_value(tree_iter, SearchResultColumn.SERIES)
        episode = model.get_value(tree_iter, SearchResultColumn.EPISODE)
        if series and episode:
            text = series + "|" + episode
        elif series:
            text = series
        elif episode:
            text = episode
        else:
            text = None
            
        return not (text and key.lower() in text.lower())
        
    # Lazy treeview initialization. Signal when treeview is being displayed on screen
    #def _on_event(self, widget, event):
    def _on_visibility_notify_event(self, event, user_data):
        self.main_window.controller().on_button_find_clicked(None)

        #self.disconnect_by_func(self._on_event)
        self.disconnect_by_func(self._on_visibility_notify_event)

    def _on_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        points_to_row, x, y, model, path, tree_iter = widget.get_tooltip_context(x, y, keyboard_mode)
        if not points_to_row or keyboard_mode or x > self._get_column_width(0):
            # x mouse coordinate is outside the first column
            return False

        #if self._on_query_tooltip_path == path:
        #    return False
        #self._on_query_tooltip_path = path

        channel = model.get_value(tree_iter, SearchResultColumn.CHANNELS)
        image_url = model.get_value(tree_iter, SearchResultColumn.THUMBNAIL_SMALL)

        #categories = model.get_value(tree_iter, SearchResultColumn.CATEGORIES)
        #if not categories or categories == "Unknown":
        #    categories = None

        available = model.get_value(tree_iter, SearchResultColumn.AVAILABLE)
        if not available or available == "Unknown":
            available = None

        duration = model.get_value(tree_iter, SearchResultColumn.DURATION)
        if not duration or duration == "Unknown" or duration == "<duration>":
            duration = None

        ####

        tooltip_text = "" + markup.text2html(channel)
        #if categories is not None:
        #    tooltip_text += "\n" + markup.text2html(categories)
        if available is not None:
            tooltip_text += "\navailable: " + available
        if duration is not None:
            duration_mins = int(duration) // 60
            string = "{0:2}".format(duration_mins // 60) + ":" + \
                         "{0:02}".format(duration_mins % 60)
            string = string.strip()
            tooltip_text += "\nduration: " + string

        tooltip.set_markup(tooltip_text)

        if self.show_images and image_url is not None:
            image = Image.image(image_url, relpath="thumbnails", timeout=self.load_image_timeout_seconds,
                                max_width=ICON_IMAGE_MAX_WIDTH, max_height=ICON_IMAGE_MAX_HEIGHT)
            if image is not None:
                tooltip.set_icon(image.get_pixbuf())

        widget.set_tooltip_cell(tooltip, path, None, None)
        return True

    #### PageUp/PageDown scrolling behavior. Keep cursor on the same row, even if the cursor goes outside the scroll viewport

    def _on_key_press_event(self, widget, event):
        (unused_send_event_explicitly, keyval) =  event.get_keyval()
        if keyval == Gdk.KEY_Page_Up or keyval == Gdk.KEY_Page_Down:
            # Stop other handlers from being invoked
            return True
        # Pass event to other handlers
        return False
    
    def _on_key_release_event(self, widget, event):
        (unused_send_event_explicitly, keyval) =  event.get_keyval()
        if keyval == Gdk.KEY_Page_Up or keyval == Gdk.KEY_Page_Down:
            # Scroll one page
            adjustment = self.main_window.main_tree_view_scrollbars.get_vadjustment()
            value = adjustment.get_value()
            page_increment = adjustment.get_page_increment()
            direction = 1 if keyval == Gdk.KEY_Page_Down else -1
            adjustment.set_value(value + page_increment * direction)
            adjustment.value_changed()
            #adjustment = self.main_window.main_tree_view_scrollbars.set_vadjustment(adjustment)
             
            # Stop other handlers from being invoked
            return True
        # Pass event to other handlers
        return False
    
    ####
    
    def _on_button_press_event(self, widget, event):
        self.button_pressed = True

        if event.type == Gdk.EventType._2BUTTON_PRESS:
            # Double-clicked
            self.main_window.controller().on_button_properties_clicked(None)
            #return True
        elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # Right mouse button pressed
            self.main_window.controller().ui_manager.get_popup_menu().popup(None, None, None, None, event.button, event.time)
            #return True
        #return False
    
    def _on_button_release_event(self, widget, event):
        self.button_pressed = False

    #DOC BUG?
    def _on_popup_menu_event(self, widget):
        self.main_window.ui_manager.get_popup_menu().popup(None, None, None, None, 0, Gtk.get_current_event_time())

    #DOC BUG? extra undocumented parameter: widget (== self)
    def _on_row_activated(self, widget, path, column):
        if not self.button_pressed:
            self._on_cell_row_toggled(None, path)
        
    #DOC BUG?
    def _on_cell_row_toggled(self, widget, path):
        # widget can be None
        model = self.get_model()        
        tree_iter = model.get_iter(path)
        toggle_value = model[path][SearchResultColumn.DOWNLOAD]
        new_toggle_value = not toggle_value

        # Uncheck parent check box, when one of the sibling check boxes or 
        # the current check box becomes unchecked
        #if toggle_value:
        if not new_toggle_value:
            parent_iter = model.iter_parent(tree_iter)
            if parent_iter != None:
                parent_row = model[parent_iter]
                parent_toggle_value = parent_row[SearchResultColumn.DOWNLOAD]
                new_parent_toggle_value = not parent_toggle_value
                # Check expected parent state against current child state
                if parent_toggle_value == toggle_value:
                    # Parent should possibly be toggled
                    # Next, check sibling states against current child state
                    if model.iter_has_child(parent_iter):
                        child_iter = model.iter_children(parent_iter)
                        while child_iter is not None:
                            row = model[child_iter]
                            if row[SearchResultColumn.DOWNLOAD] != toggle_value:
                                break
                            child_iter = model.iter_next(child_iter)
                        if child_iter == None:
                            # All siblings have the same state as the current child (checked)
                            # Toggle parent
                            parent_row[SearchResultColumn.DOWNLOAD] = new_parent_toggle_value

        # Toggle check box
        #new_toggle_value = not model[path][SearchResultColumn.DOWNLOAD]
        new_toggle_value = not toggle_value
        model[path][SearchResultColumn.DOWNLOAD] = new_toggle_value

        # Toggle children check boxes (one level deep)
        if model.iter_has_child(tree_iter):
            child_iter = model.iter_children(tree_iter)
            while child_iter is not None:
                row = model[child_iter]
                # Toggle child
                row[SearchResultColumn.DOWNLOAD] = new_toggle_value
                child_iter = model.iter_next(child_iter)

        # Check (enable) parent check box, when all the sibling check boxes and 
        # the current check box become checked
        if new_toggle_value:
            parent_iter = model.iter_parent(tree_iter)
            if parent_iter != None:
                parent_row = model[parent_iter]
                new_parent_toggle_value = not parent_row[SearchResultColumn.DOWNLOAD]
                # Check expected parent state against current child state
                if new_parent_toggle_value == new_toggle_value:
                    # Parent should possibly be toggled
                    # Next, check sibling states against current child state
                    if model.iter_has_child(parent_iter):
                        child_iter = model.iter_children(parent_iter)
                        while child_iter is not None:
                            row = model[child_iter]
                            if row[SearchResultColumn.DOWNLOAD] != new_toggle_value:
                                break
                            child_iter = model.iter_next(child_iter)
                        if child_iter == None:
                            # All siblings have the same state as the current child (checked)
                            # Toggle parent
                            parent_row[SearchResultColumn.DOWNLOAD] = new_parent_toggle_value

    def set_store(self, tree_rows):
        # Columns in the store: columns listed in get_iplayer.SearchResultColumn
        store = Gtk.TreeStore(bool, str, str, str, str, str, str, str, str, str, str)
        
        locate_search_term = None
        repeat_categories = False
        
        #NOTE Could use "for i, row in enumerate(tree_rows):"
        #     except that "i += 1" to skip a list item has no effect
        root_iter = None
        i = 0
        while i in range(len(tree_rows)):
            row = tree_rows[i]
            if row[SearchResultColumn.EPISODE] is None:
                # Series level (parent/root/level 0)
                repeat_categories = False

                #TODO try catch: if rows[i+ 1][SearchResultColumn.EPISODE] and not rows[i+ 2][SearchResultColumn.EPISODE]:
                if (i + 1 < len(tree_rows) and tree_rows[i + 1][SearchResultColumn.EPISODE]) and \
                   (i + 2 >= len(tree_rows) or not tree_rows[i + 2][SearchResultColumn.EPISODE]):
                    # Series (parent/root/level 0) has only one episode (child/leave/level 1)
                    # Merge the two rows into one
                    #TODO
                    # [1:] means skip the first tree row value: SearchResultColumn.DOWNLOAD
                    #for j, prop_value in enumerate(tree_rows[i + 1][1:]):
                    #    print "j = ", j, prop_value
                    #    row[j + 1] = prop_value
                    row[SearchResultColumn.PID] = tree_rows[i + 1][SearchResultColumn.PID]
                    row[SearchResultColumn.INDEX] = tree_rows[i + 1][SearchResultColumn.INDEX]
                    row[SearchResultColumn.EPISODE] = tree_rows[i + 1][SearchResultColumn.EPISODE]
                    row[SearchResultColumn.CATEGORIES] = tree_rows[i + 1][SearchResultColumn.CATEGORIES]
                    row[SearchResultColumn.CHANNELS] = tree_rows[i + 1][SearchResultColumn.CHANNELS]
                    row[SearchResultColumn.THUMBNAIL_SMALL] = tree_rows[i + 1][SearchResultColumn.THUMBNAIL_SMALL]
                    row[SearchResultColumn.AVAILABLE] = tree_rows[i + 1][SearchResultColumn.AVAILABLE]
                    row[SearchResultColumn.DURATION] = tree_rows[i + 1][SearchResultColumn.DURATION]
                    
                    # Skip merged row (an episode)
                    i += 1                    
                else:
                    # Repeat displaying categories in each row, if the episode's categories of a series are not all the same
                    # Check episodes (children/leaves/level 1) in a series (parent/root/level 0)
                    categories = row[SearchResultColumn.CATEGORIES]
                    j = i + 1
                    while j < len(tree_rows):
                        row_next = tree_rows[j]
                        if row_next[SearchResultColumn.EPISODE] is None:
                            # End of episodes in a series: reached next series level (parent/root/level 0)
                            break
                        if row_next[SearchResultColumn.CATEGORIES] != categories:
                            repeat_categories = True
                            break
                        j += 1
                locate_search_term = row[SearchResultColumn.SERIES]
                row[SearchResultColumn.LOCATE_SEARCH_TERM] = locate_search_term
                if repeat_categories:
                    row[SearchResultColumn.CATEGORIES] = None
                root_iter = store.append(None, row)            
            else:
                # Episode level (child/leave/level 1)
                
                # Copy locate_search_term from series (parent/root/level 0) row
                row[SearchResultColumn.LOCATE_SEARCH_TERM] = locate_search_term
                
                if not repeat_categories:
                    row[SearchResultColumn.CATEGORIES] = None
                store.append(root_iter, row)
            i += 1
        self.set_model(store)
        
        # Expanders are not drawn, so expand the tree now during initialization
        self.expand_all()

class SearchEntry(Gtk.Entry):

    def __init__(self, compact):
        Gtk.Entry.__init__(self)
        
        if compact:
            self.set_icon_from_stock(Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_FIND)
            self.set_icon_tooltip_text(Gtk.EntryIconPosition.PRIMARY, TOOLTIP_SEARCH_FIND)
        self.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_CLEAR)
        self.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, TOOLTIP_SEARCH_CLEAR)
        self.set_placeholder_text("Search")
        self.connect("icon-press", self._on_icon_press)

    def _on_icon_press(self, entry, icon_pos, event):
        #if icon_pos == Gtk.EntryIconPosition.PRIMARY:
        #    # Emit an "activate" signal
        #    signal = GObject.signal_new(...)
        #    signal.emit_by_name(...)
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            entry.set_text("")
            #entry.set_placeholder_text("Search")

####

#NOTE  
#Glade generates the following deprecated Grid property: 
#    <property name="n_rows">1</property>
#It causes a Gtk warning. This property can be removed from the generated .ui file.

#class Builder(Gtk.Builder):
class Builder(object):
    
    def __init__(self):
        self.builder = Gtk.Builder()
        #self.builder.set_translation_domain(textdomain)

        #TODO load all ui/*.ui filenames
        package_pathname = os.path.dirname(os.path.realpath(__file__))
        ui_filename = os.path.join(package_pathname, "preferences.ui")
        self.builder.add_from_file(ui_filename)

####

#NOTE session_save() is done from outside the window class and session_restore() is done from inside the window class,
def _main_quit(main_window, event):
    main_window.controller().session_save()

    if string.str2bool(settings.get_config().get(config.NOSECTION, "clear-cache-on-exit")):
        command_util.clear_cache()

    #WORKAROUND get_root_window()
    main_window.display_busy_mouse_cursor(False)

    Gtk.main_quit(main_window, event)

def main():
    #TODO: raise error count in the tool bar when precondition check(s) fail
    get_iplayer.precheck()

    # Load CSS file. Do this before window.show_all() since some themes don't resize after a CSS update
    screen = Gdk.Screen.get_default()
    css_provider = Gtk.CssProvider()
    package_pathname = os.path.dirname(os.path.realpath(__file__))
    css_filename = os.path.join(package_pathname, "style.css")
    #css_provider.load_from_file(Gio.File.new_for_path(css_filename))
    css_provider.load_from_path(css_filename)
    context = Gtk.StyleContext()
    context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    window = MainWindow()
    #window.init()
    # Icon for alt-tab list
    window.set_icon(Gtk.Image.new_from_file(os.path.dirname(__file__) + "/../" + 
                            get_iplayer_downloader.PROGRAM_NAME + ".svg").get_pixbuf())
    window.connect("delete-event", _main_quit)
    window.show_all()
    
    # Force images on button widgets
    settings = Gtk.Settings.get_default()
    settings.props.gtk_button_images = True

    # Enable threads
    GObject.threads_init()
    #GObject.threads_enter()

    # Allow ctrl+c to quit the program
    signal.signal(signal.SIGINT, lambda signal, frame: Gtk.main_quit())

    Gtk.main()

    #GObject.threads_leave()

if __name__ == "__main__":
    main()
