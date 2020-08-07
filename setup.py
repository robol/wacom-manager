from distutils.core import setup

setup(
    name = 'wacom-manager',
    version = '0.1',
    packages = [ 'wacom_manager' ],
    scripts = [ 'wacom-manager' ],
    data_files = [
        ('share/wacom-manager/ui', [ 'ui/main-window.ui' ]),
        ('share/applications', [ 'it.robol.wacom-manager.desktop' ])
    ]
)

# To build a deb file, assuming stdeb is installed:
#  python3 setup.py --command-packages=stdeb.command bdist_deb
