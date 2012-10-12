from gi.repository import Gdk, GObject, Gtk

# Load application-wide definitions
import get_iplayer_downloader

#NOTE Import module, not symbol names inside a module, to avoid circular import
import get_iplayer_downloader.ui.main_window

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
      <menuitem action="ViewPlayer"/>
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
    <menuitem action="ViewPlayer"/>
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
            ("ViewPlayer", Gtk.STOCK_MEDIA_PLAY, "Play", "<control>P", get_iplayer_downloader.ui.main_window.TOOLTIP_VIEW_PLAYER, self._on_menu_others),
            ("ViewProperties", Gtk.STOCK_PROPERTIES, "_Properties", "<alt>Return", get_iplayer_downloader.ui.main_window.TOOLTIP_VIEW_PROPERTIES, self._on_menu_others),
            ("ViewLog", Gtk.STOCK_CAPS_LOCK_WARNING, "_Log", "<control>L", get_iplayer_downloader.ui.main_window.TOOLTIP_VIEW_LOG, self._on_menu_others)
        ])

    def _add_search_menu_actions(self, action_group):
        action_group.add_actions([
            ("SearchMenu", None, "Search"),
            ("SearchGoToFind", Gtk.STOCK_FIND, "_Find", "<control>F", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_GO_TO_FIND, self._on_menu_others),
            ("SearchRotateProgrammeType", None, None, "<control>T", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_PROG_TYPE, self._on_menu_others),
            ("SearchRotateForwardSince", None, None, "<control>S", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),
            ("SearchRotateBackwardSince", None, None, "<control><shift>S", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),

            # Alternative key bindings
            ("SearchRotateProgrammeType_1", None, None, "<control>1", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_PROG_TYPE, self._on_menu_others),
            ("SearchRotateCategory_2", None, None, "<control>2", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_CATEGORY, self._on_menu_others),
            ("SearchRotateChannel_3", None, None, "<control>3", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_CHANNEL, self._on_menu_others),
            ("SearchRotateForwardSince_4", None, None, "<control>4", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),
            #("SearchRotateBackwardSince_SHIFT_4", None, None, "<control><shift>4", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others),
            ("SearchRotateBackwardSince_5", None, None, "<control>5", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_SINCE, self._on_menu_others)
        ])

    def _add_tools_menu_actions(self, action_group):
        action_group.add_actions([
            ("ToolsMenu", None, "Programme"),
            #Gtk.STOCK_GO_DOWN
            ("ToolsDownload", Gtk.STOCK_GOTO_BOTTOM, "_Download", "<control>D", get_iplayer_downloader.ui.main_window.TOOLTIP_TOOLS_DOWNLOAD, self._on_menu_others),
            ("ToolsPvrQueue", Gtk.STOCK_DND_MULTIPLE, "_Queue", "<control>Q", "Queue mode. " + get_iplayer_downloader.ui.main_window.TOOLTIP_OPTION_PVR_QUEUE, self._on_menu_others),
            ("ToolsClear", Gtk.STOCK_CLEAR, "_Clear", "<control>C", get_iplayer_downloader.ui.main_window.TOOLTIP_TOOLS_CLEAR, self._on_menu_others),
            ("ToolsRefresh", Gtk.STOCK_REFRESH, "_Refresh", "<control>R", get_iplayer_downloader.ui.main_window.TOOLTIP_TOOLS_REFRESH, self._on_menu_others)
        ])

    def _add_help_menu_actions(self, action_group):
        action_group.add_actions([
            ("HelpMenu", None, "Help"),
            ("HelpHelp", Gtk.STOCK_HELP, "_Help", "F1", get_iplayer_downloader.ui.main_window.TOOLTIP_HELP_HELP, self._on_menu_others),
            ("HelpAbout", Gtk.STOCK_ABOUT, "_About", None, get_iplayer_downloader.ui.main_window.TOOLTIP_HELP_ABOUT, self._on_menu_others)
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
            self.main_window.controller().on_preferences()
        elif name == "ViewPlayer":
            self.main_window.controller().on_button_play_clicked(None)
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
            self.main_window.controller().on_help()
        elif name == "HelpAbout":
            self.main_window.controller().on_about()
