#
# Author: Leonardo Robol <leo@robol.it
#

import gi

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from gi.repository import AppIndicator3, Gtk

from .windows import MainWindow
from . import _

class WacomManagerIndicator():

    def __init__(self):
        self._indicator = AppIndicator3.Indicator.new(
            "wacom-manager", "input-tablet",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        
        self._indicator.set_status(
            AppIndicator3.IndicatorStatus.ACTIVE
        )

        self._main_window = MainWindow(True)
        self._main_window.hide()

        self._create_menu()

        self._main_window.connect(
            'tablet_changed', self._update_tablet_name
        )
        
        self._menu.show_all()

    def _on_wacom_open_activated(self, widget = None):
        self._main_window.show()

    def _update_tablet_name(self, *args):
        device = self._main_window.get_active_device()
        label  = self._tablet_selected.get_children()[0]
        if device is None:
            label.set_text('No tablet selected')
        else:
            label.set_text(device.name)

    def _create_menu(self):
        self._menu = Gtk.Menu()

        self._tablet_selected = Gtk.MenuItem("")
        self._tablet_selected.set_sensitive(False)
        self._menu.append(self._tablet_selected)
        self._update_tablet_name()

        open_item = Gtk.MenuItem(_('Open Wacom Manager'))
        open_item.connect('activate',
                          self._on_wacom_open_activated)
        self._menu.append(open_item)

        select_area_item = Gtk.MenuItem(_('Map to Window'))
        select_area_item.connect('activate',
                                 self._main_window.on_select_window_clicked)
        self._menu.append(select_area_item)

        sep = Gtk.SeparatorMenuItem()
        self._menu.append(sep)

        close_item = Gtk.MenuItem(_('Quit'))
        close_item.connect('activate', Gtk.main_quit)
        self._menu.append(close_item)
        
        self._indicator.set_menu(self._menu)
