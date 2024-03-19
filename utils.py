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

import bpy, os, json
import serial.tools.list_ports as port_list
import globalstorage

storage = globalstorage.GlobalStorage.instance()

def force_redraw():
  return
  for screen in bpy.data.screens:
    for area in screen.areas:
      if area.ui_type == "VIEW_3D":
        for region in area.regions:
          if region.type == "UI":
            region.tag_redraw()

def port_list_callback(scene, context):
  items = []
  ports = list(port_list.comports())
  for port in ports:
    items.append((port.name, port.name, ""))
  return items

def update_cutter_location():
    if 'CAM_cutter' in bpy.data.objects:
        try:
          bpy.data.objects['CAM_cutter'].location = ((storage['current_machine_x'] - storage['work_machine_x']) / 1000,
                                                     (storage['current_machine_y'] - storage['work_machine_y']) / 1000,
                                                     (storage['current_machine_z'] - storage['work_machine_z']) / 1000)
        except:
          pass