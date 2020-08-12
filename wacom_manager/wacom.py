#
# Author: Leonardo Robol <leo@robol.it>
#

import subprocess, gi

gi.require_version('GObject', '2.0')
gi.require_version('GUdev', '1.0')

from gi.repository import GObject, GUdev

class WacomError(Exception):
    pass

def run_xsetwacom(args):
    p = subprocess.Popen([ "xsetwacom" ] + args,
                         stdout = subprocess.PIPE)
    output = p.communicate()[0].decode('utf-8')
    
    if p.wait() != 0:
        raise WacomError("Error while running xsetwacom with args: %s" % str(args))
    else:
        return output.strip()

class WacomManager(GObject.GObject):

    def __init__(self):
        GObject.GObject.__init__(self)
        self._xsetwacom = "xsetwacom"
        self._setup_observer()

    def find_devices(self):
        devices = []
        
        for line in run_xsetwacom([ "--list", "devices" ]).split("\n"):
            # We need to detect Stylus only at this stage
            if "STYLUS" in line:
                # Get the ID and the name
                pieces = line.split("\t")
                name = pieces[0]
                id   = pieces[1].split(":")[1].strip()

                devices.append(WacomTablet(id, name))
                
        return devices

    def _setup_observer(self):
        self._udev_client = GUdev.Client.new([ 'input' ])
        self._udev_client.connect('uevent', self._on_device_event)
        
    def _on_device_event(self, observer, action, device):
        self.emit('tablets_changed')

    @GObject.Signal
    def tablets_changed(self):
        pass
    

class WacomTablet():

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def set_geometry(self, geometry):
        print("Setting geometry: %s" % geometry)

        try:
            run_xsetwacom([ '--set', self.id, 'MapToOutput', geometry ])
        except WacomError as e:
            print(e)
            return False

        return True

    def set_rotation(self, rotation):
        if not rotation in [ "none", "half", "cw", "ccw" ]:
            raise WacomError("Invalid rotation mode specified")
        else:
            run_xsetwacom([ '--set', self.id, 'Rotate', rotation ])

        return True

    def get_rotation(self):
        return run_xsetwacom([ '--get', self.id, 'Rotate' ])

    def __str__(self):
        return "<Wacom Tablet %s (id = %s)>" % (self.name, self.id)
