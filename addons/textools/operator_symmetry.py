import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class operator_symmetry(bpy.types.Operator):
	"""UV Operator description"""
	bl_idname = "uv.textools_symmetry"
	bl_label = "Symmetry"
	bl_description = "Mirrors selected faces to other half or averages based on selected edge center"

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

		if bpy.context.scene.tool_settings.uv_select_mode != 'EDGE' and bpy.context.scene.tool_settings.uv_select_mode != 'FACE':
		 	return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing operator_symmetry")

	#Store selection
	utilities_uv.selectionStore()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	if bpy.context.scene.tool_settings.uv_select_mode == 'FACE':
		print( "1.) Get Face edge bounds selection")

		for face in bm.faces:
			if face.select:
				

				countSelected = 0
				for loop in face.loops:
					if loop[uvLayer].select:
						countSelected+=1
						# print("Vert selected "+str(face.index))
				if countSelected == len(face.loops):
					print("Face selected, UV?")