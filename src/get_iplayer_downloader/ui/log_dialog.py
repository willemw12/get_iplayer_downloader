from gi.repository import Gtk, Pango

# Load application-wide definitions
import get_iplayer_downloader

#NOTE Import module, not symbol names inside a module, to avoid circular import
import get_iplayer_downloader.ui.main_window

from get_iplayer_downloader import command_util
from get_iplayer_downloader.tools import markup
from get_iplayer_downloader.ui.tools.dialog import ExtendedMessageDialog

#NOTE Positive ID numbers are for user-defined buttons
CLEAR_CACHE_BUTTON_ID = 1
RESET_ERROR_COUNT_BUTTON_ID = 2
FULL_LOG_BUTTON_ID = 3
SUMMARY_LOG_BUTTON_ID = 4

class LogViewerDialogWrapper(object):

    def __init__(self, main_controller):
        self.main_controller = main_controller
        
        self._init_dialog()
        
    def _init_dialog(self):
        self.dialog = ExtendedMessageDialog(self.main_controller.main_window, 0,
                                Gtk.MessageType.INFO, Gtk.ButtonsType.NONE,
                                "", title="download log - " + get_iplayer_downloader.PROGRAM_NAME)

        label = self.dialog.get_scrolled_label()
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

        self.dialog.add_button("Clear log and cache", CLEAR_CACHE_BUTTON_ID)
        self.dialog.add_button("Reset error count", RESET_ERROR_COUNT_BUTTON_ID)
        self.dialog.add_button("Detailed log", FULL_LOG_BUTTON_ID)
        self.dialog.add_button("Log", SUMMARY_LOG_BUTTON_ID)
        self.dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        
        # Dialog buttons are laid out from left to right
        button = self.dialog.get_action_area().get_children()[0]
        #button.set_image(Gtk.Image(stock=Gtk.STOCK_DELETE))
        button.set_tooltip_text("Remove log files and image cache files")
        button = self.dialog.get_action_area().get_children()[1]
        #button.set_image(Gtk.Image(stock=Gtk.STOCK_CLEAR))
        button.set_tooltip_text("Reset error count in the progress bar")
        button = self.dialog.get_action_area().get_children()[2]
        button.set_image(Gtk.Image(stock=Gtk.STOCK_REFRESH))
        button.set_tooltip_text("Refresh today's download log")
        button = self.dialog.get_action_area().get_children()[3]
        button.set_image(Gtk.Image(stock=Gtk.STOCK_REFRESH))
        button.set_tooltip_text("Refresh today's summary download log")
        #button.grab_focus()
        # Close button
        button = self.dialog.get_action_area().get_children()[4]
        button.grab_focus()
        
        self.dialog.set_default_response(Gtk.ResponseType.CLOSE)
        #self.dialog.format_secondary_text("")
        self.dialog.get_content_area().set_size_request(get_iplayer_downloader.ui.main_window.WINDOW_LARGE_WIDTH,
                                                        get_iplayer_downloader.ui.main_window.WINDOW_LARGE_HEIGHT)

    def run(self):
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
            log_output = command_util.download_log(full=full, markup=markup)

            # Set dialog content title
            self.dialog.set_property("text", message_format)
            # Set dialog content text
            #NOTE If full download log text is too large, it won't be displayed
            if markup:
                self.dialog.format_tertiary_scrolled_markup(log_output)
            else:
                self.dialog.format_tertiary_scrolled_text(log_output)
            
            # Grab focus to enable immediate page-up/page-down scrolling with the keyboard
            #label = self.dialog.get_scrolled_label()
            #scrolled_window = label.get_parent().get_parent()
            #scrolled_window.grab_focus()
            
            if button_id == FULL_LOG_BUTTON_ID or button_id == SUMMARY_LOG_BUTTON_ID:
                if button_id_prev != button_id:
                    # Log view changed (different log view type or log files removed)
                    # Scroll to top
                    label = self.dialog.get_scrolled_label()
                    adjustment = label.get_parent().get_vadjustment()
                    adjustment.set_value(0.0)
                    adjustment.value_changed()
                    #adjustment = label.get_parent().set_vadjustment(adjustment)
            
            if button_id != RESET_ERROR_COUNT_BUTTON_ID:
                # No need to track RESET_ERROR_COUNT_BUTTON_ID because it doesn't affect the log view
                button_id_prev = button_id
                
            button_id = self.dialog.run()

            if button_id == CLEAR_CACHE_BUTTON_ID:
                command_util.clear_cache()
                self.main_controller.on_progress_bar_update(None)
            elif button_id == RESET_ERROR_COUNT_BUTTON_ID:
                self.main_controller.invalidate_error_offset()
            elif button_id == Gtk.ResponseType.CLOSE or button_id == Gtk.ResponseType.DELETE_EVENT:
                break
            
    def destroy(self):
        #if self.dialog is not None:
        self.dialog.destroy()
