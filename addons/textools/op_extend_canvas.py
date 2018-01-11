import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv
from . import utilities_ui



class op_select_extend_direction(bpy.types.Operator):
	bl_idname = "uv.textools_select_extend_direction"
	bl_label = "Select"
	bl_description = "Select this bake set in scene"

	direction = bpy.props.StringProperty(default="TL")

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		print("Set: "+self.direction)
		
		bpy.context.scene.texToolsSettings.canvas_extend_direction = self.direction

		return {'FINISHED'}



class op(bpy.types.Operator):
	bl_idname = "uv.textools_extend_canvas"
	bl_label = "Extend Canvas"
	bl_description = "Resize the UV canvas size"
	bl_options = {'REGISTER', 'UNDO'}

	size = bpy.props.IntVectorProperty(
		name = "Size",
		size=2, 
		description="Texture & UV size in pixels",
		default = (512,512),
		subtype = "XYZ"
	)


	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False
		
		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True


	def execute(self, context):
		
		extend_canvas(self)
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width = 160)

	def draw(self, context):
		# https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
		layout = self.layout
		# layout.label("Alignment?")

		# box = layout.box()
		r = layout.row()

		col = r.column(align=True)
		col.label("Side")
		row = col.row(align=True)
		row.operator(op_select_extend_direction.bl_idname, text="", icon_value=icon_direction("TL")).direction = "TL"
		row.operator(op_select_extend_direction.bl_idname, text="", icon_value=icon_direction("TR")).direction = "TR"
		row = col.row(align=True)
		row.operator(op_select_extend_direction.bl_idname, text="", icon_value=icon_direction("BL")).direction = "BL"
		row.operator(op_select_extend_direction.bl_idname, text="", icon_value=icon_direction("BR")).direction = "BR"
		

		# layout.prop(self.size)
		col = r.column(align=True)
		col.prop(self, "size", text="Size")
		
		self.layout.label("....")




def icon_direction(key):
	if bpy.context.scene.texToolsSettings.canvas_extend_direction == key:
		return utilities_ui.icon_get("op_extend_canvas_{}_active".format(key))
	else:
		return utilities_ui.icon_get("op_extend_canvas_{}_inactive".format(key))


def extend_canvas(self):
	direction = bpy.context.scene.texToolsSettings.canvas_extend_direction
	print("Execute op_extend_canvas: {}".format(direction))

	#Only in Edit mode
	# if bpy.context.active_object.mode != 'EDIT':
	# 	return False





# if __name__ == "__main__":
	# register()
utilities_ui.icon_register("op_extend_canvas_TL_active.png")
utilities_ui.icon_register("op_extend_canvas_TR_active.png")
utilities_ui.icon_register("op_extend_canvas_BL_active.png")
utilities_ui.icon_register("op_extend_canvas_BR_active.png")
utilities_ui.icon_register("op_extend_canvas_TL_inactive.png")
utilities_ui.icon_register("op_extend_canvas_TR_inactive.png")
utilities_ui.icon_register("op_extend_canvas_BL_inactive.png")
utilities_ui.icon_register("op_extend_canvas_BR_inactive.png")

print("__________________Register op_extend_canvas???")