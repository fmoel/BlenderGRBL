# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Frank Moelendoerp

bl_info = {
    "name" : "Blender GRBL",
    "author" : "Frank Moelendoerp",
    "description" : "",
    "blender" : (3, 4, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import subprocess
import bpy
import sys, os
import addon_utils
import shutil


# check if pyserial is installed, otherwise install it
try:
    import serial
except:
    print("install pyserial")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])    
    import serial

def install_console_gcode(): 
    print("install console_gcode and globalstorage")
    module_path = os.path.join(bpy.utils.resource_path('USER'), "scripts", "modules")

    addon_path = ""
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == bl_info["name"]:
            addon_path = os.path.dirname(mod.__file__)
            break
    console_gcode_py = os.path.join(addon_path, "console_gcode.py")
    globalstorage_py = os.path.join(addon_path, "globalstorage.py")
    shutil.copy2(console_gcode_py, module_path)
    shutil.copy2(globalstorage_py, module_path)

install_console_gcode()

# check if gcode console is installed, otherwise install it.
try:
    import console_gcode
    import globalstorage
except:
    install_console_gcode()
    import console_gcode
    import globalstorage

# will not be loaded, if all consoles are switched to Gcode. So load it always.
import console_python 

from . import (
    ui,
    operators,
    settings_operator,
    utils,
    visualization_operators,
)


from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.app.handlers import persistent

def set_spindle_on_off(self, value):
    global storage
    storage["spindle_on_off"] = not storage["spindle_on_off"]
    try:
        bpy.ops.grbl.set_spindle_on_off()
    except:
        pass # may fail if not connected

def get_spindle_on_off(self):
    global storage
    return storage["spindle_on_off"]

def set_work_coordinates(self, value):
    global storage
    storage["work_coordinates_idx"] = value
    #workaround EnumProperty: set/get uses index while property uses value
    storage["work_coordinates"] = bpy.context.window_manager.grbl_control.work_coordinates
    try:
        bpy.ops.grbl.send_work_coordinates()
    except:
        pass # may fail if not connected

def get_work_coordinates(self):
    global storage
    return storage["work_coordinates_idx"]

def get_stream_algorithm(self): 
    return storage["stream_algorithm_idx"]

def set_stream_algorithm(self, val): 
    storage["stream_algorithm_idx"] = val

def set_cam_active_operations(self, val):
    storage["cam_active_operation"] = val
    bpy.ops.grbl.create_cutter_object('INVOKE_DEFAULT')

storage = globalstorage.GlobalStorage.instance()
storage.keys_to_save += ["connectionPort", "connectionBaudrate", "console_log_len", "step_size", "feedrate", 
                        "spindle_speed", "stream_algorithm", 
                        "user_command_name1", "user_command_icon1", "user_command_text1", 
                        "user_command_name2", "user_command_icon2", "user_command_text2", 
                        "user_command_name3", "user_command_icon3", "user_command_text3", 
                        "user_command_name4", "user_command_icon4", "user_command_text4", 
                        "copyMillingEndLoc_name", "working_coords_show", "working_coords_display_as",
                        "working_coords_size", "working_coords_xray", "G54", "G55", "G56", "G57", 
                        "G58", "G59"]

