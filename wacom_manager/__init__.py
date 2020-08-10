#
# Author: Leonardo Robol <leo@robol.it>
#

import gi, gettext

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

_ = gettext.gettext

from .windows import MainWindow

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
    has_indicator = True
except:
    has_indicator = False

def start(options):
    if has_indicator:
        from .indicator import WacomManagerIndicator
        indicator = WacomManagerIndicator(options.quiet)
    else:
        window = MainWindow()

    Gtk.main()


    
