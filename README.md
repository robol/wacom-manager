# Wacom Manager

A simple utility to set options for a Wacom tablet in GNOME,
which are not available by the standard configuration dialog.

It only provides basic options, at the moment, as they are all I need.

![](https://raw.githubusercontent.com/robol/wacom-manager/master/documentation/demo-wacom-manager.gif)

# How to use

You can run the script directly from its folder; to accomplish that
on Ubuntu, you will need to install the required dependencies first
(note that appindicator is optional, but required to have the app
persist in the systray):
```
$ sudo apt install gir1.2-appindicator3-0.1
```
and then clone the repository and run the script
```
$ git clone https://github.com/robol/wacom-manager/
$ cd wacom; ./wacom-manager
```

If you install the packages ```python3-stdeb```, 
```python-all```, and ```descripts```, you will als be able to generate 
a Debian package to install, so that the software will appear in the Gnome Shell menu; if you have the above packages installed, run
```
$ python3 setup.py --command-packages=stdeb.command bdist_deb
```
and then install the package ```python3-wacom-manager_x.y-1_all.deb```
in the folder ```deb_dist```.

## Bug reports

Please report bugs and/or feature requests by opening an issue on Github.

## Limitations

Only works under X11 at the moment. This has only been tested under Ubuntu 20.04, although it should work on older versions as well.

