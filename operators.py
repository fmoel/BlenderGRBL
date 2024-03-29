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

import bpy, bmesh
from bpy.types import Operator
from . import (
  communication,
)

import globalstorage

import serial
from os import access, R_OK
from os.path import isfile, join

storage = globalstorage.GlobalStorage.instance()

comm = communication.GRBLCONTROL_PT_communication()

def is_unlocked():
    return storage["machine_state"] != "Alarm"

def is_milling():
    return storage["is_milling"]

class GRBLCONTROL_PT_connect(Operator):
    bl_idname = "grbl.connect"
    bl_label = "Connect to the CNC maschine"
    bl_description = "Connect to the CNC maschine using the given connection settings."

    @classmethod
    def poll(cls, context):
        global comm
        return not comm.is_open()

    def execute(self, context):
        global comm
        try:
            comm.open()
        except serial.SerialException as e:            
            self.report({'ERROR'}, "Not able to connect to port")
            print(e)
        except ValueError as e:
            self.report({'ERROR'}, "Invalid baudrate or port configuration")

        return {'FINISHED'}
    
class GRBLCONTROL_PT_disconnect(Operator):
    bl_idname = "grbl.disconnect"
    bl_label = "Disconnect from the CNC maschine"
    bl_description = "Disconnect from the CNC maschine."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open()

    def execute(self, context):
        global comm
        comm.close()
        storage["connectionEstablished"] = False
        return {'FINISHED'}
    
class GRBLCONTROL_PT_DirveHome(Operator):
    bl_idname = "grbl.drive_home"
    bl_label = "Home"
    bl_description = "Send command to CNC for driving to home position"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open()

    def execute(self, context):
        global comm
        comm.write("$H")
        return {'FINISHED'}    
    
class GRBLCONTROL_PT_Reset(Operator):
    bl_idname = "grbl.reset"
    bl_label = "Soft Reset"
    bl_description = "Send command to reset CNC"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open()

    def execute(self, context):
        global comm
        storage["is_milling"] = False
        storage["milling_line_count"] = 0
        storage["milling_current_line"] = -1
        storage["milling_progress"] = 0
        comm.write("\030")
        comm.write("$#")
        return {'FINISHED'}    
    
class GRBLCONTROL_PT_Unlock(Operator):
    bl_idname = "grbl.unlock"
    bl_label = "Unlock"
    bl_description = "Send command to unlock CNC"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open()

    def execute(self, context):
        global comm
        comm.write("$X")
        comm.write("$#")
        return {'FINISHED'}    

def get_current_work_coord_point():
    match storage["work_coordinates"]:
        case "G54":
            return "1"
        case "G55":
            return "2"
        case "G56":
            return "3"
        case "G57":
            return "4"
        case "G58":
            return "5"
        case "G59":
            return "6"


class GRBLCONTROL_PT_set_x_zero(Operator):
    bl_idname = "grbl.set_x_zero"
    bl_label = "Set X to zero"
    bl_description = "Set X to zero"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        point = get_current_work_coord_point()
        comm.write("G10 L20 P" + point + "X0")
        comm.write("$#")
        return {'FINISHED'}    
    
class GRBLCONTROL_PT_set_y_zero(Operator):
    bl_idname = "grbl.set_y_zero"
    bl_label = "Set Y to zero"
    bl_description = "Set Y to zero"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        point = get_current_work_coord_point()
        comm.write("G10 L20 P" + point + "Y0")
        comm.write("$#")
        return {'FINISHED'}    
    
class GRBLCONTROL_PT_set_z_zero(Operator):
    bl_idname = "grbl.set_z_zero"
    bl_label = "Set Z to zero"
    bl_description = "Set Z to zero"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        point = get_current_work_coord_point()
        comm.write("G10 L20 P" + point + "Z0")
        comm.write("$#")
        return {'FINISHED'}        
    
class GRBLCONTROL_PT_set_xy_zero(Operator):
    bl_idname = "grbl.set_xy_zero"
    bl_label = "Set XY to zero"
    bl_description = "Set XY to zero"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        point = get_current_work_coord_point()
        comm.write("G10 L20 P" + point + "X0Y0")
        comm.write("$#")
        return {'FINISHED'}    
    
class GRBLCONTROL_PT_set_xyz_zero(Operator):
    bl_idname = "grbl.set_xyz_zero"
    bl_label = "Set XYZ to zero"
    bl_description = "Set XYZ to zero"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        point = get_current_work_coord_point()
        comm.write("G10 L20 P" + point + "X0Y0Z0")
        comm.write("$#")
        return {'FINISHED'}    
    
class GRBLCONTROL_nothing(Operator):
    bl_idname = "grbl.nothing"
    bl_label = "just do nothing"
    bl_description = "just do nothing"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        return {'FINISHED'}    
    
