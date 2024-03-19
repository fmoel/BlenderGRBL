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
import globalstorage

storage = globalstorage.GlobalStorage.instance()

ENUM_CORRECTION = {"OBJECT": "OBJECT", "EDIT_MESH": "EDIT", "PAINT_VERTEX": "VERTEX_PAINT"}

class GRBLCONTROL_PT_create_cutter_object(Operator):
    bl_idname = "grbl.create_cutter_object"
    bl_label = "Create a cutter in 3D space"
    bl_description = "Create a cutter in 3D space"

    def invoke(self, context, event):
        #save current state
        stored_mode = context.mode
        if stored_mode != 'OBJECT':
          bpy.ops.object.mode_set(mode='OBJECT')
        selected_objects = context.selected_objects.copy()
        active_object = bpy.context.view_layer.objects.active
        hide_viewport = False

        for obj in selected_objects:
            obj.select_set(False)
        if 'CAM_cutter' in bpy.data.objects:
            hide_viewport = bpy.data.objects['CAM_cutter'].hide_get()
            bpy.data.objects['CAM_cutter'].hide_set(False)
            bpy.data.objects['CAM_cutter'].hide_select = False
            bpy.data.objects['CAM_cutter'].select_set(True)
            bpy.ops.object.delete(use_global=False, confirm=False)

        diameter = 0.003
        location = ((storage['current_machine_x'] - storage['work_machine_x']) / 1000,
                    (storage['current_machine_y'] - storage['work_machine_y']) / 1000,
                    (storage['current_machine_z'] - storage['work_machine_z']) / 1000)
        if storage['cam_active_operation'] != -1: # and bpy.data.scenes["Scene"].cam_operations is not None and storage['cam_active_operation'] in bpy.data.scenes["Scene"].cam_operations:
          diameter = bpy.data.scenes["Scene"].cam_operations[storage['cam_active_operation']].cutter_diameter

        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=diameter / 2, depth=0.02, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))        
        bpy.ops.object.editmode_toggle()
        obj = context.object
        obj.name = "CAM_cutter"
        mesh = obj.data
        blendermesh = bmesh.from_edit_mesh(mesh)
        blendermesh.faces.active = None
        for vertex in blendermesh.verts:
            vertex.co.z += 0.01
        bmesh.update_edit_mesh(mesh, loop_triangles=True)
        bpy.ops.object.editmode_toggle()
        obj.hide_set(hide_viewport)
        obj.hide_select = True
        obj.select_set(False)

        #restore former mode
        for obj in selected_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = active_object
        if stored_mode in ENUM_CORRECTION and stored_mode != 'OBJECT':
          bpy.ops.object.mode_set(mode=ENUM_CORRECTION[stored_mode])
        return {'FINISHED'}