#!/usr/bin/env python

import os
import signal
from gi.repository import Gdk, Gtk, GObject, Pango, Gio

# Application-wide constants
import get_iplayer_downloader.common

from get_iplayer_downloader import get_iplayer, settings
from get_iplayer_downloader.get_iplayer import SearchResultColumn
from get_iplayer_downloader.tools import command, config, file, markup, string
from get_iplayer_downloader.ui.tools.dialog import ExtendedMessageDialog

BORDER_WIDTH = 4

####

#TOOLTIP_FILE_QUIT

TOOLTIP_VIEW_PROPERTIES = "View properties of highlighted programme (of programme in focus)"

#TOOLTIP_EDIT_PREFERENCES

TOOLTIP_TOOLS_DOWNLOAD_OR_PRV_QUEUE = "Download selected programmes or queue programmes if PVR checked"
TOOLTIP_TOOLS_DOWNLOAD = "Download selected programmes"
TOOLTIP_TOOLS_PVR_QUEUE = "Queue selected programmes for one-off downloading by get_iplayer pvr"
TOOLTIP_TOOLS_CLEAR = "Clear programme download selection"
TOOLTIP_TOOLS_REFRESH = "Refresh programme cache"

TOOLTIP_SEARCH_FIND = "Find programmes"
TOOLTIP_SEARCH_GO_TO_FIND = "Go to search entry field on the tool bar"
TOOLTIP_SEARCH_ROTATE_PROG_TYPE = "Rotate between programme types (radio, podcast, tv)"

TOOLTIP_FILTER_SEARCH_ENTRY = "Filter programme name and description"
TOOLTIP_FILTER_PROGRAMME_TYPE = "Programme type"
TOOLTIP_FILTER_PROGRAMME_CATEGORY = "Programme category"
TOOLTIP_FILTER_SINCE = "Limit search to recently available programmes"

TOOLTIP_OPTION_FORCE_DOWNLOAD = "Force download"
TOOLTIP_OPTION_HD_TV = "HD TV recording mode. Overrides the default TV mode"
TOOLTIP_OPTION_FULL_PROXY = "Force full proxy mode. Only applies to the retrieval of programme properties. Useful outside the UK. When enabled, properties will include the available tv download sizes"
TOOLTIP_OPTION_FIND_ALL = "Search in all programme types and channels. Either all radio and podcast channels or all tv channels"

TOOLTIP_HELP_HELP = "Help for this program"
TOOLTIP_HELP_ABOUT = "About this program"

