#
# Author: Leonardo Robol <leo@robol.it
#

import gi

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from gi.repository import AppIndicator3, Gtk

from .windows import MainWindow
from . import _

class WacomManagerIndicator(AppIndicator3.Indicator):

    def __init__(self, app, quiet):
        self._indicator = AppIndicator3.Indicator.new(
            "wacom-manager", "input-tablet",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        
        self._indicator.set_status(
            AppIndicator3.IndicatorStatus.ACTIVE
        )
        
        self._app = app        

        self._menu = None
        self._create_menu()            
        self._menu.show_all()

        app.main_window.connect('tablet_changed',
                                self._update_tablet_name)

    def on_wacom_open_activated(self, widget = None):
        self._app.main_window.show()
        self._app.main_window.present()

    def _update_tablet_name(self, *args):
        device = self._app.main_window.get_active_device()
        label  = self._tablet_selected.get_children()[0]
        if device is None:
            label.set_text('No tablet detected')
            if self._menu is not None:
                self._select_area_item.set_sensitive(False)
        else:
            label.set_text(device.name)
            if self._menu is not None:
                self._select_area_item.set_sensitive(True)

    def _create_menu(self):
        self._menu = Gtk.Menu()

        self._tablet_selected = Gtk.MenuItem("")
        self._tablet_selected.set_sensitive(False)
        self._menu.append(self._tablet_selected)

        open_item = Gtk.MenuItem(_('Open Wacom Manager'))
        open_item.connect('activate',
                          self.on_wacom_open_activated)
        self._menu.append(open_item)

        self._select_area_item = Gtk.MenuItem(_('Map to Window'))
        self._select_area_item.connect('activate',
                                       self._app.main_window.on_select_window_clicked)
        self._menu.append(self._select_area_item)

        sep = Gtk.SeparatorMenuItem()
        self._menu.append(sep)

        close_item = Gtk.MenuItem(_('Quit'))
        close_item.connect('activate', lambda x : self._app.quit())
        self._menu.append(close_item)

        self._update_tablet_name()
        self._indicator.set_menu(self._menu)


