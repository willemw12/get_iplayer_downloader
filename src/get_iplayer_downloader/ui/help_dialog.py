from gi.repository import Gtk

# Load application-wide definitions
import get_iplayer_downloader

#NOTE Import module, not symbol names inside a module, to avoid circular import
import get_iplayer_downloader.ui.main_window

class HelpDialogWrapper(object):

    def __init__(self, parent):
        self.parent = parent
        
        self._init_dialog()
        
    def _init_dialog(self):
        self.dialog = Gtk.MessageDialog(self.parent, 0,
                                        Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE,
                                        "Keyboard Shortcuts", title="help - " + get_iplayer_downloader.PROGRAM_NAME)
        self.dialog.format_secondary_text(" ")
        self.dialog.set_default_response(Gtk.ResponseType.CLOSE)

        content_area = self.dialog.get_content_area()
        #content_area.set_size_request(800, 400)

        KEYBOARD_SHORTCUTS = [["Shortcut", "Command", "Description"],
                              [" ", None, None],
                              ["alt+enter", "Properties", get_iplayer_downloader.ui.main_window.TOOLTIP_VIEW_PROPERTIES],
                              ["ctrl+c", "Clear", get_iplayer_downloader.ui.main_window.TOOLTIP_TOOLS_CLEAR],
                              ["ctrl+d", "Download", get_iplayer_downloader.ui.main_window.TOOLTIP_TOOLS_DOWNLOAD],
                              ["ctrl+f", "Find", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_GO_TO_FIND],
                              ["ctrl+l", "Log", get_iplayer_downloader.ui.main_window.TOOLTIP_VIEW_LOG],
                              ["ctrl+p", "Play", get_iplayer_downloader.ui.main_window.TOOLTIP_VIEW_PLAYER],
                              ["ctrl+q", "Queue", get_iplayer_downloader.ui.main_window.TOOLTIP_OPTION_PVR_QUEUE],
                              ["ctrl+r", "Refresh", get_iplayer_downloader.ui.main_window.TOOLTIP_TOOLS_REFRESH],
                              ["ctrl+s, ctrl+shift+s", "Since", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_SINCE],
                              ["ctrl+t", "Type", get_iplayer_downloader.ui.main_window.TOOLTIP_SEARCH_ROTATE_PROG_TYPE],
                              [" ", None, None],
                              ["ctrl+1", "Type", None],
                              ["ctrl+2", "Category", None],
                              ["ctrl+3", "Channel", None],
                              #["ctrl+4, ctrl+shift+4", "Since", None],
                              ["ctrl+4, ctrl+5", "Since", None],
                              [" ", None, None],
                              ["down-arrow", None, "Go from tool bar to episode search result list"],
                              ["space or enter", None, "Toggle selection in the episode search result list"]]

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
        
        #self.dialog.show_all()
        grid.show_all()

    def run(self):
        self.dialog.run()
            
    def destroy(self):
        #if self.dialog is not None:
        self.dialog.destroy()
