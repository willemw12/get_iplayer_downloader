#!/usr/bin/env python

import os
from gi.repository import Gdk, Gtk, GObject, Pango, Gio

# Application-wide constants
import get_iplayer_downloader.common

from get_iplayer_downloader import get_iplayer, settings
from get_iplayer_downloader.tools import command, command_queue, config, file, markup, string

BORDER_WIDTH = 4

class MainWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_window_title()
        self.set_size_request(960, 720)
        self.set_border_width(BORDER_WIDTH)
        if string.str2bool(settings.config().get(config.NOSECTION, "start-maximized")):
            self.maximize()
        
        ####
        
        self._init_ui_manager()
        self._init_builder()

        ####
        
        self._init_main_grid()
        #self._init_menu_bar()
        self._init_tool_bar_box()
        self._init_main_treeview()

    def _init_ui_manager(self):
        #TODO move outside Window class
        self.ui_manager = UIManager(self)

    def _init_builder(self):
        #TODO move outside Window class
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
        
    def _init_main_treeview(self):
        self.main_treeview_scrollbar = Gtk.ScrolledWindow()
        self.main_treeview_scrollbar.set_hexpand(True)
        self.main_treeview_scrollbar.set_vexpand(True)
        self.main_grid.attach_next_to(self.main_treeview_scrollbar, self.tool_bar_box, Gtk.PositionType.BOTTOM, 1, 2)

        self.main_treeview = MainTreeView(self)
        self.main_treeview_scrollbar.add(self.main_treeview)
        
    def set_window_title(self, prog_type=get_iplayer.Type.RADIO):
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
      <separator />
      -->
      <menuitem action="FileQuit"/>
    </menu>
    <menu action="EditMenu">
      <menuitem action="EditPreferences"/>
    </menu>
    <menu action="ViewMenu">
      <menuitem action="ViewProperties"/>
    </menu>
    <menu action="ToolsMenu">
      <menuitem action="ToolsDownload"/>
      <menuitem action="ToolsClear"/>
      <menuitem action="ToolsRefresh"/>
    </menu>
    <menu action="HelpMenu">
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
    <menuitem action="ToolsClear"/>
    <menuitem action="ToolsRefresh"/>
    <separator/>
    <menuitem action="EditPreferences"/>
    <menuitem action="HelpAbout"/>
  </popup>
</ui>
"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.ui_manager = self._create_ui_manager()

        ####
        
        action_group = Gtk.ActionGroup("action_group")

        self._add_file_menu_actions(action_group)
        self._add_edit_menu_actions(action_group)
        self._add_view_menu_actions(action_group)
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
            ("EditPreferences", Gtk.STOCK_PREFERENCES, "Preferences", "<control><alt>P", None, self._on_menu_others)
        ])

    def _add_view_menu_actions(self, action_group):
        action_group.add_actions([
            ("ViewMenu", None, "View"),
            ("ViewProperties", Gtk.STOCK_PROPERTIES, "_Properties", None, "View details of selected program", self._on_menu_others)
        ])

    def _add_tools_menu_actions(self, action_group):
        action_group.add_actions([
            ("ToolsMenu", None, "Do"),
            ("ToolsDownload", Gtk.STOCK_GO_DOWN, "Download", None, "Download selected programs", self._on_menu_others),
            ("ToolsClear", Gtk.STOCK_CLEAR, "Clear", None, "Clear program download selection", self._on_menu_others),
            ("ToolsRefresh", Gtk.STOCK_REFRESH, "Refresh", None, "Refresh program cache", self._on_menu_others)
        ])

    def _add_help_menu_actions(self, action_group):
        action_group.add_actions([
            ("HelpMenu", None, "Help"),
            ("HelpAbout", Gtk.STOCK_ABOUT, "_About", None, "About this application", self._on_menu_others)
        ])

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
        #print "Menu item " + widget.get_name() + " was selected"
        
        name = widget.get_name()
        if name == "EditPreferences":
            self.main_window.tool_bar_box._on_button_preferences_clicked()
        elif name == "ViewProperties":
            self.main_window.tool_bar_box._on_button_properties_clicked(None)
        elif name == "ToolsDownload":
            self.main_window.tool_bar_box._on_button_download_clicked(None)
        elif name == "ToolsClear":
            self.main_window.tool_bar_box._on_button_clear_clicked(None)
        elif name == "ToolsRefresh":
            self.main_window.tool_bar_box._on_button_refresh_clicked(None)
        elif name == "HelpAbout":
            self.main_window.tool_bar_box._on_button_about_clicked()

