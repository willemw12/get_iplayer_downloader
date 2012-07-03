from gi.repository import Gtk

# Load application-wide definitions
import get_iplayer_downloader

class AboutDialogWrapper(object):

    def __init__(self, parent):
        self.parent = parent

        self._init_dialog()
        
    def _init_dialog(self):
        self.dialog = Gtk.AboutDialog()
        self.dialog.set_transient_for(self.parent)

        self.dialog.set_program_name(get_iplayer_downloader.PROGRAM_NAME)
        #self.dialog.set_logo_icon_name(Gtk.STOCK_GOTO_BOTTOM)
        self.dialog.set_logo_icon_name(get_iplayer_downloader.PROGRAM_NAME)
        self.dialog.set_comments(get_iplayer_downloader.DESCRIPTION + "\n\n" + get_iplayer_downloader.LONG_DESCRIPTION)
        self.dialog.set_version(get_iplayer_downloader.VERSION)
        self.dialog.set_website(get_iplayer_downloader.URL)
        self.dialog.set_website_label(get_iplayer_downloader.URL)
        #NOTE [""] is char** in C
        self.dialog.set_authors([get_iplayer_downloader.AUTHORS])

    def run(self):
        self.dialog.run()
            
    def destroy(self):
        #if self.dialog is not None:
        self.dialog.destroy()
