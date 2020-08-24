from distutils.core import setup

setup(
    name = 'wacom-manager',
    version = '0.2',
    packages = [ 'wacom_manager' ],
    scripts = [ 'wacom-manager' ],
    data_files = [
        ('share/wacom-manager/ui', [ 'ui/main-window.ui' ]),
        ('share/applications', [ 'it.robol.WacomManager.desktop' ]),
        ('share/icons/hicolor/48x48/apps', [ 'icons/48x48/it.robol.WacomManager.png' ]),
        ('share/icons/hicolor/128x128/apps', [ 'icons/128x128/it.robol.WacomManager.png' ]),
        ('share/icons/hicolor/256x256/apps', [ 'icons/256x256/it.robol.WacomManager.png' ])
    ]
)

# To build a deb file, assuming stdeb is installed:
#  python3 setup.py --command-packages=stdeb.command bdist_deb
