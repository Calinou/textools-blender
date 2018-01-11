import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv


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

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True


	def execute(self, context):
		
		swap(context)
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width = 160)

	def draw(self, context):
		# https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
		layout = self.layout
		layout.label("Alignment?")

		col = layout.column(align=True)
		row = col.row(align=True)
		row.operator("object.select_all", text="Tdsa")
		row.operator("object.select_all", text="Tdsa")
		layout = layout.column(align=True)
		row = col.row(align=True)
		row.operator("object.select_all", text="Tdsa")
		row.operator("object.select_all", text="Tdsa")
		

		# layout.prop(self.size)
		col = layout.column(align=True)
		col.prop(self, "size", text="Size")
		
		self.layout.label("....")


def swap(context):
	print("Execute op_extend_canvas")