storage_defaults = {
    "milling_progress": 0,
    "milling_line_count": 0,
    "milling_current_line": 0,
    "is_milling": False,
    "cam_active_operation": -1,
    "connectionPort_idx": 0,
    "connectionEstablished": False,
    "connectionBaudrate": 115200,
    "console_command": "",
    "console_log": [],
    "machine_state": "unconnected",
    "current_machine_x": 0.0,
    "current_machine_y": 0.0,
    "current_machine_z": 0.0,
    "work_machine_x": 0.0,
    "work_machine_y": 0.0,
    "work_machine_z": 0.0,
    "operation_area_x": 0.0,
    "operation_area_y": 0.0,
    "operation_area_z": 0.0,
    "step_size": 10.0,
    "feedrate": 500,
    "spindle_speed": 10000,
    "spindle_on_off": False,
    "last_response": "",
    "work_coordinates_idx": 0,
    "work_coordinates": "G54",
    "stream_algorithm_idx": 0,
    "user_command_name1": "Empty Slot",
    "user_command_text1": "",
    "user_command_icon1": "USER",
    "user_command_name2": "Empty Slot",
    "user_command_text2": "",
    "user_command_icon2": "USER",
    "user_command_name3": "Empty Slot",
    "user_command_text3": "",
    "user_command_icon3": "USER",
    "user_command_name4": "Empty Slot",
    "user_command_text4": "",
    "user_command_icon4": "USER",
    "copyMillingEndLoc_name": "",
    "G54": (0.0, 0.0, 0.0),
    "G55": (0.0, 0.0, 0.0),
    "G56": (0.0, 0.0, 0.0),
    "G57": (0.0, 0.0, 0.0),
    "G58": (0.0, 0.0, 0.0),
    "G59": (0.0, 0.0, 0.0),
    "machine_zero": (0.0, 0.0, 0.0),
    "working_coords_show": True,
    "working_coords_display_as_idx": 2,
    "working_coords_size": 0.020,
    "working_coords_xray": True,
}
storage.update(storage_defaults)
storage.load()
bpy.storage = storage