####

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_window_title()
        # Set minimal size: self.set_size_request(...)
        self.set_default_size(960, 720)
        self.set_border_width(BORDER_WIDTH)
        if string.str2bool(settings.config().get(config.NOSECTION, "start-maximized")):
            self.maximize()
        
        self.main_controller = MainWindowController(self)
        
        self._init_ui_manager()
        self._init_builder()

        self._init_main_grid()
        #self._init_menu_bar()
        self._init_tool_bar_box()
        self._init_main_tree_view()

        self.main_controller.init()
        self.main_tree_view.init_store()        

    def _init_ui_manager(self):
        self.ui_manager = UIManager(self)

    def _init_builder(self):
        self.builder = Builder()

    def _init_main_grid(self):
        self.main_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.main_grid)

    #def _init_menu_bar(self):
    #    self.menu_bar = self.ui_manager.get_menu_bar()
    #    self.main_grid.add(self.menu_bar)
        
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
        
    def set_window_title(self, prog_type=get_iplayer.ProgType.RADIO):
        self.set_title(prog_type + " - " + get_iplayer_downloader.common.__program_name__)

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
      <menuitem action="ViewProperties"/>
    </menu>
    <menu action="SearchMenu">
      <menuitem action="SearchGoToFind"/>
    </menu>
    <menu action="ToolsMenu">
      <menuitem action="ToolsDownload"/>
      <menuitem action="ToolsPvrQueue"/>
      <menuitem action="ToolsClear"/>
      <menuitem action="ToolsRefresh"/>
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
    <menuitem action="HelpHelp"/>
    <menuitem action="HelpAbout"/>
  </popup>
  <popup name="Hidden">
    <menuitem action="SearchRotateProgrammeType"/>
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
            ("ViewProperties", Gtk.STOCK_PROPERTIES, "Properties", "<alt>Return", TOOLTIP_VIEW_PROPERTIES, self._on_menu_others)
        ])

    def _add_search_menu_actions(self, action_group):
        action_group.add_actions([
            ("SearchMenu", None, "Search"),
            ("SearchGoToFind", Gtk.STOCK_FIND, "Find", "<control>F", TOOLTIP_SEARCH_GO_TO_FIND, self._on_menu_others),
            ("SearchRotateProgrammeType", None, None, "<control>T", TOOLTIP_SEARCH_ROTATE_PROG_TYPE, self._on_menu_others)
        ])

    def _add_tools_menu_actions(self, action_group):
        action_group.add_actions([
            ("ToolsMenu", None, "Tools"),
            ("ToolsDownload", Gtk.STOCK_GO_DOWN, "Download", "<control>D", TOOLTIP_TOOLS_DOWNLOAD, self._on_menu_others),
            ("ToolsPvrQueue", Gtk.STOCK_DND_MULTIPLE, "_Queue", "<control>Q", TOOLTIP_TOOLS_PVR_QUEUE, self._on_menu_others),
            ("ToolsClear", Gtk.STOCK_CLEAR, "Clear", "<control>C", TOOLTIP_TOOLS_CLEAR, self._on_menu_others),
            ("ToolsRefresh", Gtk.STOCK_REFRESH, "Refresh", "<control>R", TOOLTIP_TOOLS_REFRESH, self._on_menu_others)
        ])

    def _add_help_menu_actions(self, action_group):
        action_group.add_actions([
            ("HelpMenu", None, "Help"),
            ("HelpHelp", Gtk.STOCK_HELP, "Help", "F1", TOOLTIP_HELP_HELP, self._on_menu_others),
            ("HelpAbout", Gtk.STOCK_ABOUT, "About", None, TOOLTIP_HELP_ABOUT, self._on_menu_others)
        ])

    #NOTE The underscore (alt-<character) mnemonic only works when the widget is shown
    #NOTE An accelerator does not override the desktop accelerator (global shortcut)
    #NOTE Use glade or desktop shortcut keys system configration tool to find "undocumented" keys (Return, ...)
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
            self.main_window.main_controller.on_button_properties_clicked(None)
        elif name == "SearchGoToFind":
            self.main_window.main_controller.on_accel_go_to_find()
        elif name == "SearchRotateProgrammeType":
            self.main_window.main_controller.on_accel_rotate_programme_type()
        elif name == "ToolsDownload":
            self.main_window.main_controller.on_button_download_clicked(None)
        elif name == "ToolsPvrQueue":
            self.main_window.main_controller.on_button_pvr_queue_clicked()
        elif name == "ToolsClear":
            self.main_window.main_controller.on_button_clear_clicked(None)
        elif name == "ToolsRefresh":
            self.main_window.main_controller.on_button_refresh_clicked(None)
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
                                   "Shortcut keys")
        dialog.set_default_response(Gtk.ResponseType.CLOSE)
        dialog.format_secondary_text(" ")

        content_area = dialog.get_content_area()
        #content_area.set_size_request(800, 400)

        SHORTCUT_KEYS = [["alt + enter", "Properties", TOOLTIP_VIEW_PROPERTIES],
                         ["ctrl + d", "Download", TOOLTIP_TOOLS_DOWNLOAD],
                         ["ctrl + q", "Queue", TOOLTIP_TOOLS_PVR_QUEUE],
                         ["ctrl + f", "Find", TOOLTIP_SEARCH_GO_TO_FIND],
                         ["ctrl + t", "Toggle", TOOLTIP_SEARCH_ROTATE_PROG_TYPE],
                         ["ctrl + c", "Clear", TOOLTIP_TOOLS_CLEAR],
                         ["ctrl + r", "Refresh", TOOLTIP_TOOLS_REFRESH],
                         [" ", None, None],
                         ["down-arrow", None, "Go from tool bar to search result"],
                         ["space or enter", None, "Toggle programme selection in search result"]]

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER)
        for i, shortcut_key in enumerate(SHORTCUT_KEYS):
            for j, label in enumerate(shortcut_key):
                if label:
                    label = Gtk.Label(label, valign=Gtk.Align.START, halign=Gtk.Align.START,
                                      margin_left=16, margin_right=16, 
                                      hexpand_set=True, hexpand=True)
                    #label.set_padding(BORDER_WIDTH, 0)
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

        dialog.set_program_name(get_iplayer_downloader.common.__program_name__)
        dialog.set_comments(get_iplayer_downloader.common.__description__ + "\n\n" + get_iplayer_downloader.common.__long_description__)
        dialog.set_version(get_iplayer_downloader.common.__version__)
        dialog.set_website(get_iplayer_downloader.common.__url__)
        dialog.set_website_label(get_iplayer_downloader.common.__url__)
        #NOTE '[""]' means 'char**' in C
        dialog.set_authors([get_iplayer_downloader.common.__authors__])

        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.run()
        dialog.destroy()

#NOTE on Glade
# Glade generates the following deprecated Grid property: 
#     <property name="n_rows">1</property>
# It causes a Gtk warning. This property can be removed from the generated .ui file.

#class Builder(Gtk.Builder):
class Builder(object):
    
    def __init__(self):
        self.builder = Gtk.Builder()
        #self.builder.set_translation_domain(textdomain)

        #TODO load all ui/*.ui files
        package_pathname = os.path.dirname(os.path.realpath(__file__))
        ui_filename = os.path.join(package_pathname, "preferences.ui")
        self.builder.add_from_file(ui_filename)

