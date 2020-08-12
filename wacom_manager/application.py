#
# Author: Leonardo Robol <leo@robol.it>

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')

from gi.repository import Gtk, Gio

from .windows import MainWindow
from .wacom import WacomManager

# This code determines if the indicator API are
# available on the system (as on Ubuntu), or not.
try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
    has_indicator = True
except:
    has_indicator = False

class Application(Gtk.Application):

    def __init__(self, options):
        Gtk.Application.__init__(
            self,
            application_id = "it.robol.wacom-manager",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self._options = options

        # We register the main window in the do_activate
        # callback. 
        self._main_window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if self._main_window is None:
            self.manager = WacomManager()
            self.main_window = MainWindow(self, has_indicator)
            self.add_window(self.main_window.window())

            if has_indicator:
                from .indicator import WacomManagerIndicator
                self._indicator = WacomManagerIndicator(
                    self,
                    self._options.quiet
                )

            if not self._options.quiet:
                self.main_window.present()
        else:
            self.main_window.show()
            self.main_window.present()            
        