#NOTE Glade 
# Glade generates the following deprecated property for Grid: 
#     <property name="n_rows">1</property>
# It causes a Gtk warning. This property can be removed from the generated .ui file.
#
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
        
        #(TODO as GUI preference setting)
        show_label = False

        def _label(label):
            #NOTE conditional expression (inline if-then-else)
            return label if show_label else None
        
        ####
        
        #ALTERNATIVE define inline callback methods here (_on_button_download_clicked, etc.)
        
        button = Gtk.Button(label="_Download", use_underline=True, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_DOWN))
        button.set_tooltip_text("Download selected programs")
        button.connect("clicked", self._on_button_download_clicked)
        self.pack_start(button, False, False, 0)

        button = Gtk.Button(stock=Gtk.STOCK_PROPERTIES, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text("View details of highlighted program (in focus)")
        button.connect("clicked", self._on_button_properties_clicked)
        self.pack_start(button, False, False, 0)

        button = Gtk.Button(stock=Gtk.STOCK_CLEAR, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text("Clear program download selection")
        button.set_focus_on_click(False)
        button.connect("clicked", self._on_button_clear_clicked)
        self.pack_start(button, False, False, 0)

        button = Gtk.Button(stock=Gtk.STOCK_REFRESH, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text("Refresh program cache")
        button.set_focus_on_click(False)
        button.connect("clicked", self._on_button_refresh_clicked)
        self.pack_start(button, False, False, 0)
        #button.grab_focus()
        
        ####
        
        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        #button = Gtk.Button(label="_Update", use_underline=True, relief=Gtk.ReliefStyle.NONE,
        #                    image_position=Gtk.PositionType.TOP)
        #button.set_image(Gtk.Image(stock=Gtk.STOCK_GO_UP))
        #button.set_tooltip_text("Update programs list")
        button = Gtk.Button(stock=Gtk.STOCK_FIND, relief=Gtk.ReliefStyle.NONE,
                            image_position=Gtk.PositionType.TOP)
        button.set_tooltip_text("Find programs")
        button.connect("clicked", self._on_button_find_clicked)
        self.pack_start(button, False, False, 0)

        self.search_entry = SearchEntry()
        self.search_entry.set_tooltip_text("Filter program name and description")
        self.search_entry.connect("activate", self._on_button_find_clicked)
        self.pack_start(self.search_entry, False, False, 0)
        self.search_entry.grab_focus()

        ####

        label = Gtk.Label(_label(" Type:"))
        self.pack_start(label, False, False, 0)
        
        presets = [[get_iplayer.Preset.RADIO, get_iplayer.Type.RADIO,
                    get_iplayer.Channel.RADIO, "Radio"],
                   [get_iplayer.Preset.RADIO, get_iplayer.Type.PODCAST,
                    None, "Podcasts"],
                   [get_iplayer.Preset.TV, get_iplayer.Type.TV,
                    get_iplayer.Channel.TV, "TV"]]
        store = Gtk.ListStore(str, str, str, str)
        for preset in presets:
            store.append(preset)
        self.preset_combo = Gtk.ComboBox.new_with_model(store)
        self.preset_combo.set_valign(Gtk.Align.CENTER)
        self.preset_combo.set_tooltip_text("Program type")
        self.preset_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.preset_combo.pack_start(renderer_text, True)
        self.preset_combo.add_attribute(renderer_text, "text", 3)
        self.preset_combo.set_active(0)
        self.preset_combo.connect("changed", self._on_combo_preset_changed)
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

        self.category_combo = Gtk.ComboBox.new_with_model(self.cat_radio_store)
        self.category_combo.set_valign(Gtk.Align.CENTER)
        self.category_combo.set_tooltip_text("Program category")
        self.category_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.category_combo.pack_start(renderer_text, True)
        self.category_combo.add_attribute(renderer_text, "text", 1)
        self.category_combo.set_active(0)
        self.pack_start(self.category_combo, False, False, 0)

        ####

        label = Gtk.Label(_label(" Since:"))
        self.pack_start(label, False, False, 0)

        store = Gtk.ListStore(int, str)
        for since in get_iplayer.SINCE_LIST:
            store.append(since)
        self.since_combo = Gtk.ComboBox.new_with_model(store)
        self.since_combo.set_valign(Gtk.Align.CENTER)
        self.since_combo.set_tooltip_text("Limit search to recently available programs")
        self.since_combo.set_focus_on_click(False)
        renderer_text = Gtk.CellRendererText()
        self.since_combo.pack_start(renderer_text, True)
        self.since_combo.add_attribute(renderer_text, "text", 1)
        self.since_combo.set_active(0)
        self.pack_start(self.since_combo, False, False, 0)

        ####

        separator = Gtk.VSeparator()
        self.pack_start(separator, False, False, 0)

        grid = Gtk.Grid()
        self.pack_start(grid, False, False, 0)

        self.force_download_checkbutton = Gtk.CheckButton("Force", relief=Gtk.ReliefStyle.NONE)
        self.force_download_checkbutton.set_tooltip_text("Force download")
        self.force_download_checkbutton.set_focus_on_click(False)
        #grid.pack_start(self.force_download_checkbutton, False, False, 0)
        grid.add(self.force_download_checkbutton)
        
        self.hd_tv_checkbutton = Gtk.CheckButton("HD", relief=Gtk.ReliefStyle.NONE)
        self.hd_tv_checkbutton.set_tooltip_text("HD TV recording mode. Overrides the default TV mode.")
        self.hd_tv_checkbutton.set_focus_on_click(False)
        #grid.pack_start(self.force_download_checkbutton, False, False, 0)
        grid.attach_next_to(self.hd_tv_checkbutton, self.force_download_checkbutton, Gtk.PositionType.RIGHT, 1, 1)
        
        self.proxy_checkbutton = Gtk.CheckButton("Proxy", relief=Gtk.ReliefStyle.NONE)
        self.proxy_checkbutton.set_tooltip_text("Force full proxy mode. Only applies to the retrieval of program properties. Useful outside the UK. When enabled, properties will include the available tv download sizes.")
        self.proxy_checkbutton.set_focus_on_click(False)
        #grid.pack_start(self.proxy_checkbutton, False, False, 0)
        grid.attach_next_to(self.proxy_checkbutton, self.force_download_checkbutton, Gtk.PositionType.BOTTOM, 1, 1)
        
        self.search_all_checkbutton = Gtk.CheckButton("All", relief=Gtk.ReliefStyle.NONE)
        self.search_all_checkbutton.set_tooltip_text("Search in all program types and channels. All radio and podcast channels or all tv channels.")
        self.search_all_checkbutton.set_focus_on_click(False)
        #grid.pack_start(self.search_all_checkbutton, False, False, 0)
        grid.attach_next_to(self.search_all_checkbutton, self.proxy_checkbutton, Gtk.PositionType.RIGHT, 1, 1)

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
        #grid.add(self.queue_size_label)

        ##halign="start", min_horizontal_bar_width=16
        self.progress_bar = Gtk.ProgressBar()
        #self.progress_bar.set_size_request(90, -1)
        self.progress_bar.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_valign(Gtk.Align.START)
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_tooltip_text("D (downloading), Q (waiting to download)")
        self.pack_start(self.progress_bar, False, False, 0)

        ####

        #TODO one application-wide css file
        style_context = self.progress_bar.get_style_context()

        css_provider = Gtk.CssProvider()
        package_pathname = os.path.dirname(os.path.realpath(__file__))
        css_filename = os.path.join(package_pathname, "style.css")
        css_provider.load_from_file(Gio.File.new_for_path(css_filename))
        # Higher than the highest (other) priorities (GTK_STYLE_PROVIDER_PRIORITY_USER)
        style_context.add_provider(css_provider, 900)
        
        ####

        # Timeout in milliseconds
        self.timeout_id = GObject.timeout_add(5000, self.do_status_update, None)
        
        # Initialize label text
        self.do_status_update(None)

        ####

        #self.spinner = Gtk.Spinner()
        ##self.spinner_stop()
        #self.pack_start(self.spinner, False, False, 0)
        
        #self.progress_bar = Gtk.ProgressBar()
        #self.progress_bar.set_valign(Gtk.Align.CENTER)
        #self.progress_bar.set_pulse_step(0.01)
        #self.pack_start(self.progress_bar, False, False, 0)

    def do_status_update(self, user_data):
        #NOTE Linux specific
        processes = int(command.run("echo -n $(ps xo cmd | grep '^/usr/bin/perl /usr/bin/get_iplayer' | wc -l) ; exit 0", quiet=True))

        ##self.processes_label.set_label("D: " + str(processes))
        ##self.queue_size_label.set_label("Q: " + str(command_queue.size()))

        #NOTE string formatting: right-aligned (default for int), 4 characters wide:  str.format("D:{0:4}  Q:{1:4}", ...)
        self.progress_bar.set_text(str.format("D:{0}  Q:{1}", int(processes), command_queue.size()))
        self.progress_bar.set_fraction(processes / 6.0 % 1)
        #Gray-out
        #self.progress_bar.set_sensitive(processes != 0 or command_queue.size() != 0)

        return True

    def _on_button_find_clicked(self, button):
        #NOTE button can be None (this call is reused by other widgets on this panel)
        search_text = self.search_entry.get_text()

        preset = None
        prog_type = None
        combo = self.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]
            prog_type = model[tree_iter][1]
            channel = model[tree_iter][2]

        category = None
        combo = self.category_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            category = model[tree_iter][0]

        since = 0
        combo = self.since_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            since = model[tree_iter][0]

        search_all = self.search_all_checkbutton.get_active()

        get_iplayer_output_lines = get_iplayer.search(search_text, preset=preset, prog_type=prog_type,
                                                      channel=channel, category=category, since=since,
                                                      search_all=search_all)
        self.main_window.main_treeview.set_store(get_iplayer_output_lines)
        # Scroll up
        adjustment = self.main_window.main_treeview_scrollbar.get_vadjustment()
        adjustment.set_value(0.0)
        adjustment.value_changed()
        #adjustment = self.main_window.main_treeview_scrollbar.set_vadjustment(adjustment)

        self.main_window.set_window_title(prog_type=prog_type)
        
    def _on_button_download_clicked(self, button):
        #NOTE button can be None (this call is reused by other widgets on this panel)
        hd_tv_mode = False
        combo = self.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]
            if preset == get_iplayer.Preset.TV:
                hd_tv_mode = self.hd_tv_checkbutton.get_active()

        force_download = self.force_download_checkbutton.get_active()
        
        # Search selected leaf nodes (the second level) two levels deep
        model = self.main_window.main_treeview.get_model()
        indices = ""
        root_iter = model.get_iter_first()
        while root_iter is not None:
            row = model[root_iter]
            if row[0] and row[1]:
                indices += row[1] + " "
            
            #if model.iter_has_child(root_iter):
            child_iter = model.iter_children(root_iter)
            while child_iter is not None:
                row = model[child_iter]
                if row[0]:
                    indices += row[1] + " "
                child_iter = model.iter_next(child_iter)
            root_iter = model.iter_next(root_iter)
        
        if indices:
            launched = get_iplayer.get(indices, preset=preset, hd_tv_mode=hd_tv_mode, force_download=force_download)
            if not launched:
                dialog = Gtk.MessageDialog(self.main_window, 0,
                                           Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                           "get_iplayer not launched")
                dialog.format_secondary_text("Too many get_iplayers are running. Please try again later.")
                dialog.run()
                dialog.destroy()
        else:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                       "No programs selected")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()

    def _on_button_preferences_clicked(self):       #, button):
        #NOTE not called from this widget
        try:
            getattr(self.main_window, "preferences_dialog")
        except AttributeError:
            self.main_window.preferences_dialog = PreferencesDialogWrapper(self.main_window)
        self.main_window.preferences_dialog.run()
        #dialog.hide()

    def _on_button_properties_clicked(self, button):
        #NOTE button can be None (this call is reused by other widgets)
        preset = None
        combo = self.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]

        proxy_enabled = self.proxy_checkbutton.get_active()
        
        model, tree_iter = self.main_window.main_treeview.get_selection().get_selected()
        if tree_iter is not None:
            index = model[tree_iter][1]
            if index:
                get_iplayer_output_lines = get_iplayer.info(preset, index, proxy_enabled)
                window = DetailWindow(get_iplayer_output_lines)
                window.show_all()
            #else:
            #    assert(False)
        else:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                                       "No program highlighted (in focus)")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
            
    def _on_button_clear_clicked(self, button):
        #NOTE button can be None (this call is reused by other widgets)
        model = self.main_window.main_treeview.get_model()
        
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

        self.main_window.main_treeview.get_selection().unselect_all()

    def _on_button_refresh_clicked(self, button):
        #NOTE button can be None (this call is reused by other widgets)
        
        # Refresh program cache
        #preset = None
        #combo = self.preset_combo
        #tree_iter = combo.get_active_iter()
        #if tree_iter is not None:
        #    model = combo.get_model()
        #    preset = model[tree_iter][0]
        get_iplayer.refresh(preset=None)
        
        # Refresh program list
        self._on_button_find_clicked(None)

    def _on_button_about_clicked(self):       #, button):
        #NOTE not called from this widget
