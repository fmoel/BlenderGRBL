# GRBL-Control
An addon for Blender to control CNC machines based on GRBL

![Picture of Blender with addon enabled](images/Milling%20with%20BlenderCAM%20enabled.png?raw=true "Blender with Blender-GRBL enabled")

# Installation
Prerequirements:
Blender 3.4+ with an installed version of BlenderCAM is required. BlenderCAM is currently not ported to 4.0. So there is no way to test this Addon with Blender 4.0.

- Download the zip file with the green "<> Code" button. 
- Go in to Blender and open the Blender Preferences via the Edit -> Preferences... menu.
- Click on the "Install..." button
- Select the downloaded zip file
- Checkmark the newly added entry "Generic: Blender GRBL"

![Description on how to find install addon in Blender](images/Install.png?raw=true "Find install addon in Blender")

# Quickstart
Press "N" in the 3D-Space to show the toolbars on the right side. Here the tab "GBRL-Control" apears.  Use "Settings" to select the correct port and baud rate for your CNC machine. Press on connect to open the serial line. 

## General panel
![Gneral panel](images/General.png?raw=true "General panel")
The General panel has only three buttons. Mostly self explaining. Settings opens Settings dialog, Connect and Disconnected controls the connection to the CNC machine.
Connect and Disconnect using pyserial to connect to the serial port and baud rate declared in the Settings dilalog.

## Settings dialog
![Settings](images/Settings.png?raw=true "Settings")
Port: is the serial port used to talk to the CNC machine
Baudrate: is the speed used to talk to the CNC machine
Stream Algorithm:
- Line by Line [default]: The next command will be send when the former was acknowledged by the CNC machine. This is absolute safe, but is limited in transmission speed and me lead to stutter of the movement. Nearby impossible to lose chars.
- Use Buffer [recommended]: Using the buffer space of the GRBL controller of the CNC machine. Blender-GRBL takes care about the buffer of the GRBL controller of the CNC machine.
- Flow control: Make use of hardware flow control. Normally the best possible soluion. However, in practice there are a lot of problems with timing introduced by USB.

## Control panel
![Control panel](images/control.png?raw=true "Control panel")
