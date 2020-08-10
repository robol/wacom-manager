#!/usr/bin/env python3

import gi, subprocess, os
import gettext

_ = gettext.gettext

gi.require_version("Gtk", "3.0")
gi.require_version("GUdev", "1.0")

from gi.repository import Gtk, GUdev, GObject

from .wacom import WacomManager, WacomTablet
from .log import getLogger
from .config import getConfig

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

    def __init__(self, has_indicator = False):
        GObject.GObject.__init__(self)
        
        self.manager = WacomManager()
        self._has_indicator = has_indicator

        self._builder = get_builder_for("main-window.ui")
        self._load_widgets()
        self._connect_callbacks()
        self._init_widgets()
        self._window.show_all()
        
        self.set_status(_("Wacom Manager 0.1 started"))

        self._setup_observer()

    @GObject.Signal
    def tablet_changed(self, *args):
        pass

    def show(self):
        self._window.show_all()
        self._refresh_tablets()

    def hide(self, widget = None, x = None):
        self._window.hide()

        # This is just to stop delete-event chaining
        # with the rest of the system
        return True

    def _setup_observer(self):
        self._udev_client = GUdev.Client.new([ 'input' ])
        self._udev_client.connect('uevent', self._on_device_event)

    def _on_device_event(self, observer, action, device):
        self._refresh_tablets()

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

    def _refresh_tablets(self):
        self._devices = self.manager.find_devices()
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
        self._window = self._builder.get_object("window")

        # Widgets in the top tablet-selection part
        self._select_window_button = self._builder.get_object(
            "select_window_button"
        )
        self._wacom_selector = self._builder.get_object("wacom_selector")

        # Widgets in the tablet options part
        self._rapid_actions_frame = self._builder.get_object("rapid_actions_frame")
        self._rotation_combobox = self._builder.get_object("rotation_combobox")

        # Widgets in the preferences block
        self._start_at_boot_checkbutton = self._builder.get_object(
            "start_at_boot_checkbutton"
        )

        # Widget in the status bar
        self._status_label = self._builder.get_object("status_label")        

    def _connect_callbacks(self):
        if self._has_indicator:
            self._window.connect("delete-event", self.hide)
            self._window.connect("destroy", lambda x : True)
        else:
            self._window.connect("destroy", Gtk.main_quit)
            
        self._select_window_button.connect("clicked",
                                           self.on_select_window_clicked)
        self._rotation_combobox.connect("changed",
                                        self._on_rotation_changed)

        self._start_at_boot_checkbutton.connect("toggled",
                                                self._on_start_at_boot_toggled)

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
        # We need to make the user select a valid window
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

    def _on_rotation_changed(self, widget = None):
        rot = self._rotation_combobox.get_active_id()

        if rot:
            device = self.get_active_device()
            device.set_rotation(rot)

            
