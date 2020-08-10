#
# Author: Leonardo Robol <leo@robol.it>
#

import os, json

from .log import getLogger

logger = getLogger()

# Config version is incremented when we add new options, to allow
# to implement migrations between versions. 
config_version = 1

# Data to write in the autostart desktop file
AUTOSTART_DATA = r"""[Desktop Entry]
Name=Wacom Manager
Comment=Set options for Wacom Tablets
Exec=wacom-manager --quiet
Terminal=false
Type=Application
StartupNotify=true
Icon=it.robol.wacom-manager
Categories=Utility;
Keywords=Wacom;Settings;Utility
X-Ubuntu-Gettext-Domain=wacom_manager
"""

class ConfigError(Exception):
    pass

class Config():

    def __init__(self):
        self._check_directories()
        self._load_data()

    def _load_data(self):
        self._options = {
            'config_version': config_version
        }

        if os.path.exists(self._config_file):
            with open(self._config_file) as h:
                logger.info("Loading options from %s" % self._config_file)
                try:
                    self._options = json.load(h)
                    self._migrate(self._options.get('config_version', 0))
                except:
                    logger.warning("Options are invalid, default loaded")
        else:
            logger.info("Config file does not exist, loading default options")

    def _migrate(self, version = 0):
        if version <= 0:
            self._options['config_version'] = 1
            logger.info('Migration config from 0 to 1')
            self._save_options()

    def _get_autostart_desktop_path(self):
        autostart_path = os.path.join(
            os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
            "autostart"
        )

        if not os.path.exists(autostart_path):
            logger.warning('Autostart directory does not exist')
        else:
            return os.path.join(autostart_path,
                                "it.robol.wacom-manager.desktop")

    def get_start_at_boot(self):
        if 'start_at_boot' in self._options:
            return self._options['start_at_boot']
        else:
            return False

    def set_start_at_boot(self, value):
        self._options['start_at_boot'] = value
        autostart_path = self._get_autostart_desktop_path()

        if value:
            # Need to install the desktop file
            with open(autostart_path, "w") as h:
                h.write(AUTOSTART_DATA)
        else:
            if os.path.exists(autostart_path):
                try:
                    os.remove(autostart_path)
                except Exception(e):
                    logger.warning("Unable to remove autostart file:")
                    print(e)
                    
        
        self._save_options()

    def _save_options(self):
        with open(self._config_file, 'w') as h:
            json.dump(
                self._options,
                h,
                indent = True,
                sort_keys = True
            )

    def _check_directories(self):
        # Make sure that all directories where our
        # configuration is stored actually exist        
        config_directory = os.getenv('XDG_CONFIG_HOME')

        if config_directory is None:
            home_directory = os.getenv('HOME')
            config_directory = os.path.join(home_directory,
                                            '.config')

        config_directory = os.path.join(config_directory,
                                        'it.robol.wacom-manager')

        logger.info("Config directory: %s" % config_directory)

        # Try to create the config directory, if it does
        # not exist
        if not os.path.exists(config_directory):
            logger.info('Create config directory: %s' % config_directory)
            try:
                os.makedirs(config_directory)
            except:
                logger.error('Unable to create config directory!')
                raise ConfigException

        self._config_directory = config_directory
        self._config_file = os.path.join(self._config_directory,
                                         "config.json")
                


# Load a unique instance of the configuration for all the
# points in the application. 
config = Config()

def getConfig():
    return config
