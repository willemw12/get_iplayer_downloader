#!/usr/bin/env python3

import os
import signal

from gi.repository import Gdk, GObject, Gtk, Pango

# Load application-wide definitions
import get_iplayer_downloader

from get_iplayer_downloader import command_util, get_iplayer, settings
from get_iplayer_downloader.get_iplayer import SinceListIndex, SearchResultColumn, KEY_INDEX
from get_iplayer_downloader.tools import command, command_queue, config, file, markup, string
from get_iplayer_downloader.ui.tools.dialog import ExtendedMessageDialog

#TOOLTIP_FILE_QUIT

TOOLTIP_VIEW_PROPERTIES = "View properties of highlighted programme"
TOOLTIP_VIEW_LOG = "View download log"

#TOOLTIP_EDIT_PREFERENCES

TOOLTIP_TOOLS_DOWNLOAD_OR_PRV_QUEUE = "Download selected programmes, or queue programmes if PVR checked"
TOOLTIP_TOOLS_DOWNLOAD = "Download selected programmes"
TOOLTIP_TOOLS_CLEAR = "Clear programme download selection"
TOOLTIP_TOOLS_REFRESH = "Refresh programme cache, restricted of the selected programme type (radio, podcast, tv)"

TOOLTIP_SEARCH_FIND = "Find programmes"
TOOLTIP_SEARCH_CLEAR = "Clear search text"
TOOLTIP_SEARCH_GO_TO_FIND = "Go to search entry field on the tool bar"
TOOLTIP_SEARCH_ROTATE_SINCE = "Select since programmes were added to the cache"
TOOLTIP_SEARCH_ROTATE_PROG_TYPE = "Select programme type (radio, podcast, tv)"
TOOLTIP_SEARCH_ROTATE_CATEGORY = "Select category"
TOOLTIP_SEARCH_ROTATE_CHANNEL = "Select channel"

TOOLTIP_FILTER_SEARCH_ENTRY = "Search in episode name, programme name and description. Press 'Enter' to search"
TOOLTIP_FILTER_PROGRAMME_TYPE = "Filter on programme type"
TOOLTIP_FILTER_PROGRAMME_CATEGORIES = "Filter on programme categories. Disabled when filter label is 'Categories' or empty"
TOOLTIP_FILTER_PROGRAMME_CHANNELS = "Filter on programme channels. Disabled when filter label is 'Channels' or empty"
TOOLTIP_FILTER_SINCE = "Filter on programmes recently added to the cache. Disabled when filter label is 'Since' or empty"

TOOLTIP_OPTION_FORCE = "Force download or force refresh programme cache"
TOOLTIP_OPTION_ALT_RECORDING_MODES = "Try to download or queue programmes with the alternative set of recording modes"
TOOLTIP_OPTION_FIND_ALL = "Search in all available programme types and channels. Retrieving the programme list may take a long time"

TOOLTIP_TOOLS_PVR_QUEUE = "Queue selected programmes for one-off downloading by get_iplayer --pvr"
TOOLTIP_TOOLS_FUTURE = "Include or exclude future programmes in the search result and property list. Click 'Refresh', with 'Future' enabled, to update the list of future programmes in the cache. The category filter is disabled in 'Future' mode. Enable 'PVR' to queue future programmes for downloading"

TOOLTIP_HELP_HELP = "Help for this program"
TOOLTIP_HELP_ABOUT = "About this program"

TOOLTIP_PROGRESS_BAR = "Downloading / Errors. Click to view the download log, reset the error count or remove log and image cache files"

TOOLTIP_MENU_BUTTON = "Menu. Click here or right-click on the main window"

####

WINDOW_MAIN_HEIGHT = 720

WINDOW_LARGE_WIDTH = 800
WINDOW_LARGE_HEIGHT = 700

WINDOW_MEDIUM_WIDTH = 600
WINDOW_MEDIUM_HEIGHT = 500

WIDGET_BORDER_WIDTH = 4
WIDGET_BORDER_WIDTH_COMPACT = 2

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
        start_maximized = string.str2bool(settings.config().get(config.NOSECTION, "start-maximized"))
        if start_maximized:
            self.maximize()

        self.busy_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.normal_cursor = Gdk.Cursor(Gdk.CursorType.LEFT_PTR)
        
        ####
        
        # Initialize the controller
        self._main_controller = MainWindowController(self)
        
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
        self.ui_manager = UIManager(self)

    def _init_builder(self):
        self.builder = Builder()

    def _init_main_grid(self):
        self.main_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_grid)

    def _init_menu_bar(self):
        if string.str2bool(settings.config().get(config.NOSECTION, "show-menubar")):
            self.menu_bar = self.ui_manager.get_menu_bar()
            self.main_grid.add(self.menu_bar)
        
    def _init_tool_bar_box(self):
        self.tool_bar_box = ToolBarBox(self)
        self.main_grid.add(self.tool_bar_box)
        
    def _init_main_tree_view(self):
        self.main_tree_view_scrollbar = Gtk.ScrolledWindow()
        self.main_tree_view_scrollbar.set_hexpand(True)
        self.main_tree_view_scrollbar.set_vexpand(True)
        self.main_grid.attach_next_to(self.main_tree_view_scrollbar, self.tool_bar_box, Gtk.PositionType.BOTTOM, 1, 2)

        self.main_tree_view = MainTreeView(self)
        self.main_tree_view_scrollbar.add(self.main_tree_view)
        
    def controller(self):
        return self._main_controller
    
    def set_window_title(self, prog_type=get_iplayer.ProgType.RADIO):
        if prog_type:
            self.set_title(prog_type + " - " + get_iplayer_downloader.PROGRAM_NAME)
        else:
            self.set_title(get_iplayer_downloader.PROGRAM_NAME)

    def display_busy_mouse_cursor(self, busy):
        #WORKAROUND get_root_window()
        #    get root window (the desktop), otherwise setting the cursor won't work from a menu
        #    TODO get a window inside this program, not the desktop window, otherwise if the program crashes, the mouse cursor may remain busy on the desktop
        #window = self.get_window()
        window = self.get_root_window()
        if window is not None:
            if busy:
                Gdk.Window.set_cursor(window, self.busy_cursor)
                # Display the cursor immediately
                #Gdk.Display.get_default().sync()
                #self.get_display().sync()
                window.get_display().sync()
            else:
                Gdk.Window.set_cursor(window, self.normal_cursor)