#        dialog = self.main_window.builder.get_object("AboutDialog")
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

    ##### Spinner
    #
    #def spinner_start(self):
    #    #self.spinner.set_visible(True)
    #    self.spinner.start()
    # 
    #def spinner_stop(self):
    #    self.spinner.stop()
    #    #self.spinner.set_visible(False)
    
    ##### Progressbar
    #
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

    def _on_combo_preset_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            preset = model[tree_iter][0]
            
            if preset == get_iplayer.Preset.RADIO:
                self.category_combo.set_model(self.cat_radio_store)
                self.category_combo.set_active(0)
            elif preset == get_iplayer.Preset.TV:
                self.category_combo.set_model(self.cat_tv_store)
                self.category_combo.set_active(0)

class MainTreeView(Gtk.TreeView):

    def __init__(self, main_window):
        Gtk.TreeView.__init__(self)
        self.main_window = main_window
        
        #self.set_enable_search(True)
        #selection = self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        #self.set_rules_hint(True)
        ##self.set_style(allow_rules=True)
        self.set_grid_lines(Gtk.TreeViewGridLines.VERTICAL)
        #self.set_tooltip_column(3)
        #self.get_tooltip_window().set_defaujlt_size(200, -1)
        self.connect("button-press-event", self._on_button_press_event)
        self.connect("row-activated", self._on_row_activated)

        # First column
        self.set_show_expanders(False)
        self.set_level_indentation(12)
        self.set_enable_tree_lines(True)
        ##self.set_property("grid-line-pattern", "\000\001")
        ##self.set_style(grid_line_pattern="\000\001")

        self._init_store()
        self._init_columns()

    def _init_store(self):
        get_iplayer_output_lines = get_iplayer.search(None)
        self.set_store(get_iplayer_output_lines)
        
    def _init_columns(self):
        ### First column
        
        renderer = Gtk.CellRendererToggle(indicator_size=11)
        renderer.set_alignment(0, 0.5)
        renderer.connect("toggled", self._on_cell_row_toggled)
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn(None, renderer, active=0)
        self.append_column(column)

        #### Second column

        renderer = Gtk.CellRendererText(max_width_chars=256)
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn("Serie", renderer, text=2)
        column.set_resizable(True)
        column.set_max_width(250)
        self.append_column(column)
        
        #### Third column

        renderer = Gtk.CellRendererText()
        #sizing=Gtk.TreeViewColumn.FIXED
        column = Gtk.TreeViewColumn("Episode ~ Description", renderer, text=3)
        column.set_resizable(True)
        self.append_column(column)

        #tooltip = Gtk.Tooltip()
        #self.connect("query-tooltip", self._on_query_tooltip)
        #self.set_tooltip_cell(tooltip, None, column, None)
        
    #def _on_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):      #, user_data):
    #    #tooltip.set_markup(widget.get_label())
    #    tooltip.set_text(widget.get_label())

    def _on_button_press_event(self, widget, event):
        # Check if right mouse button was pressed
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.main_window.ui_manager.get_popup_menu().popup(None, None, None, None, event.button, event.time)
            return True
        #return False
     
    def _on_row_activated(self, path, column, user_data):
        self.main_window.tool_bar_box._on_button_properties_clicked(None)
    
    def _on_cell_row_toggled(self, widget, path):
        model = self.get_model()
        new_toggle_value = not model[path][0]
        model[path][0] = new_toggle_value

        # Toggle children (one level deep) as well
        tree_iter = model.get_iter(path)
        if model.iter_has_child(tree_iter):
            child_iter = model.iter_children(tree_iter)
            while child_iter is not None:
                row = model[child_iter]
                row[0] = new_toggle_value
                child_iter = model.iter_next(child_iter)

        ## Toggle parent (one level up) if all siblings have the same state
        #parent_iter = model.iter_parent(tree_iter)
        #if parent_iter != None:
        #    toggle_parent = True
        #    iter_next = model.iter_next(tree_iter)
        #    while iter_next != None:
        #        row = model[iter_next]
        #        if row[0] != new_toggle_value:
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
        store = Gtk.TreeStore(bool, str, str, str)
        
        #NOTE Could use "for i, row in enumerate(tree_rows):"
        #     except that "i += 1" to skip a list item has no effect
        root_iter = None
        i = 0
        while i in range(len(tree_rows)):
            row = tree_rows[i]
            #if not row[2]:
            if row[3] is None:
                # Root level row
                
                # If root has only one child/leave then merge the two into one row
                #TODO try catch: if rows[i+ 1][2] and not rows[i+ 2][2]:
                if (i + 1 < len(tree_rows) and tree_rows[i + 1][3]) and (i + 2 >= len(tree_rows) or not tree_rows[i + 2][3]):
                    # Copy program index and description
                    #row[0] = tree_rows[i+1][0]
                    row[1] = tree_rows[i + 1][1]
                    row[3] = tree_rows[i + 1][3]
                    # Skip merged child/leave
                    i += 1
                root_iter = store.append(None, row)            
            else:
                # Child/leave level row
                store.append(root_iter, row)
            i += 1
        self.set_model(store)
        
        # Expanders are not drawn, so expand the tree now during initialization
        self.expand_all()

