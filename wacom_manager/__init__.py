#
# Author: Leonardo Robol <leo@robol.it>
#

import gettext
_ = gettext.gettext

from .application import Application

def start(options):
    app = Application(options)    
    app.run()


    