class UIManager():

    UI_INFO = """
<ui>
  <menubar name="MenuBar">
    <menu action="FileMenu">
      <!--
      <menu action="FileNew">
        <menuitem action="FileNewStandard"/>
      </menu>
      <separator/>
      -->
      <menuitem action="FileQuit"/>
    </menu>
    <menu action="EditMenu">
      <menuitem action="EditPreferences"/>
    </menu>
    <menu action="ViewMenu">
      <!--
      <menuitem action="ViewProperties"/>
      -->
      <menuitem action="ViewLog"/>
    </menu>
    <!--
    <menu action="SearchMenu">
      <menuitem action="SearchGoToFind"/>
    </menu>
    -->
    <menu action="ToolsMenu">
      <menuitem action="ViewProperties"/>
      <menuitem action="ToolsDownload"/>
      <menuitem action="ToolsPvrQueue"/>
      <menuitem action="ToolsClear"/>
      <menuitem action="ToolsRefresh"/>
      <separator/>
      <menuitem action="SearchGoToFind"/>
    </menu>
    <menu action="HelpMenu">
      <menuitem action="HelpHelp"/>
      <menuitem action="HelpAbout"/>
    </menu>
  </menubar>
  <!--
  <toolbar name="ToolBar">
    <toolitem action="FileNewStandard"/>
    <toolitem action="FileQuit"/>
  </toolbar>
  -->
  <popup name="PopupMenu">
    <menuitem action="ViewProperties"/>
    <menuitem action="ToolsDownload"/>
    <menuitem action="ToolsPvrQueue"/>
    <menuitem action="ToolsClear"/>
    <menuitem action="ToolsRefresh"/>
    <separator/>
    <menuitem action="SearchGoToFind"/>
    <separator/>
    <menuitem action="EditPreferences"/>
    <separator/>
    <menuitem action="ViewLog"/>
    <separator/>
    <menuitem action="HelpHelp"/>
    <menuitem action="HelpAbout"/>
    <separator/>
    <menuitem action="FileQuit"/>
  </popup>
  <popup name="Hidden">
    <menuitem action="SearchRotateProgrammeType"/>
    <!--
    <menuitem action="SearchRotateCategory"/>
    <menuitem action="SearchRotateChannel"/>
    -->
    <menuitem action="SearchRotateForwardSince"/>
    <menuitem action="SearchRotateBackwardSince"/>

    <!-- Alternative key bindings -->
    <menuitem action="SearchRotateProgrammeType_1"/>
    <menuitem action="SearchRotateCategory_2"/>
    <menuitem action="SearchRotateChannel_3"/>
    <menuitem action="SearchRotateForwardSince_4"/>
    <!-- <menuitem action="SearchRotateBackwardSince_SHIFT_4"/> -->
    <menuitem action="SearchRotateBackwardSince_5"/>
  </popup>
</ui>
"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_manager = self._create_ui_manager()

        action_group = Gtk.ActionGroup("action_group")

        self._add_file_menu_actions(action_group)
        self._add_edit_menu_actions(action_group)
        self._add_view_menu_actions(action_group)
        self._add_search_menu_actions(action_group)
        self._add_tools_menu_actions(action_group)
        self._add_help_menu_actions(action_group)

        self.ui_manager.insert_action_group(action_group)

    def get_menu_bar(self):
        return self.ui_manager.get_widget("/MenuBar")

    def get_popup_menu(self):
        return self.ui_manager.get_widget("/PopupMenu")

    def _add_file_menu_actions(self, action_group):
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)

        action_filenewmenu = Gtk.Action("FileNew", None, None, Gtk.STOCK_NEW)
        action_group.add_action(action_filenewmenu)

        #action_new = Gtk.Action("FileNewStandard", "_New",
        #                        "Create a new file", Gtk.STOCK_NEW)
        #action_new.connect("activate", self._on_menu_file_new_generic)
        #action_group.add_action_with_accel(action_new, None)

        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
        action_filequit.connect("activate", self._on_menu_file_quit)
        action_group.add_action(action_filequit)

    def _add_edit_menu_actions(self, action_group):
        action_group.add_actions([
            ("EditMenu", None, "Edit"),
            ("EditPreferences", Gtk.STOCK_PREFERENCES, "Preferences", None, None, self._on_menu_others)
        ])

    def _add_view_menu_actions(self, action_group):
        action_group.add_actions([
            ("ViewMenu", None, "View"),
            ("ViewProperties", Gtk.STOCK_PROPERTIES, "_Properties", "<alt>Return", TOOLTIP_VIEW_PROPERTIES, self._on_menu_others),
            ("ViewLog", Gtk.STOCK_CAPS_LOCK_WARNING, "_Log", "<control>L", TOOLTIP_VIEW_LOG, self._on_menu_others)
        ])

    def _add_search_menu_actions(self, action_group):
        action_group.add_actions([
            ("SearchMenu", None, "Search"),
            ("SearchGoToFind", Gtk.STOCK_FIND, "_Find", "<control>F", TOOLTIP_SEARCH_GO_TO_FIND, self._on_menu_others),
            ("SearchRotateProgrammeType", None, None, "<control>T", TOOLTIP_SEARCH_ROTATE_PROG_TYPE, self._on_menu_others),
            ("SearchRotateForwardSince", None, None, "<control>S", TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),
            ("SearchRotateBackwardSince", None, None, "<control><shift>S", TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),

            # Alternative key bindings
            ("SearchRotateProgrammeType_1", None, None, "<control>1", TOOLTIP_SEARCH_ROTATE_PROG_TYPE, self._on_menu_others),
            ("SearchRotateCategory_2", None, None, "<control>2", TOOLTIP_SEARCH_ROTATE_CATEGORY, self._on_menu_others),
            ("SearchRotateChannel_3", None, None, "<control>3", TOOLTIP_SEARCH_ROTATE_CHANNEL, self._on_menu_others),
            ("SearchRotateForwardSince_4", None, None, "<control>4", TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),
            #("SearchRotateBackwardSince_SHIFT_4", None, None, "<control><shift>4", TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),
            ("SearchRotateBackwardSince_5", None, None, "<control>5", TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others)
        ])

    def _add_tools_menu_actions(self, action_group):
        action_group.add_actions([
            ("ToolsMenu", None, "Programme"),
            #Gtk.STOCK_GO_DOWN
            ("ToolsDownload", Gtk.STOCK_GOTO_BOTTOM, "_Download", "<control>D", TOOLTIP_TOOLS_DOWNLOAD, self._on_menu_others),
            ("ToolsPvrQueue", Gtk.STOCK_DND_MULTIPLE, "_Queue", "<control>Q", "Queue mode. " + TOOLTIP_TOOLS_PVR_QUEUE, self._on_menu_others),
            ("ToolsClear", Gtk.STOCK_CLEAR, "_Clear", "<control>C", TOOLTIP_TOOLS_CLEAR, self._on_menu_others),
            ("ToolsRefresh", Gtk.STOCK_REFRESH, "_Refresh", "<control>R", TOOLTIP_TOOLS_REFRESH, self._on_menu_others)
        ])

    def _add_help_menu_actions(self, action_group):
        action_group.add_actions([
            ("HelpMenu", None, "Help"),
            ("HelpHelp", Gtk.STOCK_HELP, "_Help", "F1", TOOLTIP_HELP_HELP, self._on_menu_others),
            ("HelpAbout", Gtk.STOCK_ABOUT, "_About", None, TOOLTIP_HELP_ABOUT, self._on_menu_others)
        ])

    #NOTE The underscore (alt-character) mnemonic only works when the widget is shown
    #NOTE An accelerator does not override the desktop accelerator (global desktop keyboard shortcut)
    #NOTE Use glade or the global desktop keyboard shortcuts configuration tool to find "undocumented" keys (Return, ...)
    def _create_ui_manager(self):
        ui_manager = Gtk.UIManager()

        # Throws exception if something went wrong
        ui_manager.add_ui_from_string(UIManager.UI_INFO)

        # Add the accelerator group to the toplevel window
        accelgroup = ui_manager.get_accel_group()
        self.main_window.add_accel_group(accelgroup)
        return ui_manager

    #def _on_menu_file_new_generic(self, widget):
    #    print "A File|New menu item was selected."

    def _on_menu_file_quit(self, widget):
        Gtk.main_quit()

    def _on_menu_others(self, widget):
        name = widget.get_name()
        if name == "EditPreferences":
            self.on_preferences()
        elif name == "ViewProperties":
            self.main_window.controller().on_button_properties_clicked(None)
        elif name == "ViewLog":
            self.main_window.controller().on_progress_bar_button_press_event(None, None)
        elif name == "SearchGoToFind":
            self.main_window.controller().on_accel_go_to_find()
        elif name == "SearchRotateForwardSince" or name == "SearchRotateForwardSince_4":
            self.main_window.controller().on_accel_rotate_since(False)
        #elif name == "SearchRotateBackwardSince" or name == "SearchRotateBackwardSince_SHIFT_4":
        elif name == "SearchRotateBackwardSince" or name == "SearchRotateBackwardSince_5":
            self.main_window.controller().on_accel_rotate_since(True)
        elif name == "SearchRotateProgrammeType" or name == "SearchRotateProgrammeType_1":
            self.main_window.controller().on_accel_rotate_programme_type()
        elif name == "SearchRotateCategory_2":
            self.main_window.controller().on_accel_rotate_category()
        elif name == "SearchRotateChannel_3":
            self.main_window.controller().on_accel_rotate_channel()
        elif name == "ToolsDownload":
            self.main_window.controller().on_button_download_clicked(None)
        elif name == "ToolsPvrQueue":
            self.main_window.controller().on_button_pvr_queue_clicked()
        elif name == "ToolsClear":
            self.main_window.controller().on_button_clear_clicked(None)
        elif name == "ToolsRefresh":
            self.main_window.controller().on_button_refresh_clicked(None)
        elif name == "HelpHelp":
            self.on_help()
        elif name == "HelpAbout":
            self.on_about()

    def on_preferences(self):
        try:
            getattr(self.main_window, "preferences_dialog")
        except AttributeError:
            self.main_window.preferences_dialog = PreferencesDialogWrapper(self.main_window)
        self.main_window.preferences_dialog.run()
        #dialog.hide()

    def on_help(self):
        dialog = Gtk.MessageDialog(self.main_window, 0,
                                   Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                   "Keyboard Shortcuts")
        dialog.format_secondary_text(" ")
        dialog.set_default_response(Gtk.ResponseType.CLOSE)

        content_area = dialog.get_content_area()
        #content_area.set_size_request(800, 400)

        KEYBOARD_SHORTCUTS = [["Shortcut", "Command", "Description"],
                              [" ", None, None],
                              ["alt+enter", "Properties", TOOLTIP_VIEW_PROPERTIES],
                              ["ctrl+c", "Clear", TOOLTIP_TOOLS_CLEAR],
                              ["ctrl+d", "Download", TOOLTIP_TOOLS_DOWNLOAD],
                              ["ctrl+f", "Find", TOOLTIP_SEARCH_GO_TO_FIND],
                              ["ctrl+l", "Log", TOOLTIP_VIEW_LOG],
                              ["ctrl+q", "Queue", TOOLTIP_TOOLS_PVR_QUEUE],
                              ["ctrl+r", "Refresh", TOOLTIP_TOOLS_REFRESH],
                              ["ctrl+s, ctrl+shift+s", "Since", TOOLTIP_SEARCH_ROTATE_SINCE],
                              ["ctrl+t", "Type", TOOLTIP_SEARCH_ROTATE_PROG_TYPE],
                              [" ", None, None],
                              ["ctrl+1", "Type", None],
                              ["ctrl+2", "Category", None],
                              ["ctrl+3", "Channel", None],
                              #["ctrl+4, ctrl+shift+4", "Since", None],
                              ["ctrl+4, ctrl+5", "Since", None],
                              [" ", None, None],
                              ["down-arrow", None, "Go from tool bar to search result"],
                              ["space or enter", None, "Toggle programme selection in search result"]]

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER)
        for i, keyboard_shortcut in enumerate(KEYBOARD_SHORTCUTS):
            for j, label_text in enumerate(keyboard_shortcut):
                if label_text:
                    label = Gtk.Label(label_text, valign=Gtk.Align.START, halign=Gtk.Align.START,
                                      margin_left=16, margin_right=16,
                                      hexpand_set=True, hexpand=True)
                    #label.set_padding(WIDGET_BORDER_WIDTH, 0)
                    grid.attach(label, j, i, 1, 1)
        content_area.add(grid)
        
        #dialog.show_all()
        grid.show_all()

        dialog.run()
        dialog.destroy()

    def on_about(self):
        ##dialog = self.main_window.builder.get_object("AboutDialog")
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self.main_window)

        dialog.set_program_name(get_iplayer_downloader.PROGRAM_NAME)
        #dialog.set_logo_icon_name(Gtk.STOCK_GOTO_BOTTOM)
        dialog.set_logo_icon_name(get_iplayer_downloader.PROGRAM_NAME)
        dialog.set_comments(get_iplayer_downloader.DESCRIPTION + "\n\n" + get_iplayer_downloader.LONG_DESCRIPTION)
        dialog.set_version(get_iplayer_downloader.VERSION)
        dialog.set_website(get_iplayer_downloader.URL)
        dialog.set_website_label(get_iplayer_downloader.URL)
        #NOTE [""] is char** in C
        dialog.set_authors([get_iplayer_downloader.AUTHORS])

        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.run()
        dialog.destroy()

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

class ToolBarBox(Gtk.Box):

    def __init__(self, main_window):
        Gtk.Box.__init__(self, spacing=WIDGET_BORDER_WIDTH)
        self.main_window = main_window

        ####
        
        compact_toolbar = string.str2bool(settings.config().get(config.NOSECTION, "compact-toolbar"))
        if compact_toolbar:
            show_button_labels = False
        else:
            show_button_labels = string.str2bool(settings.config().get(config.NOSECTION, "show-button-labels"))

        focus_chain = []
        
        ####
        
        button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
        button.set_image(Gtk.Image(stock=Gtk.STOCK_PROPERTIES))
        if show_button_labels:
            button.set_label("Properties")
        button.set_tooltip_text(TOOLTIP_VIEW_PROPERTIES)
        button.connect("clicked", self.main_window.controller().on_button_properties_clicked)
        self.pack_start(button, False, False, 0)
        focus_chain.append(button)

        button = Gtk.Button(use_underline=True, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        #Gtk.STOCK_GO_DOWN
        button.set_image(Gtk.Image(stock=Gtk.STOCK_GOTO_BOTTOM))
        if show_button_labels:
            button.set_label("_Download")
        button.set_tooltip_text(TOOLTIP_TOOLS_DOWNLOAD_OR_PRV_QUEUE)
        button.connect("clicked", self.main_window.controller().on_button_download_clicked)
        self.pack_start(button, False, False, 0)
        focus_chain.append(button)

        button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
        button.set_image(Gtk.Image(stock=Gtk.STOCK_CLEAR))
        if show_button_labels:
            button.set_label("Clear")
        button.set_tooltip_text(TOOLTIP_TOOLS_CLEAR)
        button.set_focus_on_click(False)
        button.connect("clicked", self.main_window.controller().on_button_clear_clicked)
        self.pack_start(button, False, False, 0)
        focus_chain.append(button)

        button = Gtk.Button(relief=Gtk.ReliefStyle.NONE, image_position=Gtk.PositionType.TOP)
        button.set_image(Gtk.Image(stock=Gtk.STOCK_REFRESH))
        if show_button_labels:
            button.set_label("Refresh")
        button.set_tooltip_text(TOOLTIP_TOOLS_REFRESH)
        button.set_focus_on_click(False)
        button.connect("clicked", self.main_window.controller().on_button_refresh_clicked)
        self.pack_start(button, False, False, 0)
        focus_chain.append(button)

        ####
        
        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        if show_button_labels:
            button = Gtk.Button(stock=Gtk.STOCK_FIND, relief=Gtk.ReliefStyle.NONE,
                                image_position=Gtk.PositionType.TOP)
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
        
        presets = [[get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO, "Radio"],
                   [get_iplayer.Preset.RADIO, get_iplayer.ProgType.PODCAST, "Podcast"],
                   [get_iplayer.Preset.TV, get_iplayer.ProgType.TV, "TV"]]
        if string.str2bool(settings.config().get(config.NOSECTION, "enable-itv")):
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
        for categories in get_iplayer.Categories.RADIO:
            self.cat_radio_store.append(categories)

        self.cat_podcast_store = Gtk.ListStore(str, str)
        for categories in get_iplayer.Categories.PODCAST:
            self.cat_podcast_store.append(categories)

        self.cat_tv_store = Gtk.ListStore(str, str)
        for categories in get_iplayer.Categories.TV:
            self.cat_tv_store.append(categories)

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

        if string.str2bool(settings.config().get(config.NOSECTION, "enable-category-filter")):
            self.pack_start(self.category_combo, False, False, 0)
            focus_chain.append(self.category_combo)

        ####

        if not compact_toolbar:
            label = Gtk.Label(" Channels:")
            self.pack_start(label, False, False, 0)

        # First in the list the label for all listed channels, the rest are keys
        channels = (get_iplayer.Channels.RADIO).split(",")
        self.chan_radio_store = Gtk.ListStore(str, str)
        first = True
        for channel in channels:
            key = label = channel.strip()
            if first:
                #key = settings.config().get("radio", "channels")
                key = ",".join(channels[1:])
                first = False
            else:
                if compact_toolbar and label.startswith("BBC "):
                    # Remove leading "BBC " substring
                    label = label[len("BBC "):]
            self.chan_radio_store.append([key, label])
        
        # First in the list the label for all listed channels, the rest are keys
        channels = (get_iplayer.Channels.TV).split(",")
        self.chan_tv_store = Gtk.ListStore(str, str)
        first = True
        for channel in channels:
            key = label = channel.strip()
            if first:
                #key = settings.config().get("tv", "channels")
                key = ",".join(channels[1:])
                first = False
            else:
                if compact_toolbar and label.startswith("BBC "):
                    # Remove leading "BBC " substring
                    label = label[len("BBC "):]
            self.chan_tv_store.append([key, label])

        self.chan_itv_store = None
        if string.str2bool(settings.config().get(config.NOSECTION, "enable-itv")):
            # First in the list the label for all listed channels, the rest are keys
            channels = (get_iplayer.Channels.ITV).split(",")
            self.chan_itv_store = Gtk.ListStore(str, str)
            first = True
            for channel in channels:
                key = label = channel.strip()
                if first:
                    #key = settings.config().get("tv", "channels")
                    key = ",".join(channels[1:])
                    first = False
                else:
                    if compact_toolbar and label.startswith("ITV "):
                        # Remove leading "ITV " string
                        label = label[len("ITV "):]
                self.chan_itv_store.append([key, label])

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

        if string.str2bool(settings.config().get(config.NOSECTION, "enable-channel-filter")):
            self.pack_start(self.channel_combo, False, False, 0)
            focus_chain.append(self.channel_combo)

        ####

        if not compact_toolbar:
            label = Gtk.Label(" Since:")
            self.pack_start(label, False, False, 0)

        store = Gtk.ListStore(int, str)
        for since in get_iplayer.SINCE_LIST:
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

        if string.str2bool(settings.config().get(config.NOSECTION, "enable-since-filter")):
            self.pack_start(self.since_combo, False, False, 0)
            focus_chain.append(self.since_combo)

        ####

        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(grid, False, False, 0)
        focus_chain.append(grid)

        self.search_all_check_button = Gtk.CheckButton("All")
        self.search_all_check_button.set_tooltip_text(TOOLTIP_OPTION_FIND_ALL)
        self.search_all_check_button.set_focus_on_click(False)
        grid.add(self.search_all_check_button)
        
        self.force_check_button = Gtk.CheckButton("Force")
        self.force_check_button.set_tooltip_text(TOOLTIP_OPTION_FORCE)
        self.force_check_button.set_focus_on_click(False)
        grid.attach_next_to(self.force_check_button, self.search_all_check_button, Gtk.PositionType.RIGHT, 1, 1)

        self.alt_recording_mode_check_button = Gtk.CheckButton("Alt")
        self.alt_recording_mode_check_button.set_tooltip_text(TOOLTIP_OPTION_ALT_RECORDING_MODES)
        self.alt_recording_mode_check_button.set_focus_on_click(False)
        grid.attach_next_to(self.alt_recording_mode_check_button, self.search_all_check_button, Gtk.PositionType.BOTTOM, 1, 1)
        
        self.future_check_button = Gtk.CheckButton("Future")
        self.future_check_button.set_tooltip_text(TOOLTIP_TOOLS_FUTURE)
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

        ##halign="start", min_horizontal_bar_width=16
        self.progress_bar = Gtk.ProgressBar()
        # Set minimal size: self.progress_bar.set_size_request(90, -1)
        #self.progress_bar.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_valign(Gtk.Align.START)
        self.progress_bar.set_fraction(0.0)
        #self.progress_bar.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        #self.progress_bar.connect("button-press-event", self.main_window.controller().on_progress_bar_button_press_event)
        #self.progress_bar.set_tooltip_text("D (downloading), Q (waiting to download)")
        self.progress_bar.set_tooltip_text(TOOLTIP_PROGRESS_BAR)
        #grid.attach_next_to(self.progress_bar, self.pvr_queue_check_button, Gtk.PositionType.RIGHT, 1, 1)
        event_box.add(self.progress_bar)

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

        ##
        
        self.pvr_queue_check_button = Gtk.CheckButton("PVR")
        self.pvr_queue_check_button.set_tooltip_text("Queue mode. " + TOOLTIP_TOOLS_PVR_QUEUE)
        self.pvr_queue_check_button.set_focus_on_click(False)
        grid.attach_next_to(self.pvr_queue_check_button, event_box, Gtk.PositionType.BOTTOM, 1, 1)

        ####

        #if not compact_toolbar:
        #KEYBOARD FOCUS:
        #event_box = Gtk.EventBox(can_focus=True)
        event_box = Gtk.EventBox(hexpand_set=True, halign=Gtk.Align.END, valign=Gtk.Align.START)
        event_box.connect("button-press-event", self._on_menu_button_press_event)
        #KEYBOARD FOCUS:
        #event_box.connect("key-release-event", self._on_menu_button_key_release_event)
        self.pack_end(event_box, False, False, 0)

        image = Gtk.Image(stock=Gtk.STOCK_PREFERENCES)
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
    #    if event.string == "\r":
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
        self.show_images = string.str2bool(settings.config().get(config.NOSECTION, "show-images"))
        self.load_image_timeout_seconds = string.str2float(settings.config().get(config.NOSECTION, "load-image-timeout-seconds"))

        #selection = self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        ##self.set_style(allow_rules=True)
        #self.set_rules_hint(True)
        self.set_grid_lines(Gtk.TreeViewGridLines.VERTICAL)
        self.set_enable_search(False)
        self.connect("button-press-event", self._on_button_press_event)
        self.connect("button-release-event", self._on_button_release_event)
        self.connect("popup-menu", self._on_popup_menu_event)
        self.connect("row-activated", self._on_row_activated)

        if string.str2bool(settings.config().get(config.NOSECTION, "show-tooltip")):
            #self.set_tooltip_column(3)
            #self.get_tooltip_window().set_default_size(200, -1)
            self.set_has_tooltip(True)

            #self._on_query_tooltip_path = None
            self.connect("query-tooltip", self._on_query_tooltip)

        # First column
        self.set_show_expanders(False)
        self.set_level_indentation(10)
        if string.str2bool(settings.config().get(config.NOSECTION, "show-treelines")):
            self.set_enable_tree_lines(True)
            ##self.set_property("grid-line-pattern", "\000\001")
            ##self.set_style(grid_line_pattern="\000\001")

        self._init_columns()

    def init_store(self):
        self.main_window.controller().session_restore()
        
        #if string.str2bool(settings.config().get(config.NOSECTION, "start-treeview-populated")):
        #    self.main_window.controller().on_button_find_clicked(None)
        
        # Lazy treeview initialization
        #self.connect("event", self._on_event)
        self.connect("visibility-notify-event", self._on_visibility_notify_event)

    # Lazy treeview initialization. Signal when treeview is being displayed on screen
    #def _on_event(self, widget, event):
    def _on_visibility_notify_event(self, event, user_data):
        self.main_window.controller().on_button_find_clicked(None)

        #self.disconnect_by_func(self._on_event)
        self.disconnect_by_func(self._on_visibility_notify_event)

    def _init_columns(self):
        if string.str2bool(settings.config().get(config.NOSECTION, "compact-treeview")):
            widget = Gtk.Label()
            (unused_minimum_height, natural_height) = widget.get_preferred_height()
            row_height = natural_height + WIDGET_BORDER_WIDTH_COMPACT
        else:
            widget = Gtk.CheckButton()
            (unused_minimum_height, natural_height) = widget.get_preferred_height()
            row_height = natural_height
        
        #### First column
        
        renderer = Gtk.CellRendererToggle(indicator_size=11)
        renderer.set_alignment(0, 0.5)
        renderer.set_property("height", row_height)
        renderer.connect("toggled", self._on_cell_row_toggled)

        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn(None, renderer, active=SearchResultColumn.DOWNLOAD)
        self.append_column(column)

        ##tooltip = Gtk.Tooltip()
        ##tooltip.set_text(tooltip_text)
        ##self.set_tooltip_cell(tooltip, None, column, renderer)

        #### Second column

        #max_width_chars=250
        renderer = Gtk.CellRendererText(width=250)
        renderer.set_property("height", row_height)
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn("Serie", renderer, text=SearchResultColumn.SERIE)
        column.set_resizable(True)
        column.set_max_width(600)
        self.append_column(column)
        
        #### Third column

        renderer = Gtk.CellRendererText()
        renderer.set_property("height", row_height)
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn("Episode ~ Description", renderer, text=SearchResultColumn.EPISODE)
        column.set_resizable(True)
        self.append_column(column)

        #### Fourth column

        #renderer = Gtk.CellRendererText(width=250)
        #renderer.set_property("height", row_height)
        ##sizing=Gtk.TreeViewColumn.FIXED
        #column = Gtk.TreeViewColumn("Categories", renderer, text=SearchResultColumn.CATEGORIES)
        #column.set_resizable(True)
        #column.set_max_width(600)
        #self.append_column(column)

    def _get_column_width(self, n):
        return self.get_column(n).get_width()

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

        categories = model.get_value(tree_iter, SearchResultColumn.CATEGORIES)
        if not categories or categories == "Unknown":
            categories = None

        available = model.get_value(tree_iter, SearchResultColumn.AVAILABLE)
        if not available or available == "Unknown":
            available = None

        duration = model.get_value(tree_iter, SearchResultColumn.DURATION)
        if not duration or duration == "Unknown" or duration == "<duration>":
            duration = None

        #

        tooltip_text = "" + markup.text2html(channel)
        if categories is not None:
            tooltip_text += "\n" + markup.text2html(categories)
        if available is not None:
            tooltip_text += "\navailable: " + available
        if duration is not None:
            tooltip_text += "\nduration: " + duration

        tooltip.set_markup(tooltip_text)

        if self.show_images and image_url is not None:
            image = _image(image_url, timeout=self.load_image_timeout_seconds)
            if image is not None:
                tooltip.set_icon(image.get_pixbuf())

        widget.set_tooltip_cell(tooltip, path, None, None)
        return True

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
        
        # Toggle check box
        new_toggle_value = not model[path][SearchResultColumn.DOWNLOAD]
        model[path][SearchResultColumn.DOWNLOAD] = new_toggle_value

        # Toggle children (one level deep) as well
        tree_iter = model.get_iter(path)
        if model.iter_has_child(tree_iter):
            child_iter = model.iter_children(tree_iter)
            while child_iter is not None:
                row = model[child_iter]
                row[SearchResultColumn.DOWNLOAD] = new_toggle_value
                child_iter = model.iter_next(child_iter)

        ## Toggle parent (one level up) when all siblings have the same state
        #parent_iter = model.iter_parent(tree_iter)
        #if parent_iter != None:
        #    toggle_parent = True
        #    iter_next = model.iter_next(tree_iter)
        #    while iter_next != None:
        #        row = model[iter_next]
        #        if row[SearchResultColumn.DOWNLOAD] != new_toggle_value:
        #            toggle_parent = False
        #            break
        #        iter_next = model.iter_next(iter_next)
        #    if toggle_parent:
        #        iter_previous = model.iter_previous(tree_iter)
        #        while iter_previous != None:
        #            row = model[iter_previous]
        #            if row[SearchResultColumn.DOWNLOAD] != new_toggle_value:
        #                toggle_parent = False
        #                break
        #            iter_previous = model.iter_previous(iter_previous)
        #    if toggle_parent:
        #        print "Toggle parent"
        #        row = model[parent_iter]
        #        row[SearchResultColumn.DOWNLOAD] = new_toggle_value

    def set_store(self, tree_rows):
        # Columns in the store: download (True/False), followed by columns listed in get_iplayer.SearchResultColumn
        store = Gtk.TreeStore(bool, str, str, str, str, str, str, str, str, str)
        
        #NOTE Could use "for i, row in enumerate(tree_rows):"
        #     except that "i += 1" to skip a list item has no effect
        root_iter = None
        i = 0
        while i in range(len(tree_rows)):
            row = tree_rows[i]
            if row[SearchResultColumn.EPISODE] is None:
                # Root level row (a serie)
                # If root (a serie) has only one child/leave (an episode) then merge the two into one row
                #TODO try catch: if rows[i+ 1][SearchResultColumn.EPISODE] and not rows[i+ 2][SearchResultColumn.EPISODE]:
                if (i + 1 < len(tree_rows) and tree_rows[i + 1][SearchResultColumn.EPISODE]) and \
                   (i + 2 >= len(tree_rows) or not tree_rows[i + 2][SearchResultColumn.EPISODE]):
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
                root_iter = store.append(None, row)            
            else:
                # Child/leave level row (an episode)
                store.append(root_iter, row)
            i += 1
        self.set_model(store)
        
        # Expanders are not drawn, so expand the tree now during initialization
        self.expand_all()

class PropertiesWindow(Gtk.Window):

    def __init__(self, get_iplayer_output_lines):
        Gtk.Window.__init__(self, title="properties - " + get_iplayer_downloader.PROGRAM_NAME)
        self.set_default_size(WINDOW_LARGE_WIDTH, WINDOW_LARGE_HEIGHT)
        self.set_border_width(WIDGET_BORDER_WIDTH)
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

        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, margin=WIDGET_BORDER_WIDTH)
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
                image = _image(image_url, timeout=timeout)
                if image is not None:
                    self.grid.add(image)

        #### Property table
        
        #NOTE To expand the grid, expand one of its child widgets
        frame = Gtk.Frame(label="Properties", label_xalign=0.01, margin=WIDGET_BORDER_WIDTH, hexpand=True)
        self.grid.add(frame)

        ####
        
        PROP_LABEL_LIST = ["available", "categories", "channel", "desc", "dir",
                           "duration", "episode", "expiry", "expiryrel",
                           "firstbcast", "firstbcastrel", "index", "lastbcast",
                           "lastbcastrel", "longname", "modes", "modesizes",
                           "pid", "player", "senum", "timeadded", "title",
                           "type", "versions", "web"]

        prop_grid = Gtk.Grid(column_homogeneous=False, row_homogeneous=False,
                             margin_top=WIDGET_BORDER_WIDTH, margin_bottom=WIDGET_BORDER_WIDTH)
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
                label1.set_padding(WIDGET_BORDER_WIDTH, 0)
                label1.set_line_wrap(True)
                #label1.set_selectable(False)
                prop_grid.attach(label1, 0, i, 1, 1)

                label2 = Gtk.Label(markup.text2html(prop_value), margin_left=40,
                                   valign=Gtk.Align.START, halign=Gtk.Align.START, use_markup=True)
                label2.set_padding(WIDGET_BORDER_WIDTH, 0)
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

        frame = Gtk.Frame(label="Additional links", label_xalign=0.01, margin=WIDGET_BORDER_WIDTH)
        self.grid.add(frame)

        url = "<a href=\"http://www.bbc.co.uk/iplayer\" title=\"BBC iPlayer\">BBC iPlayer</a>"
        url += "      "

        # Add URLs to get_iplayer's pvr configuration folder and filenames
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url += _files2urls(filepath)
        url += "      "

        # Add URLs to get_iplayer's presets configuration folder and filenames
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += _files2urls(filepath)

        label1 = Gtk.Label(url, valign=Gtk.Align.START, halign=Gtk.Align.START, use_markup=True,
                           margin_top=WIDGET_BORDER_WIDTH, margin_bottom=WIDGET_BORDER_WIDTH)
        label1.set_padding(WIDGET_BORDER_WIDTH, 0)
        label1.set_line_wrap(True)
        #WORD_CHAR
        label1.set_line_wrap_mode(Pango.WrapMode.CHAR)
        #label1.set_selectable(False)
        frame.add(label1)

        ####
        
        box = Gtk.Box(spacing=WIDGET_BORDER_WIDTH)
        self.grid.add(box)
        
        button = Gtk.Button(stock=Gtk.STOCK_CLOSE, margin=WIDGET_BORDER_WIDTH)
        button.connect("clicked", lambda user_data: self.destroy())
        box.pack_end(button, False, False, 0)
        
class PreferencesDialogWrapper(object):

    def __init__(self, main_window):
        self.builder = main_window.builder.builder
        
        self.dialog = self.builder.get_object("PreferencesDialog")

        self.general_clear_cache_on_exit_check_button = self.builder.get_object("PrefsGeneralClearCacheOnExitCheckButton")
        self.general_compact_toolbar_check_button = self.builder.get_object("PrefsGeneralCompactToolBarCheckButton")
        self.general_compact_treeview_check_button = self.builder.get_object("PrefsGeneralCompactTreeViewCheckButton")
        self.general_disable_proxy_check_button = self.builder.get_object("PrefsGeneralDisableProxyCheckButton")
        self.general_show_menubar_check_button = self.builder.get_object("PrefsGeneralShowMenuBarCheckButton")
        self.general_show_tooltip_check_button = self.builder.get_object("PrefsGeneralShowTooltipCheckButton")
        self.general_start_maximized_check_button = self.builder.get_object("PrefsGeneralStartMaximizedCheckButton")
        self.general_terminal_emulator_entry = self.builder.get_object("PrefsGeneralTerminalEmulatorEntry")

        self.radio_channels_entry = self.builder.get_object("PrefsRadioChannelsEntry")
        self.radio_download_path_entry = self.builder.get_object("PrefsRadioDownloadPathEntry")
        self.radio_download_file_chooser_button = self.builder.get_object("PrefsRadioDownloadFileChooserButton")
        self.radio_recording_modes_entry = self.builder.get_object("PrefsRadioRecordingModesEntry")
        self.radio_run_in_terminal_check_button = self.builder.get_object("PrefsRadioRunInTerminalCheckButton")

        self.tv_channels_entry = self.builder.get_object("PrefsTvChannelsEntry")
        self.tv_download_path_entry = self.builder.get_object("PrefsTvDownloadPathEntry")
        self.tv_download_file_chooser_button = self.builder.get_object("PrefsTvDownloadFileChooserButton")
        self.tv_recording_modes_entry = self.builder.get_object("PrefsTvRecordingModesEntry")
        self.tv_run_in_terminal_check_button = self.builder.get_object("PrefsTvRunInTerminalCheckButton")

        ####
        
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url = _files2urls(filepath)
        url += "      "
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += _files2urls(filepath)
        
        label = self.builder.get_object("PrefsAdvGetIPlayerConfLabel")
        label.set_markup(url)

        ####
        
        self.dialog.set_title("preferences - " + get_iplayer_downloader.PROGRAM_NAME)
        self._display_settings()

        self.builder.connect_signals(self)
        self.dialog.connect("response", self._response)

        #self.ok_button = self.builder.get_object("PrefsOkButton")
        #self.dialog.connect("show", self._on_map_event)

    def _display_settings(self):
        """ Retrieve in-memory settings and put them in dialog fields. """

        self.general_clear_cache_on_exit_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "clear-cache-on-exit")))
        self.general_compact_toolbar_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "compact-toolbar")))
        self.general_compact_treeview_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "compact-treeview")))
        self.general_disable_proxy_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "disable-proxy")))
        self.general_show_menubar_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "show-menubar")))
        self.general_show_tooltip_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "show-tooltip")))
        self.general_start_maximized_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "start-maximized")))

        value = settings.config().get(config.NOSECTION, "terminal-emulator")
        if not value:
            # Get default value (as an example value) if stored value is empty
            settings.revert_option(config.NOSECTION, "terminal-emulator")
        self.general_terminal_emulator_entry.set_text(settings.config().get(config.NOSECTION, "terminal-emulator"))

        #
        
        self.radio_channels_entry.set_text(settings.config().get("radio", "channels"))
        download_path = settings.config().get("radio", "download-path")
        self.radio_download_path_entry.set_text(download_path)
        if download_path:
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            self.radio_download_file_chooser_button.set_filename(download_path)
        else:
            # Set to root path
            self.radio_download_file_chooser_button.set_filename(os.sep)
        self.radio_recording_modes_entry.set_text(settings.config().get("radio", "recording-modes"))
        self.radio_run_in_terminal_check_button.set_active(string.str2bool(settings.config().get("radio", "run-in-terminal")))
        
        #
        
        self.tv_channels_entry.set_text(settings.config().get("tv", "channels"))
        download_path = settings.config().get("tv", "download-path")
        self.tv_download_path_entry.set_text(download_path)
        if download_path:
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            self.tv_download_file_chooser_button.set_filename(download_path)
        else:
            # Set to root path
            self.tv_download_file_chooser_button.set_filename(os.sep)
        self.tv_recording_modes_entry.set_text(settings.config().get("tv", "recording-modes"))
        self.tv_run_in_terminal_check_button.set_active(string.str2bool(settings.config().get("tv", "run-in-terminal")))

    def _capture_settings(self):
        """ Retrieve settings from dialog fields and put them in in-memory settings. """

        settings.config().set(config.NOSECTION, "clear-cache-on-exit", str(self.general_clear_cache_on_exit_check_button.get_active()))
        settings.config().set(config.NOSECTION, "compact-toolbar", str(self.general_compact_toolbar_check_button.get_active()))
        settings.config().set(config.NOSECTION, "compact-treeview", str(self.general_compact_treeview_check_button.get_active()))
        settings.config().set(config.NOSECTION, "disable-proxy", str(self.general_disable_proxy_check_button.get_active()))
        settings.config().set(config.NOSECTION, "show-menubar", str(self.general_show_menubar_check_button.get_active()))
        settings.config().set(config.NOSECTION, "show-tooltip", str(self.general_show_tooltip_check_button.get_active()))
        settings.config().set(config.NOSECTION, "start-maximized", str(self.general_start_maximized_check_button.get_active()))
        settings.config().set(config.NOSECTION, "terminal-emulator", self.general_terminal_emulator_entry.get_text())

        settings.config().set("radio", "channels", self.radio_channels_entry.get_text())
        settings.config().set("radio", "download-path", self.radio_download_path_entry.get_text())
        settings.config().set("radio", "recording-modes", self.radio_recording_modes_entry.get_text())
        settings.config().set("radio", "run-in-terminal", str(self.radio_run_in_terminal_check_button.get_active()))
        
        settings.config().set("tv", "channels", self.tv_channels_entry.get_text())
        settings.config().set("tv", "download-path", self.tv_download_path_entry.get_text())
        settings.config().set("tv", "recording-modes", self.tv_recording_modes_entry.get_text())
        settings.config().set("tv", "run-in-terminal", str(self.tv_run_in_terminal_check_button.get_active()))

    #def _on_map_event(self, user_data):
    #    self.ok_button.grab_focus()

    def _on_prefs_revert_clicked(self, user_data):
        """ Only reset settings visible on the preferences dialog window. """

        # Factory-reset all options
        #settings.revert()

        settings.revert_option(config.NOSECTION, "clear-cache-on-exit")
        settings.revert_option(config.NOSECTION, "compact-toolbar")
        settings.revert_option(config.NOSECTION, "compact-treeview")
        settings.revert_option(config.NOSECTION, "disable-proxy")
        settings.revert_option(config.NOSECTION, "show-menubar")
        settings.revert_option(config.NOSECTION, "show-tooltip")
        settings.revert_option(config.NOSECTION, "start-maximized")
        settings.revert_option(config.NOSECTION, "terminal-emulator")

        settings.revert_option("radio", "channels")
        settings.revert_option("radio", "download-path")
        settings.revert_option("radio", "recording-modes")
        settings.revert_option("radio", "run-in-terminal")
        
        settings.revert_option("tv", "channels")
        settings.revert_option("tv", "download-path")
        settings.revert_option("tv", "recording-modes")
        settings.revert_option("tv", "run-in-terminal")

        self._display_settings()

    def _on_prefs_cancel_clicked(self, user_data):
        settings.reload()
        self._display_settings()
          
    def _on_prefs_ok_clicked(self, user_data):
        self._capture_settings()
        settings.save()

    def _on_radio_download_file_chooser_file_set(self, entry_widget):
        filename = self.radio_download_file_chooser_button.get_filename()
        #entry_widget.set_text(GLib.filename_to_utf8(filename, -1, None, 25, None))
        if filename != os.sep:
            # Not root path
            entry_widget.set_text(filename)
        
    def _on_tv_download_file_chooser_file_set(self, entry_widget):
        filename = self.tv_download_file_chooser_button.get_filename()
        #entry_widget.set_text(GLib.filename_to_utf8(filename, -1, None, 25, None))
        if filename != os.sep:
            # Not root path
            entry_widget.set_text(filename)

    def _response(self, dialog, response_id):
        if response_id != Gtk.ResponseType.NONE:    # -1
            self.dialog.hide()

    def run(self):
        self.dialog.run()

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
        #    signal.emity_by_name(...)
        if icon_pos == Gtk.EntryIconPosition.SECONDARY:
            entry.set_text("")
            #entry.set_placeholder_text("Search")

#### Main window controller

class MainWindowController:
    """ Handle the active part of the main window related widgets. Activity between main widgets and 
        activity towards the (source of the gtk widget) model, i.e. get_iplayer.py.
    """
    
    class PresetComboModelColumn:
        PRESET = 0
        PROG_TYPE = 1
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.log_dialog = None
        
        self.processes = 0
        self.errors_offset = 0
        self.downloaded_pid_set = None

    def _update_processes_count(self):
        """ Update the number of running get_iplayer processes. """
        try:
            if os.name == "posix":
                self.processes = int(command.run("echo -n $(ps xo cmd | grep '^/usr/bin/perl /usr/bin/get_iplayer' | wc -l) ; exit 0", quiet=True))
            else:
                self.processes = 0
        except ValueError:
            # Sometmies self.processes is not a valid int (empty string?)
            self.processes = 0
    
    def init(self):
        """ Complete initialization, after the main window has completed its initialization. """

        self.ui_manager = self.main_window.ui_manager
        self.tool_bar_box = self.main_window.tool_bar_box
        self.main_tree_view = self.main_window.main_tree_view

        # Initialize label text
        self.on_progress_bar_update(None)

    def on_button_find_clicked(self, button):
        # button can be None
        search_text = self.tool_bar_box.search_entry.get_text()

        preset = None
        prog_type = None
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]

        categories = None
        combo = self.tool_bar_box.category_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            #WORKAROUND see also get_iplayer.py (at least in Python 2.7)
            #    On some systems, when model[tree_iter][KEY_INDEX] == None, the following exception is raised:
            #    AttributeError: 'NoneType' object has no attribute 'decode'
            #    In the debugger, model[tree_iter][KEY_INDEX] is displayed as a unicode string.
            categories = model[tree_iter][KEY_INDEX]

        channels = None
        combo = self.tool_bar_box.channel_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            channels = model[tree_iter][KEY_INDEX]
            #ALTERNATIVE
            #channels = model.get_value(tree_iter, KEY_INDEX)

        since = 0
        combo = self.tool_bar_box.since_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            since = model[tree_iter][KEY_INDEX]

        search_all = self.tool_bar_box.search_all_check_button.get_active()

        future = self.tool_bar_box.future_check_button.get_active()

        self.main_window.display_busy_mouse_cursor(True)
        output_lines = get_iplayer.search(search_text, preset=preset, prog_type=prog_type,
                                          channels=channels, categories=categories, since=since,
                                          search_all=search_all, future=future)
        self.main_window.display_busy_mouse_cursor(False)

        self.main_tree_view.set_store(output_lines)
        # Scroll to top
        adjustment = self.main_window.main_tree_view_scrollbar.get_vadjustment()
        adjustment.set_value(0.0)
        adjustment.value_changed()
        #adjustment = self.main_window.main_tree_view_scrollbar.set_vadjustment(adjustment)

        self.main_window.set_window_title(prog_type=prog_type)

    def on_button_download_clicked(self, button, pvr_queue=False):
        # button can be None
        preset = None
        prog_type = None
        alt_recording_mode = False
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]
            #channel = model[tree_iter][PresetComboModelColumn.CHANNEL]

            alt_recording_mode = self.tool_bar_box.alt_recording_mode_check_button.get_active()
            if prog_type == get_iplayer.ProgType.ITV:
                alt_recording_mode = "itvnormal,itvhigh"
    
        force = self.tool_bar_box.force_check_button.get_active()
        if button is not None and not pvr_queue:
            # If event was raised from the tool bar download button and not from a keyboard shortcut,
            # then the PVR check button determines the download/queue mode
            pvr_queue = self.tool_bar_box.pvr_queue_check_button.get_active()
        
        # Search selected leaf nodes (the second level) two levels deep
        model = self.main_tree_view.get_model()
        #indices = ""
        pid_list = []
        root_iter = model.get_iter_first()
        while root_iter is not None:
            row = model[root_iter]
            if row[SearchResultColumn.DOWNLOAD] and row[SearchResultColumn.PID]:
                #indices += row[SearchResultColumn.INDEX] + " "
                pid_list.append(row[SearchResultColumn.PID])
            
            #if model.iter_has_child(root_iter):
            child_iter = model.iter_children(root_iter)
            while child_iter is not None:
                row = model[child_iter]
                if row[SearchResultColumn.DOWNLOAD]:
                    #indices += row[SearchResultColumn.INDEX] + " "
                    pid_list.append(row[SearchResultColumn.PID])
                child_iter = model.iter_next(child_iter)
            root_iter = model.iter_next(root_iter)

        future = self.tool_bar_box.future_check_button.get_active()

        #if not indices:
        if len(pid_list) == 0:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "No programmes selected")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
            #return True
            return
        
        ####
        
        # Avoid downloading a programme twice in parallel, otherwise continue downloading
        # twice and let get_iplayer generate an "Already in history" INFO log message.
        # The user can download programmes in parallel without having
        # to clear the previous download selection and therefore avoiding
        # download errors because of two threads trying to download the same programme

        try:
            if os.name == "posix":
                #gipd_processes = int(command.run("echo -n $(ps xo cmd | grep 'get_iplayer_downloader | grep python' | wc -l) ; exit 0", quiet=True))
                gipd_processes = int(command.run("echo -n $(ps xo cmd | grep 'get_iplayer_downloader' | wc -l) ; exit 0", quiet=True))
            else:
                gipd_processes = 1
        except ValueError:
            # Sometimes gipd_processes is not a valid int (empty string?)
            gipd_processes = 1

        # If there are more than one get_iplayer_downloader processes running,
        # then don't perform the 'running in parallel' check (self.processes is
        # the number of >all< the get_iplayer processes on the system)
        # (TODO Limit self.processes to the get_iplayer processes which belong
        # to the current get_iplayer_downloader process)
        if gipd_processes == 1:
            pid_set = set(pid_list)
            # Update self.processes now, to avoid any progress bar update delay
            self._update_processes_count()
            if self.processes > 0:
                if force or self.downloaded_pid_set is None:
                    # Create new download PID list
                    self.downloaded_pid_set = pid_set
                else:
                    # Remove already downloaded PIDs from the PID list
                    pid_list = list(pid_set.difference(self.downloaded_pid_set))
                    # Add PIDs to the downloaded PID list
                    #.union(set(pid_list))
                    self.downloaded_pid_set = self.downloaded_pid_set.union(pid_set)
            #elif self.processes == 0:
            else:
                self.downloaded_pid_set = pid_set
                
            if len(pid_list) == 0:
                dialog = Gtk.MessageDialog(self.main_window, 0,
                                           Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                           "Already downloading all the selected programmes")
                #dialog.format_secondary_text("")
                dialog.run()
                dialog.destroy()
                #return True
                return        
        
        ####
        
        self.main_window.display_busy_mouse_cursor(True)
        launched, process_output = get_iplayer.get(pid_list, pid=True, pvr_queue=pvr_queue, preset=preset,
                                                   prog_type=prog_type, alt_recording_mode=alt_recording_mode,
												   force=force, future=future)
        self.main_window.display_busy_mouse_cursor(False)
        
        if not launched:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "get_iplayer not launched")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
        elif pvr_queue or future:
            # If pvr_queue is false and future is true, then future programmes won't be queued.
            # In that case, to notify the user, show a dialog window in which future programmes are not listed
            dialog = ExtendedMessageDialog(self.main_window, 0,
                                           Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                           "Queued Programmes")
            #dialog.format_secondary_text("")
            dialog.set_default_response(Gtk.ResponseType.CLOSE)
            dialog.get_content_area().set_size_request(WINDOW_MEDIUM_WIDTH, WINDOW_MEDIUM_HEIGHT)
            dialog.format_tertiary_scrolled_text("" if process_output is None else process_output)
            label = dialog.get_scrolled_label()
            label.set_valign(Gtk.Align.START)
            label.set_halign(Gtk.Align.START)
            label.set_selectable(True)
            #label.override_font(Pango.FontDescription("monospace small"))
            label.override_font(Pango.FontDescription("monospace 10"))
            dialog.run()
            dialog.destroy()
        #else:
        #    self.main_window.main_tree_view.grab_focus()

    def on_button_pvr_queue_clicked(self):
        self.on_button_download_clicked(None, pvr_queue=True)

    def on_button_properties_clicked(self, button):
        # button can be None
        preset = None
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]
 
        proxy_disabled = string.str2bool(settings.config().get(config.NOSECTION, "disable-proxy"))

        future = self.tool_bar_box.future_check_button.get_active()

        model, tree_iter = self.main_tree_view.get_selection().get_selected()
        if tree_iter is not None:
            index = model[tree_iter][SearchResultColumn.INDEX]
            if index:
                self.main_window.display_busy_mouse_cursor(True)
                get_iplayer_output_lines = get_iplayer.info(
                                                index, preset=preset, prog_type=prog_type,
                                                proxy_disabled=proxy_disabled, future=future)
                self.main_window.display_busy_mouse_cursor(False)

                window = PropertiesWindow(get_iplayer_output_lines)
                window.show_all()
            else:
                dialog = Gtk.MessageDialog(self.main_window, 0,
                                           Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                           "No programme highlighted. A serie is highlighted")
                #dialog.format_secondary_text("")
                dialog.run()
                dialog.destroy()
        else:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "No programme highlighted")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()

    def on_progress_bar_update(self, user_data):
        self._update_processes_count()
        
        errors = command_util.download_errors()
        if self.errors_offset < 0:
            # Display zero errors by raising the error count offset
            self.errors_offset = errors
        errors = errors - self.errors_offset
        if errors < 0:
            # Reset error count. Log files were probably removed
            errors = 0
            self.errors_offset = 0

        ##self.processes_label.set_label("D: " + str(processes))
        ##self.queue_size_label.set_label("Q: " + str(command_queue.size()))

        #NOTE String formatting: right-aligned (default for int), 4 characters wide: str.format("D:{0:4}  Q:{1:4}", ...)
        #self.progress_bar.set_text(str.format("D:{0}  Q:{1}", int(self.processes), command_queue.size()))
        self.tool_bar_box.progress_bar.set_text("%s / %s" % (self.processes, errors))
        # Full progress bar when TOTAL_WORKER_THREADS get_iplayer processes are running.  % 1 to keep the fraction between 0.0 and 1.0.
        self.tool_bar_box.progress_bar.set_fraction(self.processes / float(command_queue.TOTAL_WORKER_THREADS) % 1)
        # Gray-out
        #self.tool_bar_box.progress_bar.set_sensitive(self.processes != 0 or command_queue.size() != 0)

        return True

    def on_progress_bar_button_press_event(self, widget, event):
        # widget and event can be None
        if self.log_dialog is not None:
            # Dialog already running
            #return False
            return
        if event is not None and event.button != 1:
            # Not left mouse click
            #return False
            return

        # Display download log dialog window
        
        #NOTE Positive ID numbers are for user-defined buttons
        CLEAR_CACHE_BUTTON_ID = 1
        RESET_ERROR_COUNT_BUTTON_ID = 2
        FULL_LOG_BUTTON_ID = 3
        SUMMARY_LOG_BUTTON_ID = 4

        self.log_dialog = ExtendedMessageDialog(self.main_window, 0,
                                Gtk.MessageType.INFO, None, #Gtk.ButtonsType.CLOSE,
                                "", title="download log - " + get_iplayer_downloader.PROGRAM_NAME)

        label = self.log_dialog.get_scrolled_label()
        label.set_valign(Gtk.Align.START)
        label.set_halign(Gtk.Align.START)
        label.set_selectable(True)
        
        #label.override_font(Pango.FontDescription("monospace small"))
        label.override_font(Pango.FontDescription("monospace 10"))
        #ALTERNATIVE
        #css_provider = Gtk.CssProvider()
        #css_provider.load_from_data(b""" * { font: monospace; font-size: 10; } """)
        #context = label.get_style_context()
        #context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.log_dialog.add_button("Clear log and cache", CLEAR_CACHE_BUTTON_ID)
        self.log_dialog.add_button("Reset error count", RESET_ERROR_COUNT_BUTTON_ID)
        self.log_dialog.add_button("Detailed log", FULL_LOG_BUTTON_ID)
        self.log_dialog.add_button("Log", SUMMARY_LOG_BUTTON_ID)
        self.log_dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        
        # Dialog buttons are layed out from right to left
        button = self.log_dialog.get_action_area().get_children()[4]
        button.set_tooltip_text("Remove all log and image cache files")
        button = self.log_dialog.get_action_area().get_children()[3]
        button.set_tooltip_text("Reset error count in the progress bar")
        button = self.log_dialog.get_action_area().get_children()[2]
        button.set_tooltip_text("Refresh today's full download log. When the download log is very large, it will not be displayed")
        button = self.log_dialog.get_action_area().get_children()[1]
        button.set_tooltip_text("Refresh today's summary download log. Error and warning log messages are displayed in bold")
        #button.grab_focus()
        # Close button
        button = self.log_dialog.get_action_area().get_children()[0]
        button.grab_focus()
        
        self.log_dialog.set_default_response(Gtk.ResponseType.CLOSE)
        #self.log_dialog.format_secondary_text("")
        self.log_dialog.get_content_area().set_size_request(WINDOW_LARGE_WIDTH, WINDOW_LARGE_HEIGHT)

        button_id_prev = Gtk.ResponseType.CLOSE
        button_id = SUMMARY_LOG_BUTTON_ID
        full = False
        while True:
            if button_id == FULL_LOG_BUTTON_ID or button_id == SUMMARY_LOG_BUTTON_ID:
                full = (button_id == FULL_LOG_BUTTON_ID)
            if full:
                message_format = "Detailed Download Log"
            else:
                message_format = "Download Log"
            markup = not full
            log_output = command_util.download_log(full=full, markup=markup, sort_by_mtime=True)

            # Set dialog content title
            self.log_dialog.set_property("text", message_format)
            # Set dialog content text
            #NOTE If full download log text is too large, it won't be displayed
            if markup:
                self.log_dialog.format_tertiary_scrolled_markup(log_output)
            else:
                self.log_dialog.format_tertiary_scrolled_text(log_output)
            
            # Grab focus to enable immediate page-up/page-down scrolling with the keyboard
            #label = self.log_dialog.get_scrolled_label()
            #scrolled_window = label.get_parent().get_parent()
            #scrolled_window.grab_focus()
            
            if button_id == FULL_LOG_BUTTON_ID or button_id == SUMMARY_LOG_BUTTON_ID:
                if button_id_prev != button_id:
                    # Log view changed (different log view type or log files removed)
                    # Scroll to top
                    label = self.log_dialog.get_scrolled_label()
                    adjustment = label.get_parent().get_vadjustment()
                    adjustment.set_value(0.0)
                    adjustment.value_changed()
                    #adjustment = label.get_parent().set_vadjustment(adjustment)
            
            if button_id != RESET_ERROR_COUNT_BUTTON_ID:
                # No need to track RESET_ERROR_COUNT_BUTTON_ID because it doesn't affect the log view
                button_id_prev = button_id
                
            button_id = self.log_dialog.run()

            if button_id == CLEAR_CACHE_BUTTON_ID:
                command_util.clear_cache()
            elif button_id == RESET_ERROR_COUNT_BUTTON_ID:
                # Invalidate download errors offset
                self.errors_offset = -1
            elif button_id == Gtk.ResponseType.CLOSE or button_id == Gtk.ResponseType.DELETE_EVENT:
                break
            
        self.log_dialog.destroy()
        self.log_dialog = None

    def on_accel_go_to_find(self):
        self.tool_bar_box.search_entry.grab_focus()

    ####
    
    def _rotate_combo(self, combo, backward):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            active = combo.get_active()
            if backward:
                if active == 0:
                    length = len(combo.get_model())
                    combo.set_active(length - 1)
                else:
                    combo.set_active(active - 1)
            else:
                combo.set_active(active + 1)
                active = combo.get_active()
                if active == -1:
                    combo.set_active(0)

    def on_accel_rotate_since(self, backward):
        self._rotate_combo(self.tool_bar_box.since_combo, backward)

    def on_accel_rotate_programme_type(self):
        self._rotate_combo(self.tool_bar_box.preset_combo, False)
        #NOTE combo.set_active() already causes the invocation of on_combo_preset_changed()
        #self.tool_bar_box.on_combo_preset_changed(combo)

    def on_accel_rotate_category(self):
        self._rotate_combo(self.tool_bar_box.category_combo, False)

    def on_accel_rotate_channel(self):
        self._rotate_combo(self.tool_bar_box.channel_combo, False)

    ####
    
    def on_button_clear_clicked(self, button):
        # button can be None
        model = self.main_tree_view.get_model()
        
        # Search selected nodes one level deep
        for row in model:
            if row[SearchResultColumn.DOWNLOAD]:
                row[SearchResultColumn.DOWNLOAD] = False

        # Search two levels deep
        root_iter = model.get_iter_first()
        while root_iter is not None:
            #if model.iter_has_child(root_iter):
            child_iter = model.iter_children(root_iter)
            while child_iter is not None:
                row = model[child_iter]
                if row[SearchResultColumn.DOWNLOAD]:
                    row[SearchResultColumn.DOWNLOAD] = False
                child_iter = model.iter_next(child_iter)
            root_iter = model.iter_next(root_iter)

        self.main_tree_view.get_selection().unselect_all()

    def on_button_refresh_clicked(self, button):
        # button can be None
        
        ### Refresh programme cache

        preset = None
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]

        channels = None
        combo = self.tool_bar_box.channel_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            channels = model[tree_iter][KEY_INDEX]

        future = self.tool_bar_box.future_check_button.get_active()

        self.main_window.display_busy_mouse_cursor(True)
        get_iplayer.refresh(preset=preset, prog_type=prog_type, channels=channels, future=future)
        self.main_window.display_busy_mouse_cursor(False)
        
        ### Refresh programme list

        self.on_button_find_clicked(None)

    def on_combo_preset_changed(self, combo):
        """ Synchronize associated model settings. """

        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]
            
            # Synchronize category filter
            if prog_type == get_iplayer.ProgType.RADIO:
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_radio_store)
            elif prog_type == get_iplayer.ProgType.PODCAST:
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_podcast_store)
            elif prog_type == get_iplayer.ProgType.TV:
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_tv_store)
            elif prog_type == get_iplayer.ProgType.ITV:
                #self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_tv_store)
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_disabled_store)
            self.tool_bar_box.category_combo.set_active(0)

            # Synchronize channel filter
            if preset == get_iplayer.Preset.RADIO:
                self.tool_bar_box.channel_combo.set_model(self.tool_bar_box.chan_radio_store)
            elif preset == get_iplayer.Preset.TV:
                if prog_type == get_iplayer.ProgType.ITV:
                    self.tool_bar_box.channel_combo.set_model(self.tool_bar_box.chan_itv_store)
                else:
                    self.tool_bar_box.channel_combo.set_model(self.tool_bar_box.chan_tv_store)
            self.tool_bar_box.channel_combo.set_active(0)

            # Limit the initial podcast search result by enabling the since filter
            combo = self.tool_bar_box.since_combo
            model = combo.get_model()
            if prog_type == get_iplayer.ProgType.PODCAST:
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    #model = combo.get_model()
                    since = model[tree_iter][KEY_INDEX]
                    if since == 0:
                        # Set to longest, but not unlimited, since filter
                        combo.set_active(len(model) - 1)
            elif combo.get_active() == len(model) - 1:
                # Disable since filter
                combo.set_active(SinceListIndex.FOREVER)

    def on_check_button_future_clicked(self, check_button):
        if check_button.get_active():
            self.tool_bar_box.pvr_queue_check_button.set_active(True)

            ## Limit the initial search result to future programmes
            #combo = self.tool_bar_box.since_combo
            #combo.set_active(SinceListIndex.FUTURE)

            # Disable the category filter. Get_iplayer doesn't support it 
            # and future programme data sometimes lacks the categories property
            self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_disabled_store)
            self.tool_bar_box.category_combo.set_active(0)
        else:
            self.tool_bar_box.pvr_queue_check_button.set_active(False)

            # Set since filter to now or as close as possible (since 1 hour)
            #combo = self.tool_bar_box.since_combo
            #tree_iter = combo.get_active_iter()
            #if tree_iter is not None:
            #    model = combo.get_model()
            #    since = model[tree_iter][KEY_INDEX]
            #    if since == SinceListIndex.FUTURE:
            #        combo.set_active(SinceListIndex.FOREVER)

            # Restore category filter
            self.on_combo_preset_changed(self.tool_bar_box.preset_combo)

    ####
    
    def session_save(self):
        restore_session = string.str2bool(settings.config().get(config.NOSECTION, "restore-session"))
        if restore_session:
            #preset = None
            prog_type = None
            #channel = None
            combo = self.tool_bar_box.preset_combo
            tree_iter = combo.get_active_iter()
            if tree_iter is not None:
                model = combo.get_model()
                #preset = model[tree_iter][PresetComboModelColumn.PRESET]
                prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]
                #channel = model[tree_iter][PresetComboModelColumn.CHANNEL]

            categories = None
            if string.str2bool(settings.config().get(config.NOSECTION, "enable-category-filter")):
                categories = ""
                combo = self.tool_bar_box.category_combo
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    model = combo.get_model()
                    categories = model[tree_iter][KEY_INDEX]

            channels = None
            if string.str2bool(settings.config().get(config.NOSECTION, "enable-channel-filter")):
                channels = ""
                combo = self.tool_bar_box.channel_combo
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    model = combo.get_model()
                    channels = model[tree_iter][KEY_INDEX]

            since = -1
            if string.str2bool(settings.config().get(config.NOSECTION, "enable-since-filter")):
                since = 0
                combo = self.tool_bar_box.since_combo
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    model = combo.get_model()
                    since = model[tree_iter][KEY_INDEX]

            # Save values

            # If not an empty string (and not None)
            if prog_type is not None:
                settings.config().set("session", "programme-type", prog_type)
            if categories is not None:
                settings.config().set("session", "categories", categories)
            if channels is not None:
                settings.config().set("session", "channels", channels)
            if since >= 0:
                settings.config().set("session", "since", str(since))
            
            settings.save()
    
    def session_restore(self):
        restore_session = string.str2bool(settings.config().get(config.NOSECTION, "restore-session"))
        if restore_session:
            prog_type = settings.config().get("session", "programme-type")
            categories = settings.config().get("session", "categories")
            channels = settings.config().get("session", "channels")
            #NOTE Variables created in the try clause or except clause remain allocated after the try-except statement
            try:
                since = int(settings.config().get("session", "since"))
            except ValueError:
                since = 0

            # If empty string or None (in case of an error) or itv has been disabled, then set the default value
            if not prog_type or (prog_type == "itv" and not string.str2bool(settings.config().get(config.NOSECTION, "enable-itv"))):
                prog_type = get_iplayer.ProgType.RADIO
            if not categories:
                categories = ""
            if not channels:
                channels = ""

            # Don't restore when filter widget is disabled
            if not string.str2bool(settings.config().get(config.NOSECTION, "enable-category-filter")):
                categories = None
            if not string.str2bool(settings.config().get(config.NOSECTION, "enable-channel-filter")):
                channels = None
            if not string.str2bool(settings.config().get(config.NOSECTION, "enable-since-filter")):
                since = -1

            # Restore values
            
            #ALTERNATIVE way of looping (see categories and since looping below)
            combo = self.tool_bar_box.preset_combo
            model = combo.get_model()
            if model is not None:
                tree_iter = model.get_iter_first()
                i = 0
                while tree_iter is not None:
                    value = model.get_value(tree_iter, 1)
                    if value == prog_type:
                        combo.set_active(i)
                        #NOTE combo.set_active() already causes the invocation of on_combo_preset_changed()
                        #self.on_combo_preset_changed(combo)
                        break
                    tree_iter = model.iter_next(tree_iter)
                    i += 1
                self.on_combo_preset_changed(combo)

            if categories:
                combo = self.tool_bar_box.category_combo
                model = combo.get_model()
                if model is not None:
                    # Default
                    #combo.set_active(0)
                    tree_iter = model.get_iter_first()
                    while tree_iter is not None:
                        model = combo.get_model()
                        # Find the categories key
                        if model[tree_iter][KEY_INDEX] == categories:
                            combo.set_active_iter(tree_iter)
                            break
                        tree_iter = model.iter_next(tree_iter)

            if channels:
                combo = self.tool_bar_box.channel_combo
                model = combo.get_model()
                if model is not None:
                    # Default
                    #combo.set_active(0)
                    tree_iter = model.get_iter_first()
                    while tree_iter is not None:
                        model = combo.get_model()
                        # Find the channels key
                        if model[tree_iter][KEY_INDEX] == channels:
                            combo.set_active_iter(tree_iter)
                            break
                        tree_iter = model.iter_next(tree_iter)

            if since >= 0:
                combo = self.tool_bar_box.since_combo
                model = combo.get_model()
                if model is not None:
                    # Default
                    #combo.set_active(SinceListIndex.FOREVER)
                    tree_iter = model.get_iter_first()
                    while tree_iter is not None:
                        model = combo.get_model()
                        if model[tree_iter][KEY_INDEX] == int(since):
                            combo.set_active_iter(tree_iter)
                            break
                        tree_iter = model.iter_next(tree_iter)

####

def _image(url, timeout=0.0):
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

def _files2urls(filepath):
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

####

#NOTE session_save() is done from outside the window class and session_restore() is done from inside the window class,
def _main_quit(main_window, event):
    main_window.controller().session_save()

    if string.str2bool(settings.config().get(config.NOSECTION, "clear-cache-on-exit")):
        command_util.clear_cache()

    #WORKAROUND get_root_window()
    main_window.display_busy_mouse_cursor(False)

    Gtk.main_quit(main_window, event)

def main():
    get_iplayer.check_preset_files()

    # Load css file. Do this before window.show_all() since some themes don't resize after a css update
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
    window.connect("delete-event", _main_quit)
    window.show_all()
    
    # Force images on buttons
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