class GRBLCONTROL_PT_move_negative_x(Operator):
    bl_idname = "grbl.move_negative_x"
    bl_label = "Move negative X"
    bl_description = "Move relative negative X. Ctrl+click for a tenth of an increment."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):
        global comm
        step_size = storage["step_size"] / 10 if event.ctrl else storage["step_size"]
        toSend = "$J=G21G91X-" + str(step_size) + "F" + str(storage["feedrate"])
        comm.write(toSend)
        return {'FINISHED'}    

class GRBLCONTROL_PT_move_positive_x(Operator):
    bl_idname = "grbl.move_positive_x"
    bl_label = "Move positive X"
    bl_description = "Move relative positive X. Ctrl+click for a tenth of an increment."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):
        global comm
        step_size = storage["step_size"] / 10 if event.ctrl else storage["step_size"]
        toSend = "$J=G21G91X" + str(step_size) + "F" + str(storage["feedrate"])
        comm.write(toSend)
        return {'FINISHED'}    
    
class GRBLCONTROL_PT_move_negative_y(Operator):
    bl_idname = "grbl.move_negative_y"
    bl_label = "Move negative Y"
    bl_description = "Move relative negative Y. Ctrl+click for a tenth of an increment."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):
        global comm
        step_size = storage["step_size"] / 10 if event.ctrl else storage["step_size"]
        toSend = "$J=G21G91Y-" + str(step_size) + "F" + str(storage["feedrate"])
        comm.write(toSend) 
        return {'FINISHED'}  
    
class GRBLCONTROL_PT_move_positive_y(Operator):
    bl_idname = "grbl.move_positive_y"
    bl_label = "Move positive Y"
    bl_description = "Move relative positive Y. Ctrl+click for a tenth of an increment."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):
        global comm
        step_size = storage["step_size"] / 10 if event.ctrl else storage["step_size"]
        toSend = "$J=G21G91Y" + str(step_size) + "F" + str(storage["feedrate"])
        comm.write(toSend) 
        return {'FINISHED'}  
    
class GRBLCONTROL_PT_move_positive_z(Operator):
    bl_idname = "grbl.move_positive_z"
    bl_label = "Move positive Z"
    bl_description = "Move relative positive Z. Ctrl+click for a tenth of an increment."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):
        global comm
        step_size = storage["step_size"] / 10 if event.ctrl else storage["step_size"]
        toSend = "$J=G21G91Z" + str(step_size) + "F" + str(storage["feedrate"])
        comm.write(toSend) 
        return {'FINISHED'}  
    
class GRBLCONTROL_PT_move_negative_z(Operator):
    bl_idname = "grbl.move_negative_z"
    bl_label = "Move negitive Z"
    bl_description = "Move relative negitive Z. Ctrl+click for a tenth of an increment."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):
        global comm
        step_size = storage["step_size"] / 10 if event.ctrl else storage["step_size"]
        toSend = "$J=G21G91Z-" + str(step_size) + "F" + str(storage["feedrate"])
        comm.write(toSend) 
        return {'FINISHED'}      

class GRBLCONTROL_PT_feed_hold(Operator):
    bl_idname = "grbl.feed_hold"
    bl_label = "Stops motion. "
    bl_description = "In normal mode go in to hold mode. While jogging stop motion and clear the buffer."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked()

    def invoke(self, context, event):
        global comm
        comm.write("!") 
        return {'FINISHED'}
    
class GRBLCONTROL_PT_resume_feed(Operator):
    bl_idname = "grbl.resume_feed"
    bl_label = "Resume after stop motion."
    bl_description = "Resumes hold feed or saftey door/parking state."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked()

    def invoke(self, context, event):
        global comm
        comm.write("~") 
        return {'FINISHED'}         

class GRBLCONTROL_PT_send_console_command(Operator):
    bl_idname = "grbl.send_console_command"
    bl_label = "Send console command"
    bl_description = "Send console command"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and not is_milling()

    def invoke(self, context, event):
        global comm
        toSend = storage["console_command"]
        storage["console_command"] = ""
        comm.write(toSend) 
        return {'FINISHED'}      

class GRBLCONTROL_PT_update_console(Operator):
    bl_idname = "grbl.update_console"
    bl_label = "Update console"
    bl_description = "Update console"

    def invoke(self, context, event):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'CONSOLE':
                    storage["console_command"] = ""
        return {'FINISHED'}    

class GRBLCONTROL_PT_send_work_coordinates(Operator):
    bl_idname = "grbl.send_work_coordinates"
    bl_label = "Send work coordinte system"
    bl_description = "Send work coordinte system"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        toSend = storage["work_coordinates"]
        comm.write(toSend) 
        return {'FINISHED'}      
            
    def invoke(self, context, event):        
        return self.execute(context)
    

