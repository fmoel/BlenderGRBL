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

from bpy.types import Panel
import bpy

class View3DGRBLPanel:
    bl_category = "GRBL-Control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return True


class GRBLCONTROL_PT_general(View3DGRBLPanel, Panel):
    bl_label = "General"

    def draw(self, context):
        layout = self.layout


        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.operator("grbl.settings", text="Settings", icon="SETTINGS")

        row = layout.row(align=True)
        row.operator("grbl.connect", text="Connect", icon="LINKED")
        row.operator("grbl.disconnect", text="Disconnect", icon="UNLINKED")

class GRBLCONTROL_PT_Control(View3DGRBLPanel, Panel):
    bl_label = "Control"

    def draw(self, context):
        global storage
        layout = self.layout

        grbl_control = context.window_manager.grbl_control

        layout.enabled = grbl_control.connectionEstablished

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Status:")
        row.label(text=grbl_control.machine_state)

        row = col.row(align=True)
        row.operator("grbl.drive_home", text="", icon="HOME")
        row.operator("grbl.reset", text="", icon="REW")
        row.operator("grbl.unlock", text="", icon="UNLOCKED")
        row.operator("grbl.set_x_zero", text="", icon="EVENT_X")
        row.operator("grbl.set_y_zero", text="", icon="EVENT_Y")
        row.operator("grbl.set_z_zero", text="", icon="EVENT_Z")
        row.operator("grbl.set_xy_zero", text="", icon="AXIS_TOP")
        row.operator("grbl.set_xyz_zero", text="", icon="OBJECT_ORIGIN")

        col = layout.row()
        #col.props_enum(grbl_control, "work_coordinates")
        col.prop(grbl_control, "work_coordinates", expand=False, text="Work Coordinates")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("grbl.nothing", text="", icon="BLANK1")
        row.operator("grbl.move_positive_y", text="", icon="TRIA_UP")
        row.operator("grbl.nothing", text="", icon="BLANK1")
        row.operator("grbl.move_positive_z", text="", icon="SORT_DESC")
        row.label(text="")
        row.operator("grbl.drive_to_cursor_coords", text="", icon="ORIENTATION_CURSOR")
        row.operator("grbl.drive_to_vertex_coords", text="", icon="VERTEXSEL")
        #row.operator("grbl.nothing", text="", icon="TOOL_SETTINGS") # todo: machine settings "$$"
        #row.operator("grbl.nothing", text="", icon="CONSOLE") # todo: configure python console for console interaction wiht CNC
        row = col.row(align=True)
        row.operator("grbl.move_negative_x", text="", icon="TRIA_LEFT")
        row.operator("grbl.feed_hold", text="", icon="CANCEL")
        row.operator("grbl.move_positive_x", text="", icon="TRIA_RIGHT")
        row.operator("grbl.nothing", text="", icon="BLANK1")
        row.label()
        row.operator("grbl.exec_usr_cmd_1", text="", icon="USER")
        row.operator("grbl.exec_usr_cmd_2", text="", icon="USER")
        row = col.row(align=True)
        row.operator("grbl.nothing", text="", icon="BLANK1")
        row.operator("grbl.move_negative_y", text="", icon="TRIA_DOWN")
        row.operator("grbl.nothing", text="", icon="BLANK1")
        row.operator("grbl.move_negative_z", text="", icon="SORT_ASC")
        row.label()
        row.operator("grbl.exec_usr_cmd_3", text="", icon="USER")
        row.operator("grbl.exec_usr_cmd_4", text="", icon="USER")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(grbl_control, "step_size")
        row = col.row(align=True)
        row.prop(grbl_control, "feedrate")
        row = col.row(align=True)
        row.prop(grbl_control, "spindle_speed")
        if grbl_control.spindle_on_off:
            row.prop(grbl_control, "spindle_on_off", text="", icon="CANCEL")
        else:
            row.prop(grbl_control, "spindle_on_off", text="", icon="FILE_REFRESH")

        box = layout.box()
        col = box.column(align=True)        
        row = col.row(align=True)
        row.label(text="")
        row.label(text="machine")
        row.label(text="work")
        row = col.row(align=True)
        row.label(text="X")
        row.label(text="{:.3f}".format(grbl_control.current_machine_x))
        row.label(text="{:.3f}".format(grbl_control.current_machine_x - grbl_control.work_machine_x))
        row = col.row(align=True)
        row.label(text="Y")
        row.label(text="{:.3f}".format(grbl_control.current_machine_y))
        row.label(text="{:.3f}".format(grbl_control.current_machine_y - grbl_control.work_machine_y))
        row = col.row(align=True)
        row.label(text="Z")
        row.label(text="{:.3f}".format(grbl_control.current_machine_z))
        row.label(text="{:.3f}".format(grbl_control.current_machine_z - grbl_control.work_machine_z))
        
class GRBLCONTROL_PT_Milling(View3DGRBLPanel, Panel):
    bl_label = "Milling"

    def draw(self, context):
        layout = self.layout
        grbl_control = context.window_manager.grbl_control
        if bpy.context.scene.cam_operations is not None and bpy.context.scene.cam_machine.post_processor == "GRBL":
            col = layout.column()
            col.label(text="BlenderCAM with GRBL")
            row = self.layout.row()
            row.template_list("CAM_UL_operations", '', bpy.context.scene, "cam_operations", grbl_control, 'cam_active_operation')
        col = layout.column()
        row = col.row()
        row.operator("grbl.move_positive_y", text="", icon="REW")
        row.operator("grbl.resume_feed", text="", icon="PLAY")
        row.operator("grbl.feed_hold", text="", icon="PAUSE")
        col = layout.column()
        col.operator("grbl.milling_blender_cam")
        progress_bar = layout.row()
        progress_bar.prop(grbl_control, "milling_progress")
