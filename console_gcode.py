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

import os
import bpy
import globalstorage
from time import sleep
from threading import Thread

storage = globalstorage.GlobalStorage.instance()
language_id = "gcode"
PROMPT = "> "

def add_scrollback(text, text_type):
    for l in text.split("\n"):
        bpy.ops.console.scrollback_append(text=l.replace("\t", "    "),
                                          type=text_type)


def execute(context, _is_interactive):
    sc = context.space_data

    try:
        line = sc.history[-1].body
    except:
        return {'CANCELLED'}


    if len(storage["console_log"]):
        add_scrollback("\n".join(storage["console_log"]), "OUTPUT")
        storage["console_log"].clear()

    if not storage["connectionEstablished"]:
        bpy.ops.console.scrollback_append(text="Not connected.", type='ERROR')
        return {'CANCELLED'}
    
    bpy.ops.console.scrollback_append(text=sc.prompt + line, type='INPUT')

    storage["console_command"] = line
    bpy.ops.grbl.send_console_command('INVOKE_DEFAULT')

    # insert a new blank line
    bpy.ops.console.history_append(text="", current_character=0,
                                   remove_duplicates=True)

    time_out_counter = 10
    response_complete = False
    while time_out_counter > 0 and not response_complete:
        if len(storage["console_log"]):
            add_scrollback("\n".join(storage["console_log"]), "OUTPUT")
            if storage["console_log"][-1].split(":")[0] in ["< ok", "< error", "< alarm"]:
                response_complete = True
            storage["console_log"].clear()
        sleep(0.1)
        time_out_counter -= 1

    if time_out_counter == 0:
        bpy.ops.console.scrollback_append(text="Timeout during request (> 1000 ms)", type='ERROR')
        return {'CANCELLED'}

    sc.prompt = PROMPT
    return {'FINISHED'}


def autocomplete(_context):
    # sc = context.space_data
    # TODO

    return {'FINISHED'}


def banner(context):
    sc = context.space_data

    bpy.ops.console.clear()

    message = (
        "GCode console by GRBL-Control"
        "",
        "send GCode directly to your CNC machine"
        "",
    )

    for line in message:
        add_scrollback(line, 'OUTPUT')

    sc.prompt = PROMPT

    return {'FINISHED'}

#def get_serial_reponses():
#    while True:
#        if "console_log" in storage:
#            if len(storage["console_log"]):
#                try:
#                    add_scrollback("\n".join(storage["console_log"]), "OUTPUT")
#                    storage["console_log"].clear()
#                except:
#                    pass
#        sleep(0.1)
#
#serial_reponse_thread = Thread(target=get_serial_reponses)
#serial_reponse_thread.start()