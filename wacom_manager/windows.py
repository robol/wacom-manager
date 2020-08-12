#!/usr/bin/env python3

import gi, subprocess, os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

from .wacom import WacomManager, WacomTablet
from .log import getLogger
from .config import getConfig
from . import _

logger = getLogger()

def get_builder_for(ui_name):
    """Construct a Gtk.Builder object that automatically
    loads the given UI file."""

    builder = Gtk.Builder()

    # We first look into the directory ../ui given the
    # path to this file, which is where the file would
    # be located when running from the source repository.
    module_path = os.path.dirname(os.path.realpath(__file__))
    local_file = os.path.join(module_path, "..", "ui", ui_name)

    if os.path.exists(local_file):
        logger.info('Added UI definition from %s' % local_file)
        builder.add_from_file(local_file)
    else:
        ui_path = os.path.join(
            "/usr/share/wacom-manager/ui", ui_name
        )
        logger.info('Trying to open UI from %s' % ui_path)
        builder.add_from_file(ui_path)

    return builder

class MainWindow(GObject.GObject):

    def __init__(self, app, has_indicator = False):
        GObject.GObject.__init__(self)

        self._app = app

        self._has_indicator = has_indicator
        self._builder = get_builder_for("main-window.ui")
        self._load_widgets()
        self._connect_callbacks()
        self._init_widgets()

        self.set_status(_("Wacom Manager 0.1 started"))

        self._app.manager.connect('tablets_changed',
                                  self._refresh_tablets)

    def show(self):
        self._window.show_all()
        self._refresh_tablets()

    def present(self):
        self._window.present()

    def window(self):
        return self._window

    def hide(self, widget = None, x = None):
        self._window.hide()

        # This is just to stop delete-event chaining
        # with the rest of the system
        return True

    def _init_widgets(self):
        self._refresh_tablets()

        config = getConfig()
        self._start_at_boot_checkbutton.set_active(
            config.get_start_at_boot()
        )

    def get_active_device(self):
        id = self._wacom_selector.get_active_id()

        for device in self._devices:
            if device.id == id:
                return device

        return None

    @GObject.Signal
    def tablet_changed(self):
        pass

    def _refresh_tablets(self, *args):
        self._devices = self._app.manager.find_devices()
        self._wacom_selector.remove_all()

        if len(self._devices) == 0:
            self._wacom_selector.append("0", _("No tablet detected"))
            self._wacom_selector.set_active_id("0")
            self.emit('tablet_changed')
        else:
            oldid = self._wacom_selector.get_active_id()

            for device in self._devices:
                self._wacom_selector.append(device.id, device.name)

            if not oldid in [ device.id for device in self._devices ]:
                self._wacom_selector.set_active_id(self._devices[0].id)
                self._on_device_changed()

        have_tablets = len(self._devices) != 0

        self._wacom_selector.set_sensitive(have_tablets)
        self._rapid_actions_frame.set_sensitive(have_tablets)

    def _load_widgets(self):
        # List of widgets to load using Gtk.Builder, which are
        # automatically mapped to members of this object prepending
        # a _ symbol. That is, "window" -> self._window.
        widgets =  [
            "window", "select_window_button",
            "wacom_selector", "rapid_actions_frame",
            "rotation_combobox", "map_to_window_info_button",
            "rotation_info_button", "start_at_boot_checkbutton",
            "status_label"
        ]

        for w in widgets:
            setattr(self, '_%s' % w, self._builder.get_object(w))

    def _connect_callbacks(self):
        if self._has_indicator:
            self._window.connect("delete-event", self.hide)
            self._window.connect("destroy", lambda x : True)
        else:
            self._window.connect("destroy", lambda x : self._app.quit())

        self._select_window_button.connect("clicked",
                                           self.on_select_window_clicked)
        self._map_to_window_info_button.connect("clicked",
                self._on_map_to_window_info_clicked)
        self._rotation_info_button.connect("clicked",
                self._on_rotation_info_button_clicked)
        self._rotation_combobox.connect("changed",
                                        self._on_rotation_changed)

        self._start_at_boot_checkbutton.connect("toggled",
                                                self._on_start_at_boot_toggled)

    def _on_map_to_window_info_clicked(self, *args):
        self._show_info_message('Map To Window',
            _("Map to Window allows to restrict the area spanned by the pointer to a region of the screen, identified by a given window."))

    def _on_rotation_info_button_clicked(self, *args):
        self._show_info_message('Rotation',
            _("Set the rotation for the tablet."))

    def _show_info_message(self, title, msg):
        dialog = Gtk.MessageDialog(
            self._window,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            msg
        )

        dialog.run()
        dialog.destroy()

    def set_status(self, status):
        self._status_label.set_text(status)

    def _on_device_changed(self, widget = None):
        device = self.get_active_device()
        self.emit('tablet_changed')

        if device:
            # Set the current rotation in the combobox
            self._rotation_combobox.set_active_id(device.get_rotation())

    def _on_start_at_boot_toggled(self, widget = None):
        config = getConfig()
        config.set_start_at_boot(self._start_at_boot_checkbutton.get_active())

    def on_select_window_clicked(self, button = None):
        # We need to make the user selects a valid window
        p = subprocess.Popen("xwininfo", shell = True,
                             stdout = subprocess.PIPE)
        output = p.communicate()[0].decode("utf-8")

        for line in output.split("\n"):
            if "Absolute upper-left X:" in line:
                xcorner = int(line.split(":")[1].strip())
            elif "Absolute upper-left Y:" in line:
                ycorner = int(line.split(":")[1].strip())
            elif "Width:" in line:
                width = int(line.split(":")[1].strip())
            elif "Height:" in line:
                height = int(line.split(":")[1].strip())

        geometry = "%dx%d+%d+%d" % (width, height, xcorner, ycorner)

        device = self.get_active_device()
        if device:
            device.set_geometry(geometry)
            self.set_status("Set geometry to %s" % geometry)

    def _on_rotation_changed(self, widget = None):
        rot = self._rotation_combobox.get_active_id()

        if rot:
            device = self.get_active_device()
            device.set_rotation(rot)