class SceneProperties(PropertyGroup):
    milling_progress: FloatProperty(name="Progress", subtype="PERCENTAGE",soft_min=0, soft_max=100, precision=0, 
                                    get=lambda self: storage["milling_progress"], 
                                    set=lambda self, val: storage.set("milling_progress", val)) # type: ignore
    milling_line_count: bpy.props.IntProperty(name="milling_line_count", description="line count in gcode", 
                                    get=lambda self: storage["milling_line_count"], 
                                    set=lambda self, val: storage.set("milling_line_count", val)) # type: ignore
    milling_current_line: bpy.props.IntProperty(name="milling_current_line", description="current line in gcode", 
                                    get=lambda self: storage["milling_current_line"], 
                                    set=lambda self, val: storage.set("milling_current_line", val)) # type: ignore
    is_milling: bpy.props.BoolProperty(name="is_milling", description="is milling", 
                                    get=lambda self: storage["is_milling"], 
                                    set=lambda self, val: storage.set("is_milling", val)) # type: ignore
    cam_active_operation: bpy.props.IntProperty(name="cam active operation", description="active operation in chain", 
                                    get=lambda self: storage["cam_active_operation"], 
                                    set=set_cam_active_operations) # type: ignore
    connectionPort: EnumProperty(name="Port", description="Port to connect to CNC", items=utils.port_list_callback, 
                                    get=lambda self: storage["connectionPort_idx"], 
                                    set=lambda self, val: storage.set("connectionPort_idx", val)) # type: ignore
    connectionEstablished: BoolProperty(name="connection established", description="connection established", 
                                    get=lambda self: storage["connectionEstablished"], 
                                    set=lambda self, val: storage.set("connectionEstablished", val)) # type: ignore
    connectionBaudrate: IntProperty(name="Baudrate", description="Baud rate for port to connect to CNC", 
                                    get=lambda self: storage["connectionBaudrate"], 
                                    set=lambda self, val: storage.set("connectionBaudrate", val)) # type: ignore
    machine_state: StringProperty(name="Machine state", description="State of machine reported via the connection", 
                                    get=lambda self: storage["machine_state"], 
                                    set=lambda self, val: storage.set("machine_state", val)) # type: ignore
    current_machine_x: FloatProperty(name="X", description="Current x position of the machine", 
                                    get=lambda self: storage["current_machine_x"], 
                                    set=lambda self, val: storage.set("current_machine_x", val)) # type: ignore
    current_machine_y: FloatProperty(name="Y", description="Current y position of the machine", 
                                    get=lambda self: storage["current_machine_y"], 
                                    set=lambda self, val: storage.set("current_machine_y", val)) # type: ignore
    current_machine_z: FloatProperty(name="Z", description="Current z position of the machine", 
                                    get=lambda self: storage["current_machine_z"], 
                                    set=lambda self, val: storage.set("current_machine_z", val)) # type: ignore
    work_machine_x: FloatProperty(name="work X", description="Current x work position of the machine", 
                                    get=lambda self: storage["work_machine_x"], 
                                    set=lambda self, val: storage.set("work_machine_x", val)) # type: ignore
    work_machine_y: FloatProperty(name="work Y", description="Current y work position of the machine", 
                                    get=lambda self: storage["work_machine_y"], 
                                    set=lambda self, val: storage.set("work_machine_y", val)) # type: ignore
    work_machine_z: FloatProperty(name="work Z", description="Current z work position of the machine", 
                                    get=lambda self: storage["work_machine_z"], 
                                    set=lambda self, val: storage.set("work_machine_z", val)) # type: ignore
    operation_area_x: FloatProperty(name="X", description="Operation Area Width (X)", subtype='DISTANCE', min=0, max=10000.0, 
                                    get=lambda self: storage["operation_area_x"], 
                                    set=lambda self, val: storage.set("operation_area_x", val)) # type: ignore
    operation_area_y: FloatProperty(name="Depth", description="Operation Area Depth (Y)", subtype='DISTANCE', min=0, max=10000.0, 
                                    get=lambda self: storage["operation_area_y"], 
                                    set=lambda self, val: storage.set("operation_area_y", val)) # type: ignore
    operation_area_z: FloatProperty(name="Height", description="Operation Area Height (Z)", subtype='DISTANCE', min=0, max=10000.0, 
                                    get=lambda self: storage["operation_area_z"], 
                                    set=lambda self, val: storage.set("operation_area_z", val)) # type: ignore
    step_size: FloatProperty(name="Step Size", description="Step size for manual positiong", min=0, max=10000.0, 
                                    get=lambda self: storage["step_size"], 
                                    set=lambda self, val: storage.set("step_size", val)) # type: ignore
    feedrate: FloatProperty(name="Feed rate", description="Feedrate for manual positiong", min=0.1, max=100000.0, 
                                    get=lambda self: storage["feedrate"], 
                                    set=lambda self, val: storage.set("feedrate", val)) # type: ignore
    spindle_speed: FloatProperty(name="Spindle speed", description="spindle speed in rpm", min=0.1, max=100000.0, 
                                    get=lambda self: storage["spindle_speed"], 
                                    set=lambda self, val: storage.set("spindle_speed", val)) # type: ignore
    spindle_on_off: BoolProperty(name="Spindle on/off", description="spindle on/off", get=get_spindle_on_off, set=set_spindle_on_off) # type: ignore
    last_response: StringProperty(name="last response", description="last reponse from CNC", 
                                    get=lambda self: storage["last_response"], 
                                    set=lambda self, val: storage.set("last_response", val)) # type: ignore
    work_coordinates: EnumProperty(name = "Work Coords", description = "active work coordinates",
        items = [
            ("G54" , "G54" , "Activate G54 as active work coordinate system"),
            ("G55" , "G55" , "Activate G55 as active work coordinate system"),
            ("G56" , "G56" , "Activate G56 as active work coordinate system"),
            ("G57" , "G57" , "Activate G57 as active work coordinate system"),
            ("G58" , "G58" , "Activate G58 as active work coordinate system"),
            ("G59" , "G59" , "Activate G59 as active work coordinate system"),
        ],
        get=get_work_coordinates, set=set_work_coordinates,
    ) # type: ignore
    stream_algorithm: EnumProperty(name = "stream_algorithm", description = "Algorithm used for streaming the data",
        items = [
            ("line_by_line" , "Line by line" , "Sends one line, wait for GRBL to process it and send the next one"),
            ("use_buffer" , "Use buffer" , "Use the GRBL UART buffer to make the operation more robust"),
            ("flow_control" , "Flow control" , "Use hardware handshakes to get the status of the buffer. Not implemented right now. (Fallback to use_buffer)"),
        ], 
        get=get_stream_algorithm, set=set_stream_algorithm) # type: ignore
    user_command_name1: StringProperty(name="User cmd 1 Name", description="User gcode that can be run via the button 'user command 1'", 
                                    get=lambda self: storage["user_command_name1"], 
                                    set=lambda self, val: storage.set("user_command_name1", val)) # type: ignore
    user_command_text1: StringProperty(name="User cmd 1 Text", description="User gcode that can be run via the button 'user command 1'", 
                                    get=lambda self: storage["user_command_text1"], 
                                    set=lambda self, val: storage.set("user_command_text1", val)) # type: ignore
    user_command_icon1: StringProperty(name="User cmd 1 Icon", description="User gcode that can be run via the button 'user command 1'", 
                                    get=lambda self: storage["user_command_icon1"], 
                                    set=lambda self, val: storage.set("user_command_icon1", val)) # type: ignore
    user_command_name2: StringProperty(name="User cmd 2 Name", description="User gcode that can be run via the button 'user command 2'", 
                                    get=lambda self: storage["user_command_name2"], 
                                    set=lambda self, val: storage.set("user_command_name2", val)) # type: ignore
    user_command_text2: StringProperty(name="User cmd 2 Text", description="User gcode that can be run via the button 'user command 2'", 
                                    get=lambda self: storage["user_command_text2"], 
                                    set=lambda self, val: storage.set("user_command_text2", val)) # type: ignore
    user_command_icon2: StringProperty(name="User cmd 2 Icon", description="User gcode that can be run via the button 'user command 2'", 
                                    get=lambda self: storage["user_command_icon2"], 
                                    set=lambda self, val: storage.set("user_command_icon2", val)) # type: ignore
    user_command_name3: StringProperty(name="User cmd 3 Name", description="User gcode that can be run via the button 'user command 3'", 
                                    get=lambda self: storage["user_command_name3"], 
                                    set=lambda self, val: storage.set("user_command_name3", val)) # type: ignore
    user_command_text3: StringProperty(name="User cmd 3 Text", description="User gcode that can be run via the button 'user command 3'", 
                                    get=lambda self: storage["user_command_text3"], 
                                    set=lambda self, val: storage.set("user_command_text3", val)) # type: ignore
    user_command_icon3: StringProperty(name="User cmd 3 Icon", description="User gcode that can be run via the button 'user command 3'", 
                                    get=lambda self: storage["user_command_icon3"], 
                                    set=lambda self, val: storage.set("user_command_icon3", val)) # type: ignore
    user_command_name4: StringProperty(name="User cmd 4 Name", description="User gcode that can be run via the button 'user command 4'", 
                                    get=lambda self: storage["user_command_name4"], 
                                    set=lambda self, val: storage.set("user_command_name4", val)) # type: ignore
    user_command_text4: StringProperty(name="User cmd 4 Text", description="User gcode that can be run via the button 'user command 4'", 
                                    get=lambda self: storage["user_command_text4"], 
                                    set=lambda self, val: storage.set("user_command_text4", val)) # type: ignore
    user_command_icon4: StringProperty(name="User cmd 4 Icon", description="User gcode that can be run via the button 'user command 4'", 
                                    get=lambda self: storage["user_command_icon4"], 
                                    set=lambda self, val: storage.set("user_command_icon4", val)) # type: ignore
    copyMillingEndLoc: PointerProperty( name="Copy milling end location", type=bpy.types.Object,
                                    description="Copy the milling end location to this object. an be used to animate the complete CNC machine",            
                                    ) # type: ignore
    working_coords_display_as: EnumProperty(name="Working coords display as", description="How the working coords will be displayed", items=utils.empty_display_as_items,
                                    get=lambda self: storage["working_coords_display_as_idx"], 
                                    set=lambda self, val: storage.set("working_coords_display_as_idx", val)) # type: ignore
    working_coords_show: BoolProperty(name="working coords show", description="Should the working coords be displayed", 
                                    get=lambda self: storage["working_coords_show"], 
                                    set=lambda self, val: storage.set("working_coords_show", val)) # type: ignore
    working_coords_size: FloatProperty(name="Working coords size", description="Which size the working coords will be displayed", 
                                    get=lambda self: storage["working_coords_size"], 
                                    set=lambda self, val: storage.set("working_coords_size", val)) # type: ignore
    working_coords_xray: BoolProperty(name="working coords xray", description="Should the working coords be always visible, also through objects", 
                                    get=lambda self: storage["working_coords_xray"], 
                                    set=lambda self, val: storage.set("working_coords_xray", val)) # type: ignore
    
