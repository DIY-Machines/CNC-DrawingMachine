# MI-GRBL-Z-AXIS-Servo-Controller

### Overview
This plug-in allows for servo up or down.  Here is a description of the features of the plug-in.

***This version/branch of the plugin was written for Inkscape 1.0.2 and updated for Python3 changes. This version allows for use with newer versions of Inkscape which are compatible with newer system architechtures. It is recommended to use this version of the plugin or newer.***

* Servo down:  The command for move servo down.  For example, M03 or M106.
* Servo up: The command for move servo up.  For example, M05 or M107.
* X axis speed (mm/min):  The speed of the X axis mm/min.
* Y axis speed (mm/min):  The speed of the Y axis in mm/min.
* Angle for servo S# (0-180): If you have PWM control, then you can adjust this.  For J Tech firmware and most 3D printers use a number between 0 and 255 (255 being full power).  For GRBL 0.9 and 1 standard, use a number between 0 and 12000 (12000 being full power).   If you don’t have PWM, keep at max power (either 255 or 12000).
* Delay (s):  This will turn on the laser and wait to move until the delay is complete.  It is used to heat up the material and initiate the burning process.  Delay in ms for 3D printers and seconds for GRBL.
* Directory:  The directory to store the file.
Filename:  Name of the file.
* Add numeric suffix to filename:  Adds a number to the name in case there already is a file with the same name in the directory.
Live preview:  Shows the path being generated.
* Apply:  Click to run the gcode generator.


```
M3 S255     (turn servo full on)
M5          (turn servo off)
M3 S125     (turn servo half way)
M3 S0       (turn servo on full off - similar to M5)
```

### Installation

To manually install a new extension, download (from the releases section of this project) and unpack the `servo.inx` and `servo.py` files. Copy the files into the directory listed at `Edit` > `Preferences` > `System: User extensions`. After a restart of Inkscape, the new extension will be available.
