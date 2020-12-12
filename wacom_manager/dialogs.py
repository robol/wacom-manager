#
#

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

class InfoDialog():

    def __init__(self, parent, title, msg):
        self._dialog = Gtk.MessageDialog(parent = parent,
            flags = Gtk.DialogFlags.MODAL,
            type = Gtk.MessageType.INFO,
            buttons = Gtk.ButtonsType.OK)

        self._dialog.set_markup(
            "<b>%s</b>\n\n%s" % (
                title, msg
            )
        )

    def show(self):
        self._dialog.show()

    def run(self):
        self._dialog.run()

    def destroy(self):
        self._dialog.destroy()
        