class DetailWindow(Gtk.Window):

    WIDTH = 800
    
    def __init__(self, get_iplayer_output_lines):
        Gtk.Window.__init__(self, title="properties - " + get_iplayer_downloader.common.__program_name__)
        self.set_border_width(BORDER_WIDTH)
        self.set_default_size(DetailWindow.WIDTH, 700)
        #self.maximize()
        #self.set_resizable(False)

        self._init_grid(get_iplayer_output_lines)

    def _init_grid(self, prop_table):
        ##min_content_height=600, min_content_width=600
        ##visible=True, can_focus=True, hscrollbar_policy=Gtk.Policy.AUTOMATIC, 
        #                               vscrollbar_policy=Gtk.Policy.AUTOMATIC
        scrolledwindow = Gtk.ScrolledWindow()
        ##self.set_default_size(400, 400)
        #scrolledwindow.set_hexpand(True)
        #scrolledwindow.set_vexpand(True)
        self.add(scrolledwindow)

        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        ##self.grid.set_row_homogeneous(False)
        ##self.grid.set_column_homogeneous(False)
        scrolledwindow.add_with_viewport(self.grid)

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
            image_url = markup.html2text(image_url)
            image_pathname = settings.TEMP_FILEPATH + os.sep + "images"
            image_filename = file.load_url(image_url, image_pathname)
            image = Gtk.Image.new_from_file(image_filename)
            self.grid.add(image)

        #### Property table
        
        frame = Gtk.Frame(label="Properties", label_xalign=0.02, margin=BORDER_WIDTH,
                          width_request=DetailWindow.WIDTH - (8 * BORDER_WIDTH))
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
                #REMOVE and avoid automatic text selection
                label1.set_selectable(True)
                prop_grid.attach(label1, 0, i, 1, 1)
                
                label2 = Gtk.Label(markup.text2html(prop_value), valign=Gtk.Align.START,
                                   halign=Gtk.Align.START, use_markup=True)
                label2.set_padding(BORDER_WIDTH, 0)
                label2.set_line_wrap(True)
                label2.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                label2.set_selectable(True)
                prop_grid.attach(label2, 1, i, 1, 1)

                #REMOVE and avoid automatic text selection
                if prop_label == "episode" or prop_label == "title":
                    focused_label = label2

        #REMOVE and avoid automatic text selection
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
                          width_request=DetailWindow.WIDTH - (8 * BORDER_WIDTH))
        self.grid.add(frame)

        url = "<a href=\"http://www.bbc.co.uk/iplayer\" title=\"BBC iPlayer\">BBC iPlayer</a>"
        url += "      "

        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url += files2urls(filepath)
        url += "      "
        
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += files2urls(filepath)

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

        self.radio_channels_entry = self.builder.get_object("PrefsRadioChannelsEntry")
        self.radio_download_path_entry = self.builder.get_object("PrefsRadioDownloadPathEntry")
        self.radio_download_file_chooser_button = self.builder.get_object("PrefsRadioDownloadFileChooserButton")
        self.radio_run_in_terminal_entry = self.builder.get_object("PrefsRadioRunInTerminalCheckButton")

        self.tv_channels_entry = self.builder.get_object("PrefsTvChannelsEntry")
        self.tv_download_path_entry = self.builder.get_object("PrefsTvDownloadPathEntry")
        self.tv_download_file_chooser_button = self.builder.get_object("PrefsTvDownloadFileChooserButton")
        self.tv_run_in_terminal_entry = self.builder.get_object("PrefsTvRunInTerminalCheckButton")

        ###
        
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url = files2urls(filepath)
        url += "      "
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += files2urls(filepath)
        
        label = self.builder.get_object("PrefsAdvGetIPlayerConfLabel")
        label.set_markup(url)

        ####
        
        self.dialog.set_title("preferences - " + get_iplayer_downloader.common.__program_name__)
        self._get_settings()

        self.builder.connect_signals(self)
        self.dialog.connect("response", self._response)

    def _get_settings(self):        
        self.radio_channels_entry.set_text(settings.config().get("radio", "channels"))
        self.radio_download_path_entry.set_text(settings.config().get("radio", "download-path"))
        self.radio_download_file_chooser_button.set_filename(settings.config().get("radio", "download-path"))
        self.radio_run_in_terminal_entry.set_active(string.str2bool(settings.config().get("radio", "run-in-terminal")))
        
        self.tv_channels_entry.set_text(settings.config().get("tv", "channels"))
        self.tv_download_path_entry.set_text(settings.config().get("tv", "download-path"))
        self.tv_download_file_chooser_button.set_filename(settings.config().get("tv", "download-path"))
        self.tv_run_in_terminal_entry.set_active(string.str2bool(settings.config().get("tv", "run-in-terminal")))

    def _set_settings(self):        
        settings.config().set("radio", "channels", self.radio_channels_entry.get_text())
        settings.config().set("radio", "download-path", self.radio_download_path_entry.get_text())
        settings.config().set("radio", "run-in-terminal", str(self.radio_run_in_terminal_entry.get_active()))
        
        settings.config().set("tv", "channels", self.tv_channels_entry.get_text())
        settings.config().set("tv", "download-path", self.tv_download_path_entry.get_text())
        settings.config().set("tv", "run-in-terminal", str(self.tv_run_in_terminal_entry.get_active()))

    def _on_prefs_revert_clicked(self, user_data):
        settings.revert()
        self._get_settings()
          
    def _on_prefs_cancel_clicked(self, user_data):
        settings.reload()
        self._get_settings()
          
    def _on_prefs_ok_clicked(self, user_data):
        self._set_settings()
        settings.save()

    def _on_radio_download_file_chooser_file_set(self, entry_widget):
        filename = self.radio_download_file_chooser_button.get_filename()
        #TODO entry_widget.set_text(GLib.filename_to_utf8(filename, -1, None, 25, None))
        entry_widget.set_text(filename)
        
    def _on_tv_download_file_chooser_file_set(self, entry_widget):
        filename = self.tv_download_file_chooser_button.get_filename()
        #TODO entry_widget.set_text(GLib.filename_to_utf8(filename, -1, None, 25, None))
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
        self.set_placeholder_text("filter programs")
        self.connect("icon-press", self._on_icon_press)
        
    def _on_icon_press(self, entry, icon_pos, event):
        if (icon_pos == Gtk.EntryIconPosition.SECONDARY):
            entry.set_text("")
            #entry.set_placeholder_text("filter programs")

def files2urls(filepath):
    basename = os.path.basename(filepath)
    url = "<a href=\"file://" + filepath + "\" title=\"get_iplayer " + basename + " configuration folder\">" + basename + "</a>"
    for root, dirs, files in os.walk(filepath):
        # Skip empty and subfolders (one level deep)
        if len(files) > 0 and filepath == root:
            files.sort()
            url += " ("
            for i, filename in enumerate(files):
                url += "<a href=\"file://" + os.path.join(filepath, filename) + "\" title=\"get_iplayer " + basename + " configuration file\">" + filename + "</a>"
                if (i < len(files) - 1):
                    url += ", "
            url += ")"
    return url
    #ALTERNATIVE ways of sorting a list of files in a folder
    #1) glob(<filename filter>)
    #2) listdir()

def main():
    window = MainWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    
    # Enable threads
    GObject.threads_init()
    
    Gtk.main()

if __name__ == "__main__":
    main()

