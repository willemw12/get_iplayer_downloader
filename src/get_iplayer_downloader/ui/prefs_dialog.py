import os

from gi.repository import Gtk

# Load application-wide definitions
import get_iplayer_downloader

from get_iplayer_downloader import settings
from get_iplayer_downloader.tools import config, file, string

class PreferencesDialogWrapper(object):

    def __init__(self, builder):
        self.builder = builder
        
        self._init_dialog()
        
    def _init_dialog(self):
        self.dialog = self.builder.get_object("PreferencesDialog")

        self.general_clear_cache_on_exit_check_button = self.builder.get_object("PrefsGeneralClearCacheOnExitCheckButton")
        self.general_compact_toolbar_check_button = self.builder.get_object("PrefsGeneralCompactToolBarCheckButton")
        self.general_compact_treeview_check_button = self.builder.get_object("PrefsGeneralCompactTreeViewCheckButton")
        self.general_disable_presets_check_button = self.builder.get_object("PrefsGeneralDisablePresetsCheckButton")
        self.general_disable_proxy_check_button = self.builder.get_object("PrefsGeneralDisableProxyCheckButton")
        self.general_show_menubar_check_button = self.builder.get_object("PrefsGeneralShowMenuBarCheckButton")
        self.general_show_tooltip_check_button = self.builder.get_object("PrefsGeneralShowTooltipCheckButton")
        self.general_start_maximized_check_button = self.builder.get_object("PrefsGeneralStartMaximizedCheckButton")
        self.general_terminal_emulator_entry = self.builder.get_object("PrefsGeneralTerminalEmulatorEntry")

        self.radio_channels_entry = self.builder.get_object("PrefsRadioChannelsEntry")
        self.radio_download_path_entry = self.builder.get_object("PrefsRadioDownloadPathEntry")
        self.radio_download_file_chooser_button = self.builder.get_object("PrefsRadioDownloadFileChooserButton")
        self.radio_preset_file_entry = self.builder.get_object("PrefsRadioPresetFileEntry")
        self.radio_recording_modes_entry = self.builder.get_object("PrefsRadioRecordingModesEntry")
        self.radio_run_in_terminal_check_button = self.builder.get_object("PrefsRadioRunInTerminalCheckButton")

        self.tv_channels_entry = self.builder.get_object("PrefsTvChannelsEntry")
        self.tv_download_path_entry = self.builder.get_object("PrefsTvDownloadPathEntry")
        self.tv_download_file_chooser_button = self.builder.get_object("PrefsTvDownloadFileChooserButton")
        self.tv_preset_file_entry = self.builder.get_object("PrefsTvPresetFileEntry")
        self.tv_recording_modes_entry = self.builder.get_object("PrefsTvRecordingModesEntry")
        self.tv_run_in_terminal_check_button = self.builder.get_object("PrefsTvRunInTerminalCheckButton")

        ####
        
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "pvr")
        url = file.files2urls(filepath)
        url += "      "
        filepath = os.path.join(os.path.expanduser("~"), ".get_iplayer", "presets")
        url += file.files2urls(filepath)
        
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
        self.general_disable_presets_check_button.set_active(string.str2bool(settings.config().get(config.NOSECTION, "disable-presets")))
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
        self.radio_preset_file_entry.set_text(settings.config().get("radio", "preset-file"))
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
        self.tv_preset_file_entry.set_text(settings.config().get("tv", "preset-file"))
        self.tv_recording_modes_entry.set_text(settings.config().get("tv", "recording-modes"))
        self.tv_run_in_terminal_check_button.set_active(string.str2bool(settings.config().get("tv", "run-in-terminal")))

    def _capture_settings(self):
        """ Retrieve settings from dialog fields and put them in in-memory settings. """

        settings.config().set(config.NOSECTION, "clear-cache-on-exit", str(self.general_clear_cache_on_exit_check_button.get_active()))
        settings.config().set(config.NOSECTION, "compact-toolbar", str(self.general_compact_toolbar_check_button.get_active()))
        settings.config().set(config.NOSECTION, "compact-treeview", str(self.general_compact_treeview_check_button.get_active()))
        settings.config().set(config.NOSECTION, "disable-presets", str(self.general_disable_presets_check_button.get_active()))
        settings.config().set(config.NOSECTION, "disable-proxy", str(self.general_disable_proxy_check_button.get_active()))
        settings.config().set(config.NOSECTION, "show-menubar", str(self.general_show_menubar_check_button.get_active()))
        settings.config().set(config.NOSECTION, "show-tooltip", str(self.general_show_tooltip_check_button.get_active()))
        settings.config().set(config.NOSECTION, "start-maximized", str(self.general_start_maximized_check_button.get_active()))
        settings.config().set(config.NOSECTION, "terminal-emulator", self.general_terminal_emulator_entry.get_text())

        settings.config().set("radio", "channels", self.radio_channels_entry.get_text())
        settings.config().set("radio", "download-path", self.radio_download_path_entry.get_text())
        settings.config().set("radio", "preset-file", self.radio_preset_file_entry.get_text())
        settings.config().set("radio", "recording-modes", self.radio_recording_modes_entry.get_text())
        settings.config().set("radio", "run-in-terminal", str(self.radio_run_in_terminal_check_button.get_active()))
        
        settings.config().set("tv", "channels", self.tv_channels_entry.get_text())
        settings.config().set("tv", "download-path", self.tv_download_path_entry.get_text())
        settings.config().set("tv", "preset-file", self.tv_preset_file_entry.get_text())
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
        settings.revert_option(config.NOSECTION, "disable-presets")
        settings.revert_option(config.NOSECTION, "disable-proxy")
        settings.revert_option(config.NOSECTION, "show-menubar")
        settings.revert_option(config.NOSECTION, "show-tooltip")
        settings.revert_option(config.NOSECTION, "start-maximized")
        settings.revert_option(config.NOSECTION, "terminal-emulator")

        settings.revert_option("radio", "channels")
        settings.revert_option("radio", "download-path")
        settings.revert_option("radio", "preset-file")
        settings.revert_option("radio", "recording-modes")
        settings.revert_option("radio", "run-in-terminal")
        
        settings.revert_option("tv", "channels")
        settings.revert_option("tv", "download-path")
        settings.revert_option("tv", "preset-file")
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
            
    def destroy(self):
        #if self.dialog is not None:
        self.dialog.destroy()