classes = (
    SceneProperties,

    ui.GRBLCONTROL_PT_general,
    ui.GRBLCONTROL_PT_Control,
    ui.GRBLCONTROL_PT_Milling,
    operators.GRBLCONTROL_PT_connect,
    operators.GRBLCONTROL_PT_disconnect,
    operators.GRBLCONTROL_PT_DirveHome,
    operators.GRBLCONTROL_PT_Reset,
    operators.GRBLCONTROL_PT_Unlock,
    operators.GRBLCONTROL_PT_set_x_zero,
    operators.GRBLCONTROL_PT_set_y_zero,
    operators.GRBLCONTROL_PT_set_z_zero,
    operators.GRBLCONTROL_PT_set_xy_zero,
    operators.GRBLCONTROL_PT_set_xyz_zero,
    operators.GRBLCONTROL_nothing,
    operators.GRBLCONTROL_PT_move_positive_x,
    operators.GRBLCONTROL_PT_move_negative_x,
    operators.GRBLCONTROL_PT_move_positive_y,
    operators.GRBLCONTROL_PT_move_negative_y,
    operators.GRBLCONTROL_PT_move_positive_z,
    operators.GRBLCONTROL_PT_move_negative_z,
    operators.GRBLCONTROL_PT_feed_hold,
    operators.GRBLCONTROL_PT_resume_feed,
    operators.GRBLCONTROL_PT_send_console_command,
    operators.GRBLCONTROL_PT_send_work_coordinates,
    operators.GRBLCONTROL_PT_milling_blender_cam,
    operators.GRBLCONTROL_PT_set_spindle_on_off,
    operators.GRBLCONTROL_PT_execute_user_command_1,
    operators.GRBLCONTROL_PT_execute_user_command_2,
    operators.GRBLCONTROL_PT_execute_user_command_3,
    operators.GRBLCONTROL_PT_execute_user_command_4,
    operators.GRBLCONTROL_PT_drive_to_cursor_coords,
    operators.GRBLCONTROL_PT_drive_to_vertex_coords,
    settings_operator.GRBLCONTROL_OT_settings,
    visualization_operators.GRBLCONTROL_PT_create_cutter_object,
    visualization_operators.GRBLCONTROL_PT_create_or_update_working_coords_emptys,
)

