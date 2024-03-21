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

import serial
import re

from time import sleep
from threading import Thread

from . import (
  utils,
)

import globalstorage

storage = globalstorage.GlobalStorage.instance()

grbl_connection = None
lines_to_send = []
line_index = -1
need_next_status_update = False
stream_algorithm = "line_by_line"
chars_in_buffer = []
from_console = False

RX_BUFFER_SIZE = 70

readline_buffer = ""
def readline():
    global readline_buffer, grbl_connection
    return_line = ""
    try:
        if(grbl_connection.in_waiting > 0):
            readline_buffer = readline_buffer + grbl_connection.read(grbl_connection.in_waiting).decode()
        if readline_buffer.find("\n"):
            readline_buffer = readline_buffer.replace("\r", "")
            split = readline_buffer.split("\n")
            return_line = split[0]            
            readline_buffer = "\n".join(split[1:])
    except:
        pass # can be ignored: connection was closed, just return empty line
    return return_line

def control_buffers():
    global grbl_connection, line_index, lines_to_send, need_next_status_update, stream_algorithm, from_console
    global chars_in_buffer
    too_much_okays = 0
    while grbl_connection is not None and grbl_connection.is_open:
        line = readline()
        if len(line) > 0:
            if line.startswith("<") or line.startswith("$") or line.startswith("["):
                if from_console:
                    print("< " + line.replace("\r", "").replace("\n", ""))
                    storage["console_log"].append("< " + line)
                update_status_and_redraw(line)
            elif from_console:
                print("< " + line.replace("\r", "").replace("\n", ""))
                storage["console_log"].append("< " + line)
                from_console = False
            elif not from_console:
                print("< " + line.replace("\r", "").replace("\n", ""))
                for line_to_send in lines_to_send:
                    if line_to_send[1] == "sent":
                        line_to_send[1] = line
                        break                
                if stream_algorithm == "use_buffer":                    
                    if len(chars_in_buffer) > 0:
                        del chars_in_buffer[0]
                    else:
                        too_much_okays += 1
                        print("too_much_okays: " + str(too_much_okays))
                        
        if need_next_status_update:
            if grbl_connection is None or not grbl_connection.is_open:
                break
            grbl_connection.write(("?").encode('ascii'))
            #print("> ?")            
            need_next_status_update = False
        if stream_algorithm == "line_by_line":
            if line_index > -1 and len(lines_to_send) > 0:
                line_status = lines_to_send[line_index][1]
                if line_status == "ok" or line_status == "error:1": # error:1 will be send on empty lines and comments
                    line_index = line_index + 1
                    if line_index >= len(lines_to_send):
                        storage["milling_progress"] = 100
                        storage["milling_current_line"] = len(lines_to_send)
                        storage["is_milling"] = False
                        line_index = -1
                    else:
                        line = lines_to_send[line_index][0]
                        if grbl_connection is None or not grbl_connection.is_open:
                            break
                        grbl_connection.write((line + "\n").encode('ascii'))
                        print("> " + line.replace("\r", "").replace("\n", ""))
                        lines_to_send[line_index][1] = "sent"
                elif line_status == "":
                    if grbl_connection is None or not grbl_connection.is_open:
                        break
                    grbl_connection.write((line + "\n").encode('ascii'))
                    print("> " + line.replace("\r", "").replace("\n", ""))
                    lines_to_send[line_index][1] = "sent"
            try:
                if line_index > -1:
                    storage["milling_progress"] = line_index / len(lines_to_send) * 100
                    storage["milling_current_line"] = line_index
            except:
                pass # can be ignored: blender is not ready to update poperties. Just try next run.
        elif stream_algorithm == "use_buffer":
            if line_index > -1 and len(lines_to_send) > 0:
                line = lines_to_send[line_index][0]
                if (sum(chars_in_buffer) + len(line) + 1) < RX_BUFFER_SIZE:
                    if grbl_connection is None or not grbl_connection.is_open:
                        break
                    grbl_connection.write((line + "\n").encode('ascii'))
                    print("> " + line.replace("\r", "").replace("\n", ""))
                    chars_in_buffer.append(len(line) + 1)
                    lines_to_send[line_index][1] = "sent"
                    line_index += 1
                    if line_index >= len(lines_to_send):
                        storage["milling_progress"] = 100
                        storage["milling_current_line"] = len(lines_to_send)
                        storage["is_milling"] = False
                        line_index = -1
            try:
                if line_index > -1 or len(chars_in_buffer):
                    if line_index > -1:
                        storage["milling_current_line"] = line_index - len(chars_in_buffer)
                    else:
                        storage["milling_current_line"] = len(lines_to_send) - len(chars_in_buffer)
                    storage["milling_progress"] = storage["milling_current_line"] / len(lines_to_send) * 100                        
            except:
                pass # can be ignored: blender is not ready to update poperties. Just try next run.

        sleep(0.01)
    print("close control_buffers thread")


