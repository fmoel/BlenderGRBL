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

import bpy
import serial.tools.list_ports as port_list
import globalstorage

storage = globalstorage.GlobalStorage.instance()

def port_list_callback(scene, context):
    items = []
    ports = list(port_list.comports())
    for port in ports:
        items.append((port.name, port.name, ""))
    return items

def update_cutter_location():
    if 'CAM_cutter' in bpy.data.objects:
        try:
            obj = bpy.data.objects['CAM_cutter']
            location = ((storage['operation_area_x'] + storage['current_machine_x']) / 1000,
                        (storage['operation_area_y'] + storage['current_machine_y']) / 1000,
                        (storage['current_machine_z']) / 1000)
            obj.location = location
        except:
            pass

def empty_display_as_items(dummy, dummy1):
    try:
        return [(ot.identifier, ot.name, ot.description, ot.icon, ot.value) for ot in bpy.types.Object.bl_rna.properties['empty_display_type'].enum_items]
    except:
        return []