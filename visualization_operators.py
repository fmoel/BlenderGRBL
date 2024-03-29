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
        active_object = bpy.context.view_layer.objects.active
        copy_constraint = None

        diameter = 0.003
        length = 0.020
        location = ((storage['operation_area_x'] + storage['current_machine_x']) / 1000,
                    (storage['operation_area_y'] + storage['current_machine_y']) / 1000,
                    (storage['current_machine_z']) / 1000)
        if storage['cam_active_operation'] != -1: # and bpy.data.scenes["Scene"].cam_operations is not None and storage['cam_active_operation'] in bpy.data.scenes["Scene"].cam_operations:
            diameter = bpy.data.scenes["Scene"].cam_operations[storage['cam_active_operation']].cutter_diameter

        if storage["copyMillingEndLoc_name"] != "" and storage["copyMillingEndLoc_name"] in bpy.data.objects:
            obj = bpy.data.objects[storage["copyMillingEndLoc_name"]]
            obj.location = location
            context.view_layer.objects.active = obj

            if "Copy cutter location" not in obj.constraints:
                bpy.ops.object.constraint_add(type='COPY_LOCATION')
                copy_constraint = obj.constraints.items()[-1][1]
                copy_constraint.name = "Copy cutter location"
            else:
                copy_constraint = obj.constraints["Copy cutter location"]


        needs_new_cutter = False
        if 'CAM_cutter' in bpy.data.objects:
            obj = bpy.data.objects['CAM_cutter']
            if 'diameter' in obj.data and obj.data['diameter'] == diameter and 'length' in obj.data and obj.data['length'] == length:
                obj.location = location
            else:
                needs_new_cutter = True
        else:
            needs_new_cutter = True

        if needs_new_cutter:
            #save current state
            stored_mode = context.mode
            if stored_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            selected_objects = context.selected_objects.copy()
            hide_viewport = False

            for obj in selected_objects:
                obj.select_set(False)
            if 'CAM_cutter' in bpy.data.objects:
                obj = bpy.data.objects['CAM_cutter']
                hide_viewport = obj.hide_get()
                obj.hide_set(False)
                obj.hide_select = False
                obj.select_set(True)
                bpy.ops.object.delete(use_global=False, confirm=False)

            bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=diameter / 2, depth=length, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))        
            bpy.ops.object.editmode_toggle()
            obj = context.object
            obj.name = "CAM_cutter"
            mesh = obj.data
            blendermesh = bmesh.from_edit_mesh(mesh)
            blendermesh.faces.active = None
            for vertex in blendermesh.verts:
                vertex.co.z += length / 2
            bmesh.update_edit_mesh(mesh, loop_triangles=True)
            bpy.ops.object.editmode_toggle()
            obj.data["diameter"] = diameter
            obj.data["length"] = length
            if copy_constraint is not None:
                copy_constraint.target = obj
            obj.hide_set(hide_viewport)
            obj.hide_select = True
            obj.select_set(False)

            #restore former mode
            for obj in selected_objects:
                obj.select_set(True)
            if stored_mode in ENUM_CORRECTION and stored_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=ENUM_CORRECTION[stored_mode])
        bpy.context.view_layer.objects.active = active_object
        return {'FINISHED'}
    
class GRBLCONTROL_PT_create_or_update_working_coords_emptys(Operator):
    bl_idname = "grbl.create_or_update_working_coords_emptys"
    bl_label = "Create or update working coords emptys in 3D space"
    bl_description = "Create or update working coords emptys in 3D space"

    def invoke(self, context, event):
        working_points = ["machine_zero", "G54", "G55", "G56", "G57", "G58", "G59"]

        needs_new_empties = False
        any_emptys = False
        for name in working_points:
            if name not in bpy.data.objects:
                needs_new_empties = True and storage["working_coords_show"]
            else:
                any_emptys = True

        if needs_new_empties:
            #save current state
            grbl_control = bpy.context.window_manager.grbl_control
            active_object = bpy.context.view_layer.objects.active
            stored_mode = context.mode
            if stored_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            selected_objects = context.selected_objects.copy()

            for name in working_points:
                location = ((storage["operation_area_x"] + storage[name][0]) / 1000, (storage["operation_area_y"] + storage[name][1]) / 1000, storage[name][2] / 1000)
                obj = None
                if name in bpy.data.objects:
                    obj = bpy.data.objects[name]
                else:
                    bpy.ops.object.empty_add(type=grbl_control.working_coords_display_as, align='WORLD', location=location, radius=storage["working_coords_size"])
                    obj = context.object
                    obj.name = name
                    obj.show_name = True
                    obj.show_in_front = True

            #restore former mode
            for obj in selected_objects:
                obj.select_set(True)
            if stored_mode in ENUM_CORRECTION and stored_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode=ENUM_CORRECTION[stored_mode])
            bpy.context.view_layer.objects.active = active_object
        elif not storage["working_coords_show"]:
            if any_emptys:
                #save current state
                active_object = bpy.context.view_layer.objects.active
                stored_mode = context.mode
                if stored_mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                selected_objects = context.selected_objects.copy()
                for obj in selected_objects:
                    obj.select_set(False)

                for name in working_points:
                    if name in bpy.data.objects:
                        obj = bpy.data.objects[name]
                        obj.hide_set(False)
                        obj.hide_select = False
                        obj.select_set(True)

                bpy.ops.object.delete(use_global=False, confirm=False)

                #restore former mode
                for obj in selected_objects:
                    obj.select_set(True)
                if stored_mode in ENUM_CORRECTION and stored_mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode=ENUM_CORRECTION[stored_mode])
                bpy.context.view_layer.objects.active = active_object
        else:
            for name in working_points:
                working_point = bpy.data.objects[name]
                location = ((storage["operation_area_x"] + storage[name][0]) / 1000, (storage["operation_area_y"] + storage[name][1]) / 1000, storage[name][2] / 1000)
                working_point.location = location
        return {'FINISHED'}    