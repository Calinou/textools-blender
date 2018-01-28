import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_clear"
	bl_label = "Clear Colors"
	bl_description = "Clear color materials on model"
	bl_options = {'REGISTER', 'UNDO'}
	

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if bpy.context.active_object not in bpy.context.selected_objects:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		return True
	
	def execute(self, context):
		clear_colors(self, context)
		return {'FINISHED'}



def clear_colors(self, context, index):
	# obj = bpy.context.active_object

	print("Clear materials for selected objcts")
	
