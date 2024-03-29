# BlenderGRBL
An addon for Blender to control CNC machines based on GRBL

![Picture of Blender with addon enabled](images/Overview.png?raw=true "Blender with Blender-GRBL enabled")

# Installation
Pre Requirements:

Blender 3.4+ with an installed version of BlenderCAM is required. BlenderCAM is currently not ported to 4.0. So there is no way to test this Addon with Blender 4.0.

- Download the zip file with the green "<> Code" button.
- Go in to Blender and open the Blender Preferences via the Edit -> Preferences... menu.
- Click on the "Install..." button
- Select the downloaded zip file
- Checkmark the newly added entry "Generic: Blender GRBL"

![Description on how to find install addon in Blender](images/Install.png?raw=true "Find install addon in Blender")

# Quickstart
Press "N" in the 3D-Space to show the toolbars on the right side. Here the tab "GBRL-Control" appears.  Use "Settings" to select the correct port and baud rate for your CNC machine. Press on connect to open the serial line.

## General panel
![General panel](images/General.png?raw=true "General panel")

The General panel has only three buttons. Mostly self explaining. Settings opens Settings dialog, Connect and Disconnected controls the connection to the CNC machine.
Connect and Disconnect using pyserial to connect to the serial port and baud rate declared in the Settings dialog.

## Settings dialog
![Settings](images/Settings.png?raw=true "Settings")

Port: is the serial port used to talk to the CNC machine
Baud Rate: is the speed used to talk to the CNC machine
Stream Algorithm:
- Line by Line [default]: The next command will be sent when the former was acknowledged by the CNC machine. This is absolutely safe, but is limited in transmission speed and can lead to stutter of the movement. Nearby impossible to lose chars.
- Use Buffer [recommended]: Using the buffer space of the GRBL controller of the CNC machine. Blender-GRBL takes care about the buffer of the GRBL controller of the CNC machine.
- Flow control: __currently not implemented__ Make use of hardware flow control. Normally the best possible solution. However, in practice there are a lot of problems with timing introduced by USB.

Then there are four blocks for User Commands, which are available in the control panel. Each consists of:
- Button Label: Will be shown as tool tip on mouse over
- GCode: Is the Gcode that will be send. (Currently single line, this means max 70 characters with GRBL 1.1 running on the CNC machine)
- Icon: Name of the ICON for the button in the control panel. A list can be found here: [Blendicons](https://wilkinson.graphics/blender-icons/) or in the development panel of Blender itself.

Animation
- Copy milling end location: Will copy the cutter location to another blender objet. Can be used to animate the CNC machine

Work Coordinates
- working coords show: Make the working coordinates stored in the machine visible
- Display as: Gives Blender options to show points in 3d space
- Size: the size of the coordinate object in meters
- Xray: If switched on, visible through objects

Clicking beside the díalog box or pressing ESC will cancel the transaction and the changes are omitted

## Control panel
![Control panel](images/Control.png?raw=true "Control panel")

The control panel has most of the operators. Starting with the first row of buttons:
- Home: Send the homing command to the CNC
- Reset: Send the Reset stroke to the CNC
- Unlock: Unlocks the CNC
- X/Y/Z zero: This three buttons set the work coordinates of to zero for the corresponding axis
- X-Y-Plane zero: Set the work coordinates for X- and Y-axis to zero
- XYZ-Zero: Set the work coordinates for all axis to zero

Below is the Working point selection. Selecting the working point send the corresponding command to the CNC and the work coordinates in the location section of the control panel get updated (only if connected and unlocked).

Next coming the movement area
- Four direction arrows: Clicking this buttons will drive the CNC __Step size__ millimeters with a speed __Feed rate__ mm/min in X or Y direction. Pressing __Shift__ reduces the __Step size__ to the tenth of it for a single move.
- Up/Down arrows: The same as above with Z
- Stop button: Feed hold. Interrupts the current Jogging

Beside the movement area there are six other buttons:
- Drive to cursor: Using Blender's cursor to set the destination position using the work coordinates.
- Drive to Vertex: Using the currently selected Vertex to set the destination position using the work coordinates.
- User buttons 1-4: Four buttons that can be assigned to a user specific GCode sequence in the settings dialog.

Values:
- Step size: Set the step size for the movement area in mm
- Feed rate: set the speed for the the movement area in mm/min
- Spindle speed: Set the speed of the spindle in RPM.
- Spindle on/off button: Switches the spindle on or off
 
## Milling panel
![Milling panel](images/Milling.png?raw=true "Title")

The first list shows available BlenderCAM operations. Select the one that should be send to the CNC machine. If the button __Send selected Blender file__ is not available, the GCode maybe missing. Go to the BlenderCAM panel and press __Calculate path & export Gcode__

Other buttons:
- Reset: __currently not implemented__ go to the first line of the Gcode file
- Play: Start/Continue the Gcode file
- Pause: Pause the Gcode file

![Picture of Blender with addon enabled](images/Milling%20with%20BlenderCAM%20enabled.png?raw=true "Blender with Blender-GRBL enabled")

## Console
![Console](images/Console.png?raw=true "Console")

Blender-GBRL comes with G Code console. To activate this change one area to __Python Console__ and switch the language as shown in the screenshot. To use the console, Blender-GBRL must be connected to the CNC machine - obviously. Blenders UI limits the response time. After 1 second a timeout will be shown. However, if the next line is just empty, it will prompt the rest of the message, if any.

![Open console](images/Open%20console.png?raw=true "Open console")

![Change the languages of the console](images/Languages_Gcode.png?raw=true "Change console language")

# Uninstall
Find the addon in Preference -> Addon and press remove. However, there are two files left in the system. Both don't hurt. It is _console_gcode.py_ and _globalstorage.py_ in the Blenders user folder _scripts/modules_. These files are required to be installed in a different way and cannot be removed automatically. If the addon is uninstalled, they will no longer be imported and with a restart of Blender they are no longer active. To completely uninstall the addon, these files must be deleted manually.