class ToolBarBox(Gtk.Box):

    def __init__(self, main_window):
        Gtk.Box.__init__(self, spacing=BORDER_WIDTH)
        self.main_window = main_window
        
        ####
        
        hide_label = string.str2bool(settings.config().get(config.NOSECTION, "compact-toolbar"))

        def _label(label):
            #NOTE conditional expression (inline if-then-else)
            return None if hide_label else label
        
        ####
        
        button = Gtk.Button(label="_Download", use_underline=True, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
        button.set_tooltip_text(TOOLTIP_TOOLS_DOWNLOAD_OR_PRV_QUEUE)
        button.connect("clicked", self.main_window.main_controller.on_button_download_clicked)
        self.pack_start(button, False, False, 0)

        button = Gtk.Button(stock=Gtk.STOCK_PROPERTIES, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text(TOOLTIP_VIEW_PROPERTIES)
        button.connect("clicked", self.main_window.main_controller.on_button_properties_clicked)
        self.pack_start(button, False, False, 0)

        button = Gtk.Button(stock=Gtk.STOCK_CLEAR, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text(TOOLTIP_TOOLS_CLEAR)
        button.set_focus_on_click(False)
        button.connect("clicked", self.main_window.main_controller.on_button_clear_clicked)
        self.pack_start(button, False, False, 0)

        button = Gtk.Button(stock=Gtk.STOCK_REFRESH, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text(TOOLTIP_TOOLS_REFRESH)
        button.set_focus_on_click(False)
        button.connect("clicked", self.main_window.main_controller.on_button_refresh_clicked)
        self.pack_start(button, False, False, 0)
        #button.grab_focus()
        
        ####
        
        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        #button = Gtk.Button(label="_Update", use_underline=True, relief=Gtk.ReliefStyle.NONE,
        #                    image_position=Gtk.PositionType.TOP)
        #button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_UP))
        #button.set_tooltip_text("Update programmes list")
        button = Gtk.Button(stock=Gtk.STOCK_FIND, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text(TOOLTIP_SEARCH_FIND)
        button.connect("clicked", self.main_window.main_controller.on_button_find_clicked)
        self.pack_start(button, False, False, 0)

        self.search_entry = SearchEntry()
        self.search_entry.set_tooltip_text(TOOLTIP_FILTER_SEARCH_ENTRY)
        self.search_entry.connect("activate", self.main_window.main_controller.on_button_find_clicked)
        self.pack_start(self.search_entry, False, False, 0)
        self.search_entry.grab_focus()

        ####

        label = Gtk.Label(_label(" Type:"))
        self.pack_start(label, False, False, 0)
        
        #NOTE Reusing radio channels in podcast preset
        presets = [[get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO,
                    get_iplayer.Channel.RADIO, "Radio"],
                   [get_iplayer.Preset.RADIO, get_iplayer.ProgType.PODCAST,
                    get_iplayer.Channel.RADIO, "Podcast"],
                   [get_iplayer.Preset.TV, get_iplayer.ProgType.TV,
                    get_iplayer.Channel.TV, "TV"]]
        store = Gtk.ListStore(str, str, str, str)
        for preset in presets:
            store.append(preset)

        self.preset_combo = Gtk.ComboBox.new_with_model(store)
        #self.preset_combo.set_active(-1)
        
        self.preset_combo.set_valign(Gtk.Align.CENTER)
        self.preset_combo.set_tooltip_text(TOOLTIP_FILTER_PROGRAMME_TYPE)
        self.preset_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.preset_combo.pack_start(renderer_text, True)
        self.preset_combo.add_attribute(renderer_text, "text", 3)
        self.preset_combo.connect("changed", self.main_window.main_controller.on_combo_preset_changed)
        self.pack_start(self.preset_combo, False, False, 0)
        
        ####
        
        label = Gtk.Label(_label(" Category:"))
        self.pack_start(label, False, False, 0)

        self.cat_radio_store = Gtk.ListStore(str, str)
        for category in get_iplayer.Category.RADIO:
            self.cat_radio_store.append(category)

        self.cat_tv_store = Gtk.ListStore(str, str)
        for category in get_iplayer.Category.TV:
            self.cat_tv_store.append(category)

        #self.category_combo = Gtk.ComboBox.new_with_model(self.cat_radio_store)
        self.category_combo = Gtk.ComboBox()
        # Mark as unselected, to allow it to be set automatically (by session restore) 
        self.category_combo.set_active(-1)
        
        self.category_combo.set_valign(Gtk.Align.CENTER)
        self.category_combo.set_tooltip_text(TOOLTIP_FILTER_PROGRAMME_CATEGORY)
        self.category_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.category_combo.pack_start(renderer_text, True)
        self.category_combo.add_attribute(renderer_text, "text", 1)
        self.pack_start(self.category_combo, False, False, 0)

        ####

        label = Gtk.Label(_label(" Since:"))
        self.pack_start(label, False, False, 0)

        store = Gtk.ListStore(int, str)
        for since in get_iplayer.SINCE_LIST:
            store.append(since)

        self.since_combo = Gtk.ComboBox.new_with_model(store)
        self.since_combo.set_active(0)

        self.since_combo.set_valign(Gtk.Align.CENTER)
        self.since_combo.set_tooltip_text(TOOLTIP_FILTER_SINCE)
        self.since_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.since_combo.pack_start(renderer_text, True)
        self.since_combo.add_attribute(renderer_text, "text", 1)
        self.pack_start(self.since_combo, False, False, 0)

        ####

        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(grid, False, False, 0)

        self.force_download_check_button = Gtk.CheckButton("Force")
        self.force_download_check_button.set_tooltip_text(TOOLTIP_OPTION_FORCE_DOWNLOAD)
        self.force_download_check_button.set_focus_on_click(False)
        #grid.pack_start(self.force_download_check_button, False, False, 0)
        grid.add(self.force_download_check_button)
        
        self.hd_tv_check_button = Gtk.CheckButton("HD")
        self.hd_tv_check_button.set_tooltip_text(TOOLTIP_OPTION_HD_TV)
        self.hd_tv_check_button.set_focus_on_click(False)
        #grid.pack_start(self.force_download_check_button, False, False, 0)
        grid.attach_next_to(self.hd_tv_check_button, self.force_download_check_button, Gtk.PositionType.RIGHT, 1, 1)
        
        self.proxy_check_button = Gtk.CheckButton("Proxy")
        self.proxy_check_button.set_tooltip_text(TOOLTIP_OPTION_FULL_PROXY)
        self.proxy_check_button.set_focus_on_click(False)
        #grid.pack_start(self.proxy_check_button, False, False, 0)
        grid.attach_next_to(self.proxy_check_button, self.force_download_check_button, Gtk.PositionType.BOTTOM, 1, 1)
        
        self.search_all_check_button = Gtk.CheckButton("All")
        self.search_all_check_button.set_tooltip_text(TOOLTIP_OPTION_FIND_ALL)
        self.search_all_check_button.set_focus_on_click(False)
        #grid.pack_start(self.search_all_check_button, False, False, 0)
        grid.attach_next_to(self.search_all_check_button, self.proxy_check_button, Gtk.PositionType.RIGHT, 1, 1)

        ####
        
        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(grid, False, False, 0)

        #self.processes_label = Gtk.Label("D: 0")
        #self.processes_label.set_tooltip_text("Downloading")
        #grid.add(self.processes_label)
        #
        #self.queue_size_label = Gtk.Label("Q: 0")
        #self.queue_size_label.set_tooltip_text("Waiting to download")
        #grid.addmain_window.main_controller.(self.queue_size_label)

        ##halign="start", min_horizontal_bar_width=16
        self.progress_bar = Gtk.ProgressBar()
        # Set minimal size: self.progress_bar.set_size_request(90, -1)
        self.progress_bar.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_valign(Gtk.Align.START)
        self.progress_bar.set_fraction(0.0)
        #self.progress_bar.set_tooltip_text("D (downloading), Q (waiting to download)")
        self.progress_bar.set_tooltip_text("Downloading")
        grid.add(self.progress_bar)

        ##

        #TODO one application-wide css file
        style_context = self.progress_bar.get_style_context()

        css_provider = Gtk.CssProvider()
        package_pathname = os.path.dirname(os.path.realpath(__file__))
        css_filename = os.path.join(package_pathname, "style.css")
        css_provider.load_from_file(Gio.File.new_for_path(css_filename))
        # Higher than the highest (other) priorities (GTK_STYLE_PROVIDER_PRIORITY_USER)
        style_context.add_provider(css_provider, 900)
        
        ##

        # Timeout in milliseconds
        self.timeout_id = GObject.timeout_add(5000, self._on_progress_bar_update, None)
        
        # Initialize label text
        self._on_progress_bar_update(None)

        ####
        
        self.pvr_queue_check_button = Gtk.CheckButton("PVR")
        self.pvr_queue_check_button.set_tooltip_text(TOOLTIP_TOOLS_PVR_QUEUE)
        self.pvr_queue_check_button.set_focus_on_click(False)
        grid.add(self.pvr_queue_check_button)

        ####

        #self.spinner = Gtk.Spinner()
        ##self.spinner_stop()
        #self.pack_start(self.spinner, False, False, 0)
        
        #self.progress_bar = Gtk.ProgressBar()
        #self.progress_bar.set_valign(Gtk.Align.CENTER)
        #self.progress_bar.set_pulse_step(0.01)
        #self.pack_start(self.progress_bar, False, False, 0)

    def _on_progress_bar_update(self, user_data):
        if os.name == "posix":
            processes = command.run("echo -n $(ps xo cmd | grep '^/usr/bin/perl /usr/bin/get_iplayer' | wc -l) ; exit 0", quiet=True)
        else:
            processes = 0

        ##self.processes_label.set_label("D: " + str(processes))
        ##self.queue_size_label.set_label("Q: " + str(command_queue.size()))

        #NOTE string formatting: right-aligned (default for int), 4 characters wide:  str.format("D:{0:4}  Q:{1:4}", ...)
        #self.progress_bar.set_text(str.format("D:{0}  Q:{1}", int(processes), command_queue.size()))
        self.progress_bar.set_text(processes)
        self.progress_bar.set_fraction(int(processes) / 6.0 % 1)
        #Gray-out
        #self.progress_bar.set_sensitive(processes != 0 or command_queue.size() != 0)

        return True

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
        Gtk.TreeView.__init__(self)
        self.main_window = main_window
        self.button_pressed = False
        
        #selection = self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        #self.set_tooltip_column(3)
        #self.get_tooltip_window().set_defaujlt_size(200, -1)
        ##self.set_style(allow_rules=True)
        #self.set_rules_hint(True)
        self.set_grid_lines(Gtk.TreeViewGridLines.VERTICAL)
        self.set_enable_search(False)
        self.connect("button-press-event", self._on_button_press_event)
        self.connect("button-release-event", self._on_button_release_event)
        self.connect("row-activated", self._on_row_activated)

        # First column
        self.set_show_expanders(False)
        self.set_level_indentation(10)
        self.set_enable_tree_lines(False)
        ##self.set_property("grid-line-pattern", "\000\001")
        ##self.set_style(grid_line_pattern="\000\001")

        self._init_columns()

    def init_store(self):
        self.main_window.main_controller.session_restore()
        self.main_window.main_controller.on_button_find_clicked(None)
        
    def _init_columns(self):
        #### First column
        
        renderer = Gtk.CellRendererToggle(indicator_size=11)
        renderer.set_alignment(0, 0.5)
        renderer.connect("toggled", self._on_cell_row_toggled)
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn(None, renderer, active=SearchResultColumn.DOWNLOAD)
        self.append_column(column)

        #### Second column

        renderer = Gtk.CellRendererText(max_width_chars=256)
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn("Serie", renderer, text=SearchResultColumn.SERIE)
        column.set_resizable(True)
        column.set_max_width(250)
        self.append_column(column)
        
        #### Third column

        renderer = Gtk.CellRendererText()
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn("Episode ~ Description", renderer, text=SearchResultColumn.EPISODE)
        column.set_resizable(True)
        self.append_column(column)

        #tooltip = Gtk.Tooltip()
        #self.connect("query-tooltip", self._on_query_tooltip)
        #self.set_tooltip_cell(tooltip, None, column, None)
        
    #def _on_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):      #, user_data):
    #    #tooltip.set_markup(widget.get_label())
    #    tooltip.set_text(widget.get_label())

    def _on_button_press_event(self, widget, event):
        self.button_pressed = True

        if event.type == Gdk.EventType._2BUTTON_PRESS:
            # Double-clicked
            self.main_window.main_controller.on_button_properties_clicked(None)
            #return True
        elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # Right mouse button pressed
            self.main_window.ui_manager.get_popup_menu().popup(None, None, None, None, event.button, event.time)
            #return True
        #return False
    
    def _on_button_release_event(self, widget, event):
        self.button_pressed = False

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
        #            if row[0] != new_toggle_value:
        #                toggle_parent = False
        #                break
        #            iter_previous = model.iter_previous(iter_previous)
        #    if toggle_parent:
        #        print "Toggle parent"
        #        row = model[parent_iter]
        #        row[0] = new_toggle_value

    def set_store(self, tree_rows):
        # Columns in the store: download (True/False), followed by columns listed in get_iplayer.SearchResultColumn
        store = Gtk.TreeStore(bool, str, str, str, str)
        
        #NOTE Could use "for i, row in enumerate(tree_rows):"
        #     except that "i += 1" to skip a list item has no effect
        root_iter = None
        i = 0
        while i in range(len(tree_rows)):
            row = tree_rows[i]
            #if not row[2]:
            if row[SearchResultColumn.EPISODE] is None:
                # Root level row (a serie)
                # If root (a serie) has only one child/leave (an episode) then merge the two into one row
                #TODO try catch: if rows[i+ 1][SearchResultColumn.EPISODE] and not rows[i+ 2][SearchResultColumn.EPISODE]:
                if (i + 1 < len(tree_rows) and tree_rows[i + 1][SearchResultColumn.EPISODE]) and (i + 2 >= len(tree_rows) or not tree_rows[i + 2][SearchResultColumn.EPISODE]):
                    row[SearchResultColumn.PID] = tree_rows[i + 1][SearchResultColumn.PID]
                    row[SearchResultColumn.INDEX] = tree_rows[i + 1][SearchResultColumn.INDEX]
                    row[SearchResultColumn.EPISODE] = tree_rows[i + 1][SearchResultColumn.EPISODE]
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

    WIDTH = 800
    
    def __init__(self, get_iplayer_output_lines):
        Gtk.Window.__init__(self, title="properties - " + get_iplayer_downloader.common.__program_name__)
        self.set_border_width(BORDER_WIDTH)
        self.set_default_size(PropertiesWindow.WIDTH, 700)
        #self.maximize()
        #self.set_resizable(False)

        self._init_grid(get_iplayer_output_lines)

    def _init_grid(self, prop_table):
        ##min_content_height=600, min_content_width=600
        ##visible=True, can_focus=True, hscrollbar_policy=Gtk.Policy.AUTOMATIC, 
        #                               vscrollbar_policy=Gtk.Policy.AUTOMATIC
        scrolled_window = Gtk.ScrolledWindow()
        ##self.set_default_size(400, 400)
        #scrolled_window.set_hexpand(True)
        #scrolled_window.set_vexpand(True)
        self.add(scrolled_window)

        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
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
        #    if prop_table[i][0] == "thumbnail4":
        #        break
        #if i < len(prop_table):
        #    image_url = prop_table[i][1]

        if image_url is not None:
            #TODO g_markup_escape_text() or g_markup_printf_escaped()
            image_url = markup.html2text(image_url)
            image_pathname = settings.TEMP_PATHNAME + os.sep + "images"
            image_filename = file.load_url(image_url, image_pathname)
            image = Gtk.Image.new_from_file(image_filename)
            self.grid.add(image)

        #### Property table
        
        frame = Gtk.Frame(label="Properties", label_xalign=0.02, margin=BORDER_WIDTH,
                          width_request=PropertiesWindow.WIDTH - (8 * BORDER_WIDTH))
        self.grid.add(frame)

        viewport = Gtk.Viewport()
        frame.add(viewport)

        ####
        
        PROP_LABEL_LIST = ["available", "categories", "channel", "desc", "dir", "duration",
                           "episode", "expiryrel", "index", "longname", "modes",
                           "modesizes", "pid", "player", "senum", "timeadded", "title",
                           "type", "versions", "web"]

        prop_grid = Gtk.Grid(column_homogeneous=False, row_homogeneous=False)
        viewport.add(prop_grid)
        
        focused_label = None
        #for prop_row in prop_table:
        #for i, prop_row in enumerate(prop_table):
        for i, (prop_label, prop_value) in enumerate(prop_table):
            if prop_label in PROP_LABEL_LIST:
                label1 = Gtk.Label(prop_label, valign=Gtk.Align.START, halign=Gtk.Align.START)
                label1.set_padding(BORDER_WIDTH, 0)
                label1.set_line_wrap(True)
                #TODO avoid automatic text selection
                label1.set_selectable(True)
                prop_grid.attach(label1, 0, i, 1, 1)

                label2 = Gtk.Label(markup.text2html(string.decode(prop_value)), valign=Gtk.Align.START,
                                   halign=Gtk.Align.START, use_markup=True)
                label2.set_padding(BORDER_WIDTH, 0)
                label2.set_line_wrap(True)
                label2.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                label2.set_selectable(True)
                prop_grid.attach(label2, 1, i, 1, 1)

                #TODO avoid automatic text selection
                if prop_label == "episode" or prop_label == "title":
                    focused_label = label2

        #TODO avoid automatic text selection
        if focused_label:
            focused_label.grab_focus()
        
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
        
        ##ALTERNATIVE however Gtk.Grid has better geometry management
        #prop_table = Gtk.Table(len(prop_list), len(prop_list[0]), False)
        #frame.add(prop_table)
        #
        #i = 0
        #for prop_row in prop_list:
        #    label = Gtk.Label(prop_row[0], valign=Gtk.Align.START, halign=Gtk.Align.START)
        #    label.set_padding(4, 0)
        #    label.set_line_wrap(True)
        #    prop_table.attach(label, 0, 1, i, i+1)
        #
        #    #, use_markup=True
        #    label = Gtk.Label(prop_row[1], valign=Gtk.Align.START, halign=Gtk.Align.START)
        #    label.set_padding(4, 0)
        #    label.set_line_wrap(True)
        #    prop_table.attach(label, 1, 2, i, i+1)
        #    
        #    i += 1

        ####

        frame = Gtk.Frame(label="Additional links", label_xalign=0.02, margin=BORDER_WIDTH,
                          width_request=PropertiesWindow.WIDTH - (8 * BORDER_WIDTH))
        self.grid.add(frame)

        url = "<a href=\"http://www.bbc.co.uk/iplayer\" title=\"BBC iPlayer\">BBC iPlayer</a>"
        url += "      "

        # Add urls to get_iplayer's pvr configuration folder and files
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url += _files2urls(filepath)
        url += "      "

        # Add urls to get_iplayer's presets configuration folder and files
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += _files2urls(filepath)

        label1 = Gtk.Label(url, valign=Gtk.Align.START, halign=Gtk.Align.START, use_markup=True)
        label1.set_padding(BORDER_WIDTH, 0)
        label1.set_line_wrap(True)
        label1.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label1.set_selectable(True)
        frame.add(label1)

#TODO avoid automatic text selection
class PreferencesDialogWrapper(object):

    def __init__(self, main_window):
        self.builder = main_window.builder.builder
        
        self.dialog = self.builder.get_object("PreferencesDialog")

        self.general_compact_toolbar_entry = self.builder.get_object("PrefsGeneralCompactToolbar")
        self.general_start_maximized_entry = self.builder.get_object("PrefsGeneralStartMaximized")

        self.radio_channels_entry = self.builder.get_object("PrefsRadioChannelsEntry")
        self.radio_download_path_entry = self.builder.get_object("PrefsRadioDownloadPathEntry")
        self.radio_download_file_chooser_button = self.builder.get_object("PrefsRadioDownloadFileChooserButton")
        self.radio_run_in_terminal_entry = self.builder.get_object("PrefsRadioRunInTerminalCheckButton")

        self.tv_channels_entry = self.builder.get_object("PrefsTvChannelsEntry")
        self.tv_download_path_entry = self.builder.get_object("PrefsTvDownloadPathEntry")
        self.tv_download_file_chooser_button = self.builder.get_object("PrefsTvDownloadFileChooserButton")
        self.tv_run_in_terminal_entry = self.builder.get_object("PrefsTvRunInTerminalCheckButton")

        ####
        
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url = _files2urls(filepath)
        url += "      "
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += _files2urls(filepath)
        
        label = self.builder.get_object("PrefsAdvGetIPlayerConfLabel")
        label.set_markup(url)

        ####
        
        self.dialog.set_title("preferences - " + get_iplayer_downloader.common.__program_name__)
        self._display_settings()

        self.builder.connect_signals(self)
        self.dialog.connect("response", self._response)

        #self.ok_button = self.builder.get_object("PrefsOkButton")
        #self.dialog.connect("show", self._on_show)

    def _display_settings(self):
        """ Retrieve in-memory settings and put them in dialog fields """
        self.general_compact_toolbar_entry.set_active(string.str2bool(settings.config().get(config.NOSECTION, "compact-toolbar")))
        self.general_start_maximized_entry.set_active(string.str2bool(settings.config().get(config.NOSECTION, "start-maximized")))

        self.radio_channels_entry.set_text(settings.config().get("radio", "channels"))
        self.radio_download_path_entry.set_text(settings.config().get("radio", "download-path"))
        self.radio_download_file_chooser_button.set_filename(settings.config().get("radio", "download-path"))
        self.radio_run_in_terminal_entry.set_active(string.str2bool(settings.config().get("radio", "run-in-terminal")))
        
        self.tv_channels_entry.set_text(settings.config().get("tv", "channels"))
        self.tv_download_path_entry.set_text(settings.config().get("tv", "download-path"))
        self.tv_download_file_chooser_button.set_filename(settings.config().get("tv", "download-path"))
        self.tv_run_in_terminal_entry.set_active(string.str2bool(settings.config().get("tv", "run-in-terminal")))

    def _capture_settings(self):
        """ Retrieve settings from dialog fields and put them in in-memory settings """
        settings.config().set(config.NOSECTION, "compact-toolbar", str(self.general_compact_toolbar_entry.get_active()))
        settings.config().set(config.NOSECTION, "start-maximized", str(self.general_start_maximized_entry.get_active()))
        
        settings.config().set("radio", "channels", self.radio_channels_entry.get_text())
        settings.config().set("radio", "download-path", self.radio_download_path_entry.get_text())
        settings.config().set("radio", "run-in-terminal", str(self.radio_run_in_terminal_entry.get_active()))
        
        settings.config().set("tv", "channels", self.tv_channels_entry.get_text())
        settings.config().set("tv", "download-path", self.tv_download_path_entry.get_text())
        settings.config().set("tv", "run-in-terminal", str(self.tv_run_in_terminal_entry.get_active()))

    #def _on_show(self, user_data):
    #    self.ok_button.grab_focus()

    def _on_prefs_revert_clicked(self, user_data):
        """ Only reset settings visible on the preferences dialog window """

        # Factory-reset all options
        #settings.revert()

        settings.revert_option(config.NOSECTION, "compact-toolbar")
        settings.revert_option(config.NOSECTION, "start-maximized")

        settings.revert_option("radio", "channels")
        settings.revert_option("radio", "download-path")
        settings.revert_option("radio", "run-in-terminal")
        
        settings.revert_option("tv", "channels")
        settings.revert_option("tv", "download-path")
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
        entry_widget.set_text(filename)
        
    def _on_tv_download_file_chooser_file_set(self, entry_widget):
        filename = self.tv_download_file_chooser_button.get_filename()
        #entry_widget.set_text(GLib.filename_to_utf8(filename, -1, None, 25, None))
        entry_widget.set_text(filename)

    def _response(self, dialog, response_id):
        if response_id != Gtk.ResponseType.NONE:    # -1
            self.dialog.hide()

    def run(self):
        self.dialog.run()

class SearchEntry(Gtk.Entry):

    def __init__(self):
        Gtk.Entry.__init__(self)
        
        self.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_CLEAR)
        self.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Clear filter")
        self.set_placeholder_text("filter programmes")
        self.connect("icon-press", self._on_icon_press)
        
    def _on_icon_press(self, entry, icon_pos, event):
        if (icon_pos == Gtk.EntryIconPosition.SECONDARY):
            entry.set_text("")
            #entry.set_placeholder_text("filter programmes")

class MainWindowController:
    """ Handle the active part of the main window related widgets. Activity between main widgets and 
        activity towards the model (get_iplayer.py)
    """
    
    def __init__(self, main_window):
        self.main_window = main_window

    # Convenience method
    def init(self):
        """ Complete initialization, after the main window has completed its initialization """
        self.tool_bar_box = self.main_window.tool_bar_box
        self.main_tree_view = self.main_window.main_tree_view

    def on_button_find_clicked(self, button):
        # button can be None
        search_text = self.tool_bar_box.search_entry.get_text()

        preset = None
        prog_type = None
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]
            prog_type = model[tree_iter][1]
            channel = model[tree_iter][2]

        category = None
        combo = self.tool_bar_box.category_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            #WORKAROUND see also get_iplayer.py
            #    On some systems, when model[tree_iter][0] == None, the following exception is raised:
            #    AttributeError: 'NoneType' object has no attribute 'decode'
            #    In the debugger, model[tree_iter][0] is displayed as a unicode string.
            category = model[tree_iter][0]

        since = 0
        combo = self.tool_bar_box.since_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            since = model[tree_iter][0]

        search_all = self.tool_bar_box.search_all_check_button.get_active()

        get_iplayer_output_lines = get_iplayer.search(search_text, preset=preset, prog_type=prog_type,
                                                      channel=channel, category=category, since=since,
                                                      search_all=search_all)
        self.main_tree_view.set_store(get_iplayer_output_lines)
        # Scroll up
        adjustment = self.main_window.main_tree_view_scrollbar.get_vadjustment()
        adjustment.set_value(0.0)
        adjustment.value_changed()
        #adjustment = self.main_window.main_tree_view_scrollbar.set_vadjustment(adjustment)

        self.main_window.set_window_title(prog_type=prog_type)

    def on_button_download_clicked(self, button, pvr_queue=False):
        # button can be None
        hd_tv_mode = False
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]
            if preset == get_iplayer.Preset.TV:
                hd_tv_mode = self.tool_bar_box.hd_tv_check_button.get_active()

        force_download = self.tool_bar_box.force_download_check_button.get_active()
        if button is not None and not pvr_queue:
            # If event was raised from the tool bar download button and not from a shortcut key,
            # then the PVR check button determines the download/queue mode
            pvr_queue = self.tool_bar_box.pvr_queue_check_button.get_active()
        
        # Search selected leaf nodes (the second level) two levels deep
        model = self.main_tree_view.get_model()
        #indices = ""
        pid_list = []
        root_iter = model.get_iter_first()
        while root_iter is not None:
            row = model[root_iter]
            if row[0] and row[1]:
                #indices += row[1] + " "
                pid_list.append(row[1])
            
            #if model.iter_has_child(root_iter):
            child_iter = model.iter_children(root_iter)
            while child_iter is not None:
                row = model[child_iter]
                if row[0]:
                    #indices += row[1] + " "
                    pid_list.append(row[1])
                child_iter = model.iter_next(child_iter)
            root_iter = model.iter_next(root_iter)
        
        #if indices:
        if len(pid_list) > 0:
            launched, process_output = get_iplayer.get(pid_list, pid=True, pvr_queue=pvr_queue, preset=preset, 
                                                       hd_tv_mode=hd_tv_mode, force_download=force_download)
            if not launched:
                dialog = Gtk.MessageDialog(self.main_window, 0,
                                           Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                           "get_iplayer not launched")
                #dialog.format_secondary_text("")
                dialog.run()
                dialog.destroy()
            elif pvr_queue:
                dialog = ExtendedMessageDialog(self.main_window, 0,
                                               Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                               "Queued programmes")
                dialog.set_default_response(Gtk.ResponseType.CLOSE)
                #dialog.format_secondary_text("")
                dialog.get_content_area().set_size_request(600, 500)
                dialog.format_tertiary_scrolled_text(string.decode(process_output))
                label = dialog.get_scrolled_label()
                label.set_valign(Gtk.Align.START)
                label.set_halign(Gtk.Align.START)
                label.set_selectable(True)
                dialog.run()
                dialog.destroy()
            #else:
            #    self.main_window.main_tree_view.grab_focus()
        else:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "No programmes selected")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()

    def on_button_pvr_queue_clicked(self):
        self.on_button_download_clicked(None, pvr_queue=True)

    def on_button_properties_clicked(self, button):
        # button can be None
        preset = None
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]

        proxy_enabled = self.tool_bar_box.proxy_check_button.get_active()
        
        model, tree_iter = self.main_tree_view.get_selection().get_selected()
        if tree_iter is not None:
            index = model[tree_iter][SearchResultColumn.INDEX]
            if index:
                get_iplayer_output_lines = get_iplayer.info(index, preset=preset, proxy_enabled=proxy_enabled)
                window = PropertiesWindow(get_iplayer_output_lines)
                window.show_all()
            #else:
            #    assert(False)
        else:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "No programme highlighted (no programme in focus)")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
            
    def on_accel_go_to_find(self):
        self.tool_bar_box.search_entry.grab_focus()

    def on_accel_rotate_programme_type(self):
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            active = combo.get_active()
            combo.set_active(active + 1)
            active = combo.get_active()
            if active == -1:
                combo.set_active(0)
            #NOTE combo.set_active() already causes the invocation of on_combo_preset_changed()
            #self.tool_bar_box.on_combo_preset_changed(combo)

    def on_button_clear_clicked(self, button):
        # button can be None
        model = self.main_tree_view.get_model()
        
        # Search selected nodes one level deep
        for row in model:
            if row[0]:
                row[0] = False

        # Search two levels deep
        root_iter = model.get_iter_first()
        while root_iter is not None:
            #if model.iter_has_child(root_iter):
            child_iter = model.iter_children(root_iter)
            while child_iter is not None:
                row = model[child_iter]
                if row[0]:
                    row[0] = False
                child_iter = model.iter_next(child_iter)
            root_iter = model.iter_next(root_iter)

        self.main_tree_view.get_selection().unselect_all()

    def on_button_refresh_clicked(self, button):
        # button can be None
        
        # Refresh programme cache
        #preset = None
        #combo = self.tool_bar_box.preset_combo
        #tree_iter = combo.get_active_iter()
        #if tree_iter is not None:
        #    model = combo.get_model()
        #    preset = model[tree_iter][0]
        get_iplayer.refresh(preset=None)
        
        # Refresh programme list
        self.on_button_find_clicked(None)

    def on_combo_preset_changed(self, combo):
        """ Synchronize associated model settings. """
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]
            prog_type = model[tree_iter][1]
            
            if preset == get_iplayer.Preset.RADIO:
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_radio_store)
                self.tool_bar_box.category_combo.set_active(0)
            elif preset == get_iplayer.Preset.TV:
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_tv_store)
                self.tool_bar_box.category_combo.set_active(0)

            # Limit the initial podcast search result by enabling the since filter
            combo = self.tool_bar_box.since_combo
            if prog_type == get_iplayer.ProgType.PODCAST:
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    model = combo.get_model()
                    since = model[tree_iter][0]
                    if since == 0:
                        # Set to longest by not unlimited since filter
                        combo.set_active(len(get_iplayer.SINCE_LIST) - 1)
            elif combo.get_active() == len(get_iplayer.SINCE_LIST) - 1:
                # Disable since filter
                combo.set_active(0)

    def on_set_programme_type(self, prog_type):
        # Lookup prog_type
        combo = self.tool_bar_box.preset_combo
        model = combo.get_model()
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

    ####
    
    def session_save(self):
        restore_session = string.str2bool(settings.config().get(config.NOSECTION, "restore-session"))
        if restore_session:
            #preset = None
            prog_type = None
            combo = self.tool_bar_box.preset_combo
            tree_iter = combo.get_active_iter()
            if tree_iter is not None:
                model = combo.get_model()
                #preset = model[tree_iter][0]
                prog_type = model[tree_iter][1]
                #channel = model[tree_iter][2]
            if prog_type:
                # Programme type is not an empty string
                settings.config().set("session", "programme-type", prog_type)
                settings.save()
    
    def session_restore(self):
        restore_session = string.str2bool(settings.config().get(config.NOSECTION, "restore-session"))
        if restore_session:
            prog_type = settings.config().get("session", "programme-type")
            if not prog_type:
                # Programme type is an empty string (or None)
                prog_type = get_iplayer.ProgType.RADIO
            self.on_set_programme_type(prog_type)
    