@persistent
def load_handler_create_cutter(dummy, dummy1):
    bpy.ops.grbl.create_cutter_object('INVOKE_DEFAULT')
    bpy.ops.grbl.create_or_update_working_coords_emptys('INVOKE_DEFAULT')
    grbl_control = bpy.context.window_manager.grbl_control
    if storage["copyMillingEndLoc_name"] != "":
        grbl_control.copyMillingEndLoc = bpy.data.objects[storage["copyMillingEndLoc_name"]]

def register():
    try:
        operators.GRBLCONTROL_PT_execute_user_command_1.bl_label = storage["user_command_name1"]
        operators.GRBLCONTROL_PT_execute_user_command_2.bl_label = storage["user_command_name2"]
        operators.GRBLCONTROL_PT_execute_user_command_3.bl_label = storage["user_command_name3"]
        operators.GRBLCONTROL_PT_execute_user_command_4.bl_label = storage["user_command_name4"]
    except:
        pass # maybe not stored etc...

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.grbl_control = PointerProperty(type=SceneProperties)
    grbl_control = bpy.context.window_manager.grbl_control
    storage.restoreObject(grbl_control)

    bpy.app.handlers.load_post.append(load_handler_create_cutter)

def unregister():
    if bpy.context.window_manager.grbl_control.connectionEstablished:
        bpy.ops.grbl.disconnect()
    
    storage.saveObject(bpy.context.window_manager.grbl_control)
    storage.save()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.grbl_control

    bpy.app.handlers.load_post.remove(load_handler_create_cutter)