class GRBLCONTROL_PT_milling_blender_cam(Operator):
    bl_idname = "grbl.milling_blender_cam"
    bl_label = "Send selected BlenderCAM file to CNC"
    bl_description = "Send selected BlenderCAM file to CNC"

    @staticmethod
    def file_available():
        if bpy.context.scene.cam_operations is None:
            return False
        operation_index = storage["cam_active_operation"]
        if operation_index == -1:
            return False
        filename = join(bpy.path.abspath("//"), bpy.context.scene.cam_operations[operation_index].filename + ".gcode")
        try:
            assert isfile(filename) and access(filename, R_OK), f"File {filename} doesn't exist or isn't readable"
        except:
            return False
        return True

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling() and cls.file_available()

    def execute(self, context):
        global comm
        operation_index = storage["cam_active_operation"]
        filename = join(bpy.path.abspath("//"), bpy.context.scene.cam_operations[operation_index].filename + ".gcode")
        comm.send_file(filename) 
        return {'FINISHED'}      
            
    def invoke(self, context, event):        
        return self.execute(context)
    
class GRBLCONTROL_PT_set_spindle_on_off(Operator):
    bl_idname = "grbl.set_spindle_on_off"
    bl_label = "Set spindle on/off"
    bl_description = "Set spindle on/off"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        toSend = ""
        if storage["spindle_on_off"]:
            toSend = "M3 S" + str(storage["spindle_speed"])
        else:
            toSend = "M5"
        comm.write(toSend) 
        return {'FINISHED'}      
            
    def invoke(self, context, event):        
        return self.execute(context)

class GRBLCONTROL_PT_execute_user_command_1(Operator):
    bl_idname = "grbl.exec_usr_cmd_1"    
    bl_label = "Execute user Command 1"
    bl_description = "Execute user Command 1"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        toSend = storage["user_command_text1"]
        comm.write(toSend) 
        return {'FINISHED'}      
            
    def invoke(self, context, event):        
        return self.execute(context)

class GRBLCONTROL_PT_execute_user_command_2(Operator):
    bl_idname = "grbl.exec_usr_cmd_2"    
    bl_label = "Execute user Command 2"
    bl_description = "Execute user Command 2"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        toSend = storage["user_command_text2"]
        comm.write(toSend) 
        return {'FINISHED'}      
            
    def invoke(self, context, event):        
        return self.execute(context)

class GRBLCONTROL_PT_execute_user_command_3(Operator):
    bl_idname = "grbl.exec_usr_cmd_3"    
    bl_label = "Execute user Command 3"
    bl_description = "Execute user Command 3"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        toSend = storage["user_command_text3"]
        comm.write(toSend) 
        return {'FINISHED'}      
            
    def invoke(self, context, event):        
        return self.execute(context)

class GRBLCONTROL_PT_execute_user_command_4(Operator):
    bl_idname = "grbl.exec_usr_cmd_4"
    bl_label = "Execute user Command 4"
    bl_description = "Execute user Command 4"

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def execute(self, context):
        global comm
        toSend = storage["user_command_text4"]
        comm.write(toSend) 
        return {'FINISHED'}      
            
    def invoke(self, context, event):        
        return self.execute(context)

class GRBLCONTROL_PT_drive_to_cursor_coords(Operator):
    bl_idname = "grbl.drive_to_cursor_coords"
    bl_label = "Drive X/Y to blenders cursor (work-coords)"
    bl_description = "Drive X/Y to blenders cursor position using the work cooridinates. Press with shift to also include Z position."

    @classmethod
    def poll(cls, context):
        global comm
        return comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):        
        cursor = context.scene.cursor.location
        z = ""
        if event.shift:
            z = "Z" + "{:.3f}".format(cursor.z * 1000)
        toSend = "$J=X" + "{:.3f}".format(cursor.x * 1000) + "Y" + "{:.3f}".format(cursor.y * 1000) + z + "F" + str(storage["feedrate"])
        comm.write(toSend) 
        return {'FINISHED'}

class GRBLCONTROL_PT_drive_to_vertex_coords(Operator):
    bl_idname = "grbl.drive_to_vertex_coords"
    bl_label = "Drive X/Y to blenders cursor (vertex-coords)"
    bl_description = "Drive X/Y to active vertex position using the work cooridinates. Press with shift to also include Z position"

    @classmethod
    def poll(cls, context):
        global comm
        vertex_selected = False
        obj = bpy.context.object
        if obj is None or obj.mode != 'EDIT':
            return False
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        for elem in reversed(bm.select_history):
            if isinstance(elem, bmesh.types.BMVert):    
                vertex_selected = True
                break        
        return vertex_selected and comm.is_open() and is_unlocked() and not is_milling()

    def invoke(self, context, event):        
        vertex = None
        ob = bpy.context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)

        for elem in reversed(bm.select_history):
            if isinstance(elem, bmesh.types.BMVert):
                vertex = elem
                break            
        vertex_location = ob.matrix_world @ vertex.co
        z = ""
        if event.shift:
            z = "Z" + "{:.3f}".format(vertex_location.z * 1000)
        toSend = "$J=X" + "{:.3f}".format(vertex_location.x * 1000) + "Y" + "{:.3f}".format(vertex_location.y * 1000) + z + "F" + str(storage["feedrate"])
        comm.write(toSend) 
        return {'FINISHED'}