def _files2urls(filepath):
    """ Return a string containing a url to the folder @filepath and the files inside @filepath (one level deep), sorted by file name """
    basename = os.path.basename(filepath)
    url = "<a href=\"file://" + filepath + "\" title=\"get_iplayer " + basename + " configuration folder\">" + basename + "</a>"
    for root, dirs, files in os.walk(filepath):
        # Skip empty and subfolders
        if len(files) > 0 and filepath == root:
            files.sort()
            url += " ("
            for i, filename in enumerate(files):
                # Skip files created by get_iplayer --pvrqueue
                if not filename.startswith("ONCE_"):
                    url += "<a href=\"file://" + os.path.join(filepath, filename) + "\" title=\"get_iplayer " + basename + " configuration file\">" + filename + "</a>"
                    if (i < len(files) - 1):
                        url += ", "
            url += ")"
    return url
    #ALTERNATIVE ways of sorting a list of files in a folder: glob(<filename filter>); listdir()

#NOTE session_save() is done from outside the window class and session_restore() is done from inside the window class,
def _main_quit(main_window, event):
    main_window.main_controller.session_save()
    Gtk.main_quit(main_window, event)

def main():
    window = MainWindow()
    window.connect("delete-event", _main_quit)
    window.show_all()

    # Force images on buttons
    settings = Gtk.Settings.get_default()
    settings.props.gtk_button_images = True

    # Enable threads
    GObject.threads_init()

    # Allow ctrl+c to quit the program
    signal.signal(signal.SIGINT, lambda signal, frame: Gtk.main_quit())

    Gtk.main()

if __name__ == "__main__":
    main()
