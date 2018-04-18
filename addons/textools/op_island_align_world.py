import bpy
import os
import bmesh
import math
import operator
from mathutils import Vector
from collections import defaultdict
from itertools import chain # 'flattens' collection of iterables

from . import utilities_uv



class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_world"
	bl_label = "Align World"
	bl_description = "Align selected UV islands to world / gravity directions"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):


		if not bpy.context.active_object:
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


		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False


		# if bpy.context.scene.tool_settings.uv_select_mode != 'FACE':
		#  	return False

		# if bpy.context.scene.tool_settings.use_uv_select_sync:
		# 	return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}



def main(context):
	print("--------------------------- Executing aling_world")

	#Store selection
	# utilities_uv.selection_store()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()


