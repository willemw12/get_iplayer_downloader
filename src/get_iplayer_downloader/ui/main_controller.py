import os
import webbrowser

from gi.repository import Gtk, Pango

# Load application-wide definitions
import get_iplayer_downloader

#NOTE Import module, not symbol names inside a module, to avoid circular import
import get_iplayer_downloader.ui.about_dialog as about_dialog
import get_iplayer_downloader.ui.help_dialog as help_dialog
import get_iplayer_downloader.ui.log_dialog as log_dialog
import get_iplayer_downloader.ui.main_window
import get_iplayer_downloader.ui.prefs_dialog as prefs_dialog
import get_iplayer_downloader.ui.props_window as props_window

from get_iplayer_downloader import command_util, get_iplayer, search_cache, settings
from get_iplayer_downloader.get_iplayer import SinceListIndex, SearchResultColumn, KEY_INDEX    #, VALUE_INDEX
from get_iplayer_downloader.tools import command, command_queue, config, file, string
from get_iplayer_downloader.ui.tools.dialog import ExtendedMessageDialog

class MainWindowController:
    """ Handle the active part of the main window related widgets.
        Activity between main widgets and activity towards the
        (source of the gtk widget) model, i.e. get_iplayer.py.
    """
    
    class PresetComboModelColumn:
        PRESET = 0
        PROG_TYPE = 1
    
    def __init__(self, main_window):
        self.main_window = main_window
        #self.log_dialog = None
        
        self.processes = 0
        self.errors_offset = 0
        self.downloaded_pid_set = None
        
        #NOTE convert class data members to an array or a dictionary
        #self.prog_types = [getattr(get_iplayer.ProgType, attr) for attr in dir(get_iplayer.ProgType) if not callable(attr) and not attr.startswith("__")]
        self.prog_types = {getattr(get_iplayer.ProgType, attr): True for attr in dir(get_iplayer.ProgType) if not callable(attr) and not attr.startswith("__")}

    def _update_processes_count(self):
        """ Update the number of running get_iplayer processes. """
        try:
            if os.name == "posix":
                self.processes = int(command.run("echo -n $(ps xo cmd | grep 'perl /usr/bin/get_iplayer ' | grep -v 'grep' | wc -l) ; exit 0", quiet=True))
            else:
                self.processes = 0
        except ValueError:
            # Sometimes self.processes is not a valid int (empty string?)
            self.processes = 0
    
    def init(self):
        """ Complete initialization, after the main window has completed its initialization. """

        self.ui_manager = self.main_window.ui_manager
        self.tool_bar_box = self.main_window.tool_bar_box
        self.main_tree_view = self.main_window.main_tree_view

        # Initialize label text
        self.on_progress_bar_update(None)

    def _set_filters_sensitive(self, prog_type):
        """ Disable filters when search results have been cached. """
        enable_filters = not search_cache.has_cache(prog_type)
        #self.tool_bar_box.search_entry.set_sensitive(enable_filters)
        #self.tool_bar_box.search_entry.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, True)
        #self.tool_bar_box.search_entry.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, enable_filters)
        self.tool_bar_box.search_entry.set_editable(enable_filters)
        self.tool_bar_box.category_combo.set_sensitive(enable_filters)
        self.tool_bar_box.channel_combo.set_sensitive(enable_filters)
        self.tool_bar_box.since_combo.set_sensitive(enable_filters)
        self.tool_bar_box.search_all_check_button.set_sensitive(enable_filters)
        self.tool_bar_box.future_check_button.set_sensitive(enable_filters)

    def on_button_play_clicked_by_pid(self, button, pid):
        """ Visit BBC iPlayer web site. If @pid is None, then play selected episode in the tree view """
        # button can be None
        if pid is None:
            # Get PID from selected episode in the tree view
            model, tree_iter = self.main_tree_view.get_selection().get_selected()
            if tree_iter is not None:
                #index = model[tree_iter][SearchResultColumn.INDEX]
                #if index:
                
                # Generate player URL. Note that get_iplayer does not retrieve 
                # the value of the <player> field when searching episodes
                pid = model[tree_iter][SearchResultColumn.PID]
                if pid is None:
                    dialog = Gtk.MessageDialog(self.main_window, 0,
                                               Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                               "No episode highlighted. A series is highlighted")
                    #dialog.format_secondary_text("")
                    dialog.run()
                    dialog.destroy()
                    #return
            else:
                dialog = Gtk.MessageDialog(self.main_window, 0,
                                           Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                           "No episode highlighted")
                #dialog.format_secondary_text("")
                dialog.run()
                dialog.destroy()
                #return

        if pid:
            if pid.startswith("http"):
                # URL
                self.on_button_play_clicked_by_url(None, pid)
            else:
                #TODO if prog_type not in [get_iplayer.Channels.CH4, get_iplayer.Channels.ITV]:
                # Go to episode's information page
                #self.on_button_play_clicked_by_url(None, "https://www.bbc.co.uk/iplayer/episode/" + pid)
                # Go to episode's player page
                self.on_button_play_clicked_by_url(None, "https://www.bbc.co.uk/sounds/play/" + pid)

    def on_button_play_clicked_by_url(self, button, url):
        """ Visit BBC iPlayer web site. """
        if url is not None:
            webbrowser.open_new_tab(url)

    def on_button_properties_clicked(self, button):
        # button can be None
        preset = None
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            #search_all = self.tool_bar_box.search_all_presets_check_button.get_active()
            #if search_all_presets:
            if string.str2bool(settings.get_config().get(config.NOSECTION, "disable-presets")):
                preset = None
            else:
                preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]

        proxy_disabled = string.str2bool(settings.get_config().get(config.NOSECTION, "disable-proxy"))

        future = self.tool_bar_box.future_check_button.get_active()

        model, tree_iter = self.main_tree_view.get_selection().get_selected()
        if tree_iter is not None:
            #index = model[tree_iter][SearchResultColumn.INDEX]
            #if index:
            pid = model[tree_iter][SearchResultColumn.PID]
            if pid:
                self.main_window.display_busy_mouse_cursor(True)
                get_iplayer_output_lines = get_iplayer.info(
                                                pid, None, preset=preset, prog_type=prog_type,
                                                proxy_disabled=proxy_disabled, future=future)
                self.main_window.display_busy_mouse_cursor(False)

                self.on_progress_bar_update(None)

                window = props_window.PropertiesWindow(self, get_iplayer_output_lines, icon=self.main_window.get_icon())
                window.show_all()
            else:
                dialog = Gtk.MessageDialog(self.main_window, 0,
                                           Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                           "No episode highlighted. A series is highlighted")
                #dialog.format_secondary_text("")
                dialog.run()
                dialog.destroy()
        else:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "No episode highlighted")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()

    def on_button_download_clicked(self, button, pvr_queue=False):
        # button can be None
        preset = None
        prog_type = None
        alt_recording_mode = False
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            
            #NOTE Downloading in "All" preset mode will not even work when all settings (radiomode, tvmode,
            #     outputradio, outputtv, etc.) are in one file (in the options file or a single preset file).
            #     Get_iplayer.get() cannot (easily) determine the prog_type of each episode and
            #     get_iplayer does not determine the programme type by it self
            #search_all = self.tool_bar_box.search_all_presets_check_button.get_active()
            #if search_all_presets:
            if string.str2bool(settings.get_config().get(config.NOSECTION, "disable-presets")):
                preset = None
            else:
                preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]
            #channel = model[tree_iter][self.PresetComboModelColumn.CHANNEL]

            alt_recording_mode = self.tool_bar_box.alt_recording_mode_check_button.get_active()
    
        dry_run = self.tool_bar_box.dry_run_check_button.get_active()
        force = self.tool_bar_box.force_check_button.get_active()
        future = self.tool_bar_box.future_check_button.get_active()
        
        #PVR_CHECK_BUTTON
        #pvr_queue_checkbox_state = self.tool_bar_box.pvr_queue_check_button.get_active()
        #if button is not None and not pvr_queue:
        #    # If event was raised from the tool bar download button and not from a keyboard shortcut,
        #    # then the PVR check button determines the download/queue mode
        #    pvr_queue = pvr_queue_checkbox_state
        
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

        #if not indices:
        if len(pid_list) == 0:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "No episodes selected")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
            #return True
            return
        
        ####
        
        ## Avoid downloading an episode twice in parallel, otherwise continue downloading
        ## twice and let get_iplayer generate an "Already in history" INFO log message.
        ## The user can download episodes in parallel without having
        ## to clear the previous download selection and therefore avoiding
        ## download errors because of two threads trying to download the same episode
        #
        #try:
        #    if os.name == "posix":
        #        #NOTE 2>/dev/null: to surpress error messages, e.g.:
        #        #    Signal 18 (CONT) caught by ps (procps-ng version 3.3.9).
        #        #    ps:display.c:66: please report this bug
        #        gipd_processes = int(command.run("echo -n $(ps xo cmd 2>/dev/null | grep 'get_iplayer_downloader' | grep 'python' | grep -v 'grep' | wc -l) ; exit 0", quiet=True))
        #    else:
        #        gipd_processes = 1
        #except ValueError:
        #    # Sometimes gipd_processes is not a valid int (empty string?)
        #    gipd_processes = 1
        #
        ## If there are more than one get_iplayer_downloader processes running,
        ## then don't perform the 'running in parallel' check (self.processes is
        ## the number of >all< the get_iplayer processes on the system).
        ## (TODO Limit self.processes to the get_iplayer processes which belong
        ## to the current get_iplayer_downloader process).
        ## TODO detect 'programme type' change
        ##PVR_CHECK_BUTTON
        ##if gipd_processes == 1 and not dry_run and not pvr_queue:
        #if gipd_processes == 1 and not dry_run:
        #    # Update self.processes now, to avoid any progress bar update delay
        #    self._update_processes_count()
        #    if self.processes > 0:
        #        #if not force:
        #        # Remove already downloaded PIDs from the PID set (copy of pid_list)
        #        pid_set = set(pid_list)
        #        downloaded_pid_set = set(self.downloaded_pid_list)
        #        pid_list = list(pid_set.difference(downloaded_pid_set))
        #    if len(pid_list) == 0:
        #        dialog = Gtk.MessageDialog(self.main_window, 0,
        #                                   Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
        #                                   "Already downloading all the selected episodes")
        #        #dialog.format_secondary_text("")
        #        dialog.run()
        #        dialog.destroy()
        #        #return True
        #        return        
        
        ####
        
        self.main_window.display_busy_mouse_cursor(True)
        launched, process_output = get_iplayer.get(pid_list, pid=True, pvr_queue=pvr_queue, preset=preset,
                                                   prog_type=prog_type, alt_recording_mode=alt_recording_mode,
                                                   dry_run=dry_run, force=force, future=future)
        self.main_window.display_busy_mouse_cursor(False)
        
        self.on_progress_bar_update(None)

        if not launched:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "get_iplayer not launched")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()
        #PVR_CHECK_BUTTON
        #elif pvr_queue_checkbox_state or pvr_queue or future:
        #    # If implicitly or explicitly queuing, always show the Queued Episodes dialog window,
        #    # even if nothing will be queued
        elif dry_run or pvr_queue or future:
            if dry_run:
                if process_output is not None:
                    process_output = process_output.replace("; ", "\n") + "\n"
                message_format = "Command list"
            else:
                message_format = "Queued Episodes"

            # When queuing episodes, always show the Queued Episodes dialog window, even if nothing will be queued
            dialog = ExtendedMessageDialog(self.main_window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, message_format)
            #dialog.format_secondary_text("")
            dialog.set_default_response(Gtk.ResponseType.CLOSE)
            dialog.get_content_area().set_size_request(get_iplayer_downloader.ui.main_window.WINDOW_LARGE_WIDTH,
                                                       get_iplayer_downloader.ui.main_window.WINDOW_LARGE_HEIGHT)
            dialog.format_tertiary_scrolled_text("" if process_output is None else process_output)
            label = dialog.get_scrolled_label()
            label.set_valign(Gtk.Align.START)
            label.set_halign(Gtk.Align.START)
            label.set_selectable(True)
            #label.override_font(Pango.FontDescription("monospace small"))
            label.override_font(Pango.FontDescription("monospace 10"))
            dialog.run()
            dialog.destroy()
        else:
            #self.main_window.main_tree_view.grab_focus()
            self.downloaded_pid_list = pid_list

    def on_button_pvr_queue_clicked(self, button):
        self.on_button_download_clicked(None, pvr_queue=True)

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
        
        # Refresh episode cache

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
            (channels, exclude_channels) = _separate_excluded_channels(channels)

        future = self.tool_bar_box.future_check_button.get_active()

        self.main_window.display_busy_mouse_cursor(True)
        get_iplayer.refresh(preset=preset, prog_type=prog_type, channels=channels, exclude_channels=exclude_channels, future=future)
        self.main_window.display_busy_mouse_cursor(False)
        
        # Refresh episode list

        self.on_button_find_clicked(None)

    def _check_first_time_find(self, prog_type):
        """ Return True if @prog_type has been searched in for the first time. """
        first_time = self.prog_types[prog_type]
        if first_time:
            self.prog_types[prog_type] = False
        return first_time

    def on_button_find_clicked(self, button):
        # button can be None
        search_text = self.tool_bar_box.search_entry.get_text()
        search_all = self.tool_bar_box.search_all_check_button.get_active()
        disable_presets = string.str2bool(settings.get_config().get(config.NOSECTION, "disable-presets"))
        
        preset = None
        prog_type = None
        combo = self.tool_bar_box.preset_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            if disable_presets:
                preset = None
            else:
                preset = model[tree_iter][self.PresetComboModelColumn.PRESET]
            prog_type = model[tree_iter][self.PresetComboModelColumn.PROG_TYPE]

        categories = None
        exclude_categories = None
        combo = self.tool_bar_box.category_combo
        if not search_all or combo.get_active() > 0:
            # A specific set of categories has been selected
            tree_iter = combo.get_active_iter()
            if tree_iter is not None:
                model = combo.get_model()
                #WORKAROUND see also get_iplayer.py (at least in Python 2.7)
                #    On some systems, when model[tree_iter][KEY_INDEX] == None, the following exception is raised:
                #    AttributeError: 'NoneType' object has no attribute 'decode'
                #    In the debugger, model[tree_iter][KEY_INDEX] is displayed as a unicode string.
                categories = model[tree_iter][KEY_INDEX]
                (categories, exclude_categories) = _separate_excluded_categories(categories)
                
        channels = None
        exclude_channels = None
        combo = self.tool_bar_box.channel_combo
        if not search_all or combo.get_active() > 0:
            # A specific set of channels has been selected
            tree_iter = combo.get_active_iter()
            if tree_iter is not None:
                model = combo.get_model()
                channels = model[tree_iter][KEY_INDEX]
                #ALTERNATIVE
                #channels = model.get_value(tree_iter, KEY_INDEX)
                (channels, exclude_channels) = _separate_excluded_channels(channels)

        since = 0
        combo = self.tool_bar_box.since_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            since = model[tree_iter][KEY_INDEX]

        future = self.tool_bar_box.future_check_button.get_active()

        self.main_window.display_busy_mouse_cursor(True)
        if self._check_first_time_find(prog_type):
            get_iplayer.refresh(preset=preset, prog_type=prog_type, channels=channels, exclude_channels=exclude_channels, future=future)
        output_lines = get_iplayer.search(search_text, preset=preset, prog_type=prog_type,
                                          channels=channels, exclude_channels=exclude_channels,
                                          categories=categories, exclude_categories=exclude_categories,
                                          since=since, future=future)
        self.main_window.display_busy_mouse_cursor(False)

        self.on_progress_bar_update(None)

        self.main_tree_view.set_store(output_lines)
        # Scroll to top
        adjustment = self.main_window.main_tree_view_scrollbars.get_vadjustment()
        adjustment.set_value(0.0)
        adjustment.value_changed()
        #adjustment = self.main_window.main_tree_view_scrollbars.set_vadjustment(adjustment)

        #if disable_presets:
        #    prog_type = None
        self.main_window.set_window_title(prog_type=prog_type)

        # Invalidate downloaded PID list
        self.downloaded_pid_list = []
        
        # Disable filters when there are cached search results available
        self._set_filters_sensitive(prog_type)

    def on_button_similar_clicked(self, button, locate_search_term):
        # button can be None
        
        if os.name == "posix" and locate_search_term is not None:
            output = ""

            self.main_window.display_busy_mouse_cursor(True)
            cmd = "locate " + file.sanitize_path(locate_search_term, False)
            process_output = command.run(cmd, quiet=True)
            output += cmd + ":\n" + process_output
            self.main_window.display_busy_mouse_cursor(False)
                             
            dialog = ExtendedMessageDialog(self.main_window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                           "Similar Episodes")
            #dialog.format_secondary_text("")
            dialog.set_default_response(Gtk.ResponseType.CLOSE)
            dialog.get_content_area().set_size_request(get_iplayer_downloader.ui.main_window.WINDOW_LARGE_WIDTH_WIDE,
                                                       get_iplayer_downloader.ui.main_window.WINDOW_LARGE_HEIGHT_WIDE)

            dialog.format_tertiary_scrolled_text(output)
            label = dialog.get_scrolled_label()
            label.set_valign(Gtk.Align.START)
            label.set_halign(Gtk.Align.START)
            label.set_selectable(True)
            #label.override_font(Pango.FontDescription("monospace small"))
            label.override_font(Pango.FontDescription("monospace 10"))
            dialog.run()
            dialog.destroy()

    ####
    
    def on_accel_go_to_find(self):
        self.tool_bar_box.search_entry.grab_focus()

    def on_accel_locate_similar(self, locate_search_term):
        model, tree_iter = self.main_tree_view.get_selection().get_selected()
        if tree_iter is not None:
            #index = model[tree_iter][SearchResultColumn.INDEX]
            #if index:
            locate_search_term = model[tree_iter][SearchResultColumn.LOCATE_SEARCH_TERM]
            #if locate_search_term:
            self.on_button_similar_clicked(None, locate_search_term)
        else:
            dialog = Gtk.MessageDialog(self.main_window, 0,
                                       Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                       "No episode highlighted")
            #dialog.format_secondary_text("")
            dialog.run()
            dialog.destroy()

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

    def on_accel_rotate_programme_type(self):
        self._rotate_combo(self.tool_bar_box.preset_combo, False)
        #NOTE combo.set_active() already causes the invocation of on_combo_preset_changed()
        #self.tool_bar_box.on_combo_preset_changed(combo)

    def on_accel_rotate_category(self):
        self._rotate_combo(self.tool_bar_box.category_combo, False)

    def on_accel_rotate_channel(self):
        self._rotate_combo(self.tool_bar_box.channel_combo, False)

    def on_accel_rotate_since(self, backward):
        self._rotate_combo(self.tool_bar_box.since_combo, backward)

    ####
    
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
            elif prog_type == get_iplayer.ProgType.TV:
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_tv_store)
            elif prog_type in [get_iplayer.ProgType.CH4, get_iplayer.ProgType.ITV]:
                #self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_tv_store)
                self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_disabled_store)
            self.tool_bar_box.category_combo.set_active(0)

            # Synchronize channel filter
            if preset == get_iplayer.Preset.RADIO:
                self.tool_bar_box.channel_combo.set_model(self.tool_bar_box.chan_radio_store)
            elif preset == get_iplayer.Preset.TV:
                if prog_type == get_iplayer.ProgType.CH4:
                    self.tool_bar_box.channel_combo.set_model(self.tool_bar_box.chan_ch4_store)
                elif prog_type == get_iplayer.ProgType.ITV:
                    self.tool_bar_box.channel_combo.set_model(self.tool_bar_box.chan_itv_store)
                else:
                    self.tool_bar_box.channel_combo.set_model(self.tool_bar_box.chan_tv_store)
            self.tool_bar_box.channel_combo.set_active(0)

            combo = self.tool_bar_box.since_combo
            model = combo.get_model()
            if combo.get_active() == len(model) - 1:
                # Disable since filter
                combo.set_active(SinceListIndex.FOREVER)
                
            # Disable filters when there are cached search results available
            self._set_filters_sensitive(prog_type)

    ####
    
    def on_check_button_future_clicked(self, check_button):
        if check_button.get_active():
            #PVR_CHECK_BUTTON
            #self.tool_bar_box.pvr_queue_check_button.set_active(True)

            ## Limit the initial search result to future episodes
            #combo = self.tool_bar_box.since_combo
            #combo.set_active(SinceListIndex.FUTURE)

            # Disable the category filter. Get_iplayer doesn't support it 
            # and future episode data sometimes lacks the categories property
            self.tool_bar_box.category_combo.set_model(self.tool_bar_box.cat_disabled_store)
            self.tool_bar_box.category_combo.set_active(0)
        else:
            #PVR_CHECK_BUTTON
            #self.tool_bar_box.pvr_queue_check_button.set_active(False)

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

    def on_preferences(self):
        #try:
        #    getattr(self.main_window, "preferences_dialog")
        #except AttributeError:
        #    self.main_window.preferences_dialog = prefs_dialog.PreferencesDialogWrapper(self.main_window)
        
        dialog = prefs_dialog.PreferencesDialogWrapper(self.main_window.builder.builder, 
                                                       icon=self.main_window.get_icon())
        #dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.run()
        dialog.destroy()

    def on_help(self):
        dialog = help_dialog.HelpDialogWrapper(self.main_window)
        #dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.run()
        dialog.destroy()

    #TODO about_dialog.py
    def on_about(self):
        ##dialog = self.main_window.builder.get_object("AboutDialog")
        dialog = about_dialog.AboutDialogWrapper(self.main_window)
        #dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.run()
        dialog.destroy()

    ####
    
    def invalidate_error_offset(self):
        self.errors_offset = -1
        self.on_progress_bar_update(None)

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
        self.tool_bar_box.progress_bar.set_text("{0} / {1}".format(self.processes, errors))
        # Full progress bar when TOTAL_WORKER_THREADS get_iplayer processes are running.  % 1 to keep the fraction between 0.0 and 1.0.
        self.tool_bar_box.progress_bar.set_fraction(self.processes / float(command_queue.TOTAL_WORKER_THREADS) % 1)
        # Gray-out
        #self.tool_bar_box.progress_bar.set_sensitive(self.processes != 0 or command_queue.size() != 0)

        return True

    def on_progress_bar_button_press_event(self, widget, event):
        # widget and event can be None
        
        #if self.log_dialog is not None:
        #    # Dialog is already running
        #    #return False
        #    return
        
        if event is not None and event.button != 1:
            # Not left mouse click
            #return False
            return

        # Display download log dialog window
        self.log_dialog = log_dialog.LogViewerDialogWrapper(self)
        self.log_dialog.run()
        self.log_dialog.destroy()
        
        #self.log_dialog = None

    ####
    
    def session_save(self):
        restore_session = string.str2bool(settings.get_config().get(config.NOSECTION, "restore-session"))
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
            if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-category-filter")):
                categories = ""
                combo = self.tool_bar_box.category_combo
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    model = combo.get_model()
                    categories = model[tree_iter][KEY_INDEX]
                if categories.startswith(","):
                    # Remove prepended "all" filter
                    categories = categories[1:]

            channels = None
            if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-channel-filter")):
                channels = ""
                combo = self.tool_bar_box.channel_combo
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    model = combo.get_model()
                    channels = model[tree_iter][KEY_INDEX]

            since = -1
            if string.str2bool(settings.get_config().get(config.NOSECTION, "enable-since-filter")):
                since = 0
                combo = self.tool_bar_box.since_combo
                tree_iter = combo.get_active_iter()
                if tree_iter is not None:
                    model = combo.get_model()
                    since = model[tree_iter][KEY_INDEX]

            search_all = self.tool_bar_box.search_all_check_button.get_active()

            # Save values

            # If not an empty string (and not None)
            if prog_type is not None:
                settings.get_config().set("session", "programme-type", prog_type)
            if categories is not None:
                settings.get_config().set("session", "categories", categories)
            if channels is not None:
                settings.get_config().set("session", "channels", channels)
            if since >= 0:
                settings.get_config().set("session", "since", str(since))
            settings.get_config().set("session", "search-all", str(search_all))
            
            settings.save_config()
    
    def session_restore(self):
        restore_session = string.str2bool(settings.get_config().get(config.NOSECTION, "restore-session"))
        if restore_session:
            prog_type = settings.get_config().get("session", "programme-type")
            categories = settings.get_config().get("session", "categories")
            channels = settings.get_config().get("session", "channels")
            #NOTE Variables created in the try clause or except clause remain allocated after the try-except statement
            try:
                since = int(settings.get_config().get("session", "since"))
            except ValueError:
                since = 0
            search_all = string.str2bool(settings.get_config().get("session", "search-all"))

            # If empty string or None (in case of an error) or ch4/itv has been disabled, then set the default value
            if not prog_type or \
                    (prog_type == "ch4" and not string.str2bool(settings.get_config().get(config.NOSECTION, "enable-ch4"))) or \
                    (prog_type == "itv" and not string.str2bool(settings.get_config().get(config.NOSECTION, "enable-itv"))):
                prog_type = get_iplayer.ProgType.RADIO
            if not categories:
                categories = ""
            if not channels:
                channels = ""

            # Don't restore when filter widget is disabled
            if not string.str2bool(settings.get_config().get(config.NOSECTION, "enable-category-filter")):
                categories = None
            if not string.str2bool(settings.get_config().get(config.NOSECTION, "enable-channel-filter")):
                channels = None
            if not string.str2bool(settings.get_config().get(config.NOSECTION, "enable-since-filter")):
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

            self.tool_bar_box.search_all_check_button.set_active(search_all)

####

def _separate_excluded_categories(categories):
    #if not "\"-" in channels and  not ",-" in channels:
    if not "-" in categories:
        return (categories, None)
    
    include_categories = None
    exclude_categories = None

    category_list = categories.split(",")
    for category in category_list:
        #if category is not None:
        if category.startswith("-"):
            # Add substring
            if exclude_categories is None:
                exclude_categories = category[1:]
            else:
                exclude_categories += "," + category[1:]
        else:
            if include_categories is None:
                include_categories = category
            else:
                include_categories += "," + category

    return (include_categories, exclude_categories)

def _separate_excluded_channels(channels):
    #if not "\"-" in channels and  not ",-" in channels:
    if not "-" in channels:
        return (channels, None)
    
    include_channels = None
    exclude_channels = None

    channel_list = channels.split(",")
    for channel in channel_list:
        #if channel is not None:
        if channel.startswith("-"):
            # Add substring
            if exclude_channels is None:
                exclude_channels = channel[1:]
            else:
                exclude_channels += "," + channel[1:]
        else:
            if include_channels is None:
                include_channels = channel
            else:
                include_channels += "," + channel

    return (include_channels, exclude_channels)