def request_status_update():
    global need_next_status_update
    while grbl_connection != None:
        if grbl_connection.is_open:
            try:    
                need_next_status_update = True
            except:
                pass
        sleep(0.1)
    print("close request_status_update thread")

def update_status_and_redraw(line):
    global grbl_connection
    was_status = False
    storage["last_response"] = storage["last_response"] + ""

    if line.startswith("[G5"): 
        point = line[1:4]
        coords = line[5:-1].split(",")        
        storage[point] = (float(coords[0]), float(coords[1]), float(coords[2]))
    if line.startswith("$130"): 
        storage["operation_area_x"] = float(line.split("=")[1])
    if line.startswith("$131"): 
        storage["operation_area_y"] = float(line.split("=")[1])
    if line.startswith("$132"): 
        storage["operation_area_z"] = float(line.split("=")[1])
    if line.startswith("<") and line.endswith(">"):
        was_status = True
        status = line[0:-3]
        parts = status.split("|")
        for part in parts:
            if part.startswith("MPos"):
                coords = part.split(":")[1].split(",")
                storage["current_machine_x"] = float(coords[0])
                storage["current_machine_y"] = float(coords[1])
                storage["current_machine_z"] = float(coords[2])
            if part.startswith("WCO"):
                coords = part.split(":")[1].split(",")
                storage["work_machine_x"] = float(coords[0])
                storage["work_machine_y"] = float(coords[1])
                storage["work_machine_z"] = float(coords[2])
            if part.startswith("<"):
                storage["machine_state"] = part[1:]
        utils.update_cutter_location()
    return was_status

control_buffers_thread = None
request_status_update_thread = None

class GRBLCONTROL_PT_communication:
    def open(self):
        global grbl_connection, control_buffers_thread, request_status_update_thread, chars_in_buffer, lines_to_send, line_index
        grbl_connection = serial.Serial(port=storage["connectionPort"], baudrate=storage["connectionBaudrate"], timeout=1, write_timeout=1)
        sleep(0.5)
        chars_in_buffer.clear()
        lines_to_send.clear()
        line_index = -1
        storage["is_milling"] = False
        storage["milling_line_count"] = 0
        storage["milling_current_line"] = -1
        storage["milling_progress"] = 0
        control_buffers_thread = Thread(target=control_buffers)
        control_buffers_thread.start()
        request_status_update_thread = Thread(target=request_status_update)         
        request_status_update_thread.start()
        storage["connectionEstablished"] = True
        grbl_connection.write(b"$$\n")
        grbl_connection.write(b"$#\n")

    def milling_end(self):
        global control_buffers_thread, request_status_update_thread
        storage["is_milling"] = False

    def update_status(self, line):
        update_status_and_redraw(line)

    def close(self):
        global grbl_connection
        storage["connectionEstablished"] = False
        grbl_connection.close()
        grbl_connection = None
        storage["is_milling"] = False
        storage["milling_line_count"] = 0
        storage["milling_current_line"] = -1
        storage["milling_progress"] = 0
        if control_buffers_thread.is_alive():
            control_buffers_thread.join()
        if request_status_update_thread.is_alive():
            request_status_update_thread.join()

    def update_milling_status(self, lineNumber: int, lineCount: int):
        storage["milling_line_count"] = lineCount
        storage["milling_current_line"] = lineNumber

    def is_open(self):
        global grbl_connection
        return grbl_connection != None and grbl_connection.is_open
    
    def write(self, toSend):
        global grbl_connection, from_console
        #storage["console_log"].append("> " + toSend)
        print("> " + toSend)
        from_console = True
        if len(toSend) > 1:
            toSend += "\n"
        if toSend.find("G10") > -1:
            toSend += "$#\n"
        grbl_connection.write((toSend).encode('utf-8'))

    def send_file(self, filename):
        global line_index, stream_algorithm
        storage["is_milling"] = True
        stream_algorithm = storage["stream_algorithm"]
        if stream_algorithm == "flow_control": 
            stream_algorithm == "use_buffer"
        lines_to_send.clear()
        with open(file=filename) as file:
            lines = file.readlines()
            regex = re.compile(r"\([^\)]*\)", re.IGNORECASE)
            for line in lines:
                line = line.replace("\r", "").replace("\n", "")
                line = regex.sub("", line)
                lines_to_send.append([line, "", "todo: time needed"])
        chars_in_buffer.clear()
        storage["milling_line_count"] = len(lines_to_send)
        storage["milling_current_line"] = 0
        line_index = 0
