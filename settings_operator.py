import bpy
from bpy.types import Operator
from . import (
  utils,
  operators
)

import globalstorage

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    IntProperty,
    EnumProperty,
)

storage = globalstorage.GlobalStorage.instance()

class GRBLCONTROL_OT_settings(Operator):
    bl_idname = "grbl.settings"
    bl_label = "Settings"

    connectionPort: EnumProperty(name="Port", description="Port to connect to CNC", items=utils.port_list_callback) # type: ignore
    connectionBaudrate: IntProperty(name="Baudrate", description="Baud rate for port to connect to CNC", default=115200) # type: ignore
    stream_algorithm: EnumProperty(name = "Stream Algorithm", description = "Algorithm used for streaming the data",
        items = [
            ("line_by_line" , "Line by line" , "Sends one line, wait for GRBL to process it and send the next one"),
            ("use_buffer" , "Use buffer" , "Use the GRBL UART buffer to make the operation more robust"),
            ("flow_control" , "Flow control" , "Use hardware handshakes to get the status of the buffer. Not implemented right now. (Fallback to use_buffer)"),
        ],
        default="use_buffer"
    ) # type: ignore
    user_command_name1: StringProperty(name="User cmd 1 button label", description="User gcode that can be run via the button 'user command 1'", default="Empty slot") # type: ignore
    user_command_text1: StringProperty(name="User cmd 1 g code", description="User gcode that can be run via the button 'user command 1'", default="", ) # type: ignore
    user_command_icon1: StringProperty(name="User cmd 1 Icon", description="User gcode that can be run via the button 'user command 1'", default="USER") # type: ignore
    user_command_name2: StringProperty(name="User cmd 2 button label", description="User gcode that can be run via the button 'user command 2'", default="Empty slot") # type: ignore
    user_command_text2: StringProperty(name="User cmd 2 g code", description="User gcode that can be run via the button 'user command 2'", default="") # type: ignore
    user_command_icon2: StringProperty(name="User cmd 2 Icon", description="User gcode that can be run via the button 'user command 2'", default="USER") # type: ignore
    user_command_name3: StringProperty(name="User cmd 3 button label", description="User gcode that can be run via the button 'user command 3'", default="Empty slot") # type: ignore
    user_command_text3: StringProperty(name="User cmd 3 g code", description="User gcode that can be run via the button 'user command 3'", default="") # type: ignore
    user_command_icon3: StringProperty(name="User cmd 3 Icon", description="User gcode that can be run via the button 'user command 3'", default="USER") # type: ignore
    user_command_name4: StringProperty(name="User cmd 4 button label", description="User gcode that can be run via the button 'user command 4'", default="Empty slot") # type: ignore
    user_command_text4: StringProperty(name="User cmd 4 g code", description="User gcode that can be run via the button 'user command 4'", default="") # type: ignore
    user_command_icon4: StringProperty(name="User cmd 4 Icon", description="User gcode that can be run via the button 'user command 4'", default="USER") # type: ignore
    user_command_icon4: StringProperty(name="User cmd 4 Icon", description="User gcode that can be run via the button 'user command 4'", default="USER") # type: ignore
    working_coords_display_as: EnumProperty(name="Working coords display as", description="How the working coords will be displayed", items=utils.empty_display_as_items) # type: ignore
    working_coords_show: BoolProperty(name="working coords show", description="Should the working coords be displayed", default=True) # type: ignore
    working_coords_xray: BoolProperty(name="working coords show xray", description="Should the working coords be as xray through objects", default=True) # type: ignore
    working_coords_size: FloatProperty(name="Working coords size", description="Which size the working coords will be displayed", default=20) # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        col.prop(self, "connectionPort", expand=False)
        col.prop(self, "connectionBaudrate")
        col.prop(self, "stream_algorithm")
        col.separator()
        col = layout.column()
        col.label(text="User Command 1:")
        col.prop(self, "user_command_name1", text="Button label")
        col.prop(self, "user_command_text1", text="GCode")
        col.prop(self, "user_command_icon1", text="Icon")
        col.separator()
        col = col.column()
        col.label(text="User Command 2:")
        col.prop(self, "user_command_name2", text="Button label")
        col.prop(self, "user_command_text2", text="GCode")
        col.prop(self, "user_command_icon2", text="Icon")
        col.separator()
        col = col.column()
        col.label(text="User Command 3:")
        col.prop(self, "user_command_name3", text="Button label")
        col.prop(self, "user_command_text3", text="GCode")
        col.prop(self, "user_command_icon3", text="Icon")
        col.separator()
        col = col.column()
        col.label(text="User Command 4:")
        col.prop(self, "user_command_name4", text="Button label")
        col.prop(self, "user_command_text4", text="GCode")
        col.prop(self, "user_command_icon4", text="Icon")

        # workaround no pointer allowed in operators, the name will be saved in copyMillingEndLoc_name
        grbl_control = bpy.context.window_manager.grbl_control
        col.separator()
        col = col.column()
        col.label(text="Animation")
        col.prop(grbl_control, "copyMillingEndLoc")

        col.separator()
        col = col.column()
        col.label(text="Work Coordinates")
        col.prop(self, "working_coords_show")
        col.prop(self, "working_coords_display_as", text="Display As")
        col.prop(self, "working_coords_size", text="Size")
        col.prop(self, "working_coords_xray", text="Xray")

    def execute(self, context):
        storage["connectionPort"] = self.connectionPort
        storage["connectionBaudrate"] = self.connectionBaudrate
        storage["stream_algorithm"] = self.stream_algorithm
        storage["user_command_name1"] = self.user_command_name1
        storage["user_command_text1"] = self.user_command_text1
        storage["user_command_icon1"] = self.user_command_icon1
        storage["user_command_name2"] = self.user_command_name2
        storage["user_command_text2"] = self.user_command_text2
        storage["user_command_icon2"] = self.user_command_icon2
        storage["user_command_name3"] = self.user_command_name3
        storage["user_command_text3"] = self.user_command_text3
        storage["user_command_icon3"] = self.user_command_icon3
        storage["user_command_name4"] = self.user_command_name4
        storage["user_command_text4"] = self.user_command_text4
        storage["user_command_icon4"] = self.user_command_icon4

        # workaround enum setter/getter handle index instead of value, while getattr gives value
        grbl_control = bpy.context.window_manager.grbl_control
        grbl_control.connectionPort = self.connectionPort
        grbl_control.stream_algorithm = self.stream_algorithm
        grbl_control.working_coords_display_as = self.working_coords_display_as

        if grbl_control.copyMillingEndLoc is not None:
            storage["copyMillingEndLoc_name"] =  grbl_control.copyMillingEndLoc.name
        else:
            storage["copyMillingEndLoc_name"] =  ""

        storage["working_coords_show"] = self.working_coords_show
        storage["working_coords_display_as"] = self.working_coords_display_as
        storage["working_coords_size"] = self.working_coords_size
        storage["working_coords_xray"] = self.working_coords_xray

        reregister_user_buttons()
        storage.save()
        return {'FINISHED'}

    def invoke(self, context, event):        
        self.connectionPort = storage["connectionPort"]
        self.connectionBaudrate = storage["connectionBaudrate"]
        self.stream_algorithm = storage["stream_algorithm"]
        self.user_command_name1 = storage["user_command_name1"]
        self.user_command_text1 = storage["user_command_text1"]
        self.user_command_icon1 = storage["user_command_icon1"]
        self.user_command_name2 = storage["user_command_name2"]
        self.user_command_text2 = storage["user_command_text2"]
        self.user_command_icon2 = storage["user_command_icon2"]
        self.user_command_name3 = storage["user_command_name3"]
        self.user_command_text3 = storage["user_command_text3"]
        self.user_command_icon3 = storage["user_command_icon3"]
        self.user_command_name4 = storage["user_command_name4"]
        self.user_command_text4 = storage["user_command_text4"]
        self.user_command_icon4 = storage["user_command_icon4"]
        
        self.working_coords_show = storage["working_coords_show"]
        self.working_coords_display_as = storage["working_coords_display_as"]
        self.working_coords_size = storage["working_coords_size"]
        self.working_coords_xray = storage["working_coords_xray"]

        return context.window_manager.invoke_props_dialog(self)

def reregister_user_buttons():
  grbl_control = bpy.context.window_manager.grbl_control  
  operators.GRBLCONTROL_PT_execute_user_command_1.bl_label = grbl_control.user_command_name1
  operators.GRBLCONTROL_PT_execute_user_command_2.bl_label = grbl_control.user_command_name2
  operators.GRBLCONTROL_PT_execute_user_command_3.bl_label = grbl_control.user_command_name3
  operators.GRBLCONTROL_PT_execute_user_command_4.bl_label = grbl_control.user_command_name4

  for cls in [operators.GRBLCONTROL_PT_execute_user_command_1, operators.GRBLCONTROL_PT_execute_user_command_2, 
              operators.GRBLCONTROL_PT_execute_user_command_3, operators.GRBLCONTROL_PT_execute_user_command_4]:
    bpy.utils.unregister_class(cls)
    bpy.utils.register_class(cls)

    