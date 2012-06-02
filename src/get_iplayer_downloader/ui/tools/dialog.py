from gi.repository import Gtk

class ExtendedMessageDialog(Gtk.MessageDialog):
    """ A message dialog with a third scrollable text widget. """
    
    #NOTE Subclassing a convenience class, a class not always suited for that purpose
    def __init__(self,
                 parent,
                 flags,
                 message_type,
                 buttons,
                 message_format,
                 **keywords):
        #super(MessageDialog, self).__init__(parent=parent, ...
        Gtk.MessageDialog.__init__(self,
                               parent=parent,
                               flags=flags,
                               message_type=message_type,
                               buttons=buttons,
                               message_format=message_format,
                               **keywords)
        
        # Creating a secondary text makes the"primary" text appear in a large bold font
        #self.format_secondary_text(process_output)
        self.format_secondary_text(" ")

        # Add text label with scrollbars
        
        content_area = self.get_content_area()
        scrolled_window = Gtk.ScrolledWindow(expand=True)
        content_area.add(scrolled_window)

        self.scrolled_label = Gtk.Label(None)
        scrolled_window.add_with_viewport(self.scrolled_label)

        #self.show_all()
        scrolled_window.show_all()

    def get_scrolled_label(self):
        return self.scrolled_label
    
    def format_tertiary_scrolled_text(self, message_format):
        self.scrolled_label.set_text(message_format)

    def format_tertiary_scrolled_markup(self, message_format):
        self.scrolled_label.set_markup(message_format)
