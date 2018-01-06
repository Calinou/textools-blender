import bpy
import os
import bmesh
import math
from mathutils import Vector
from collections import defaultdict

from . import utilities_uv

class op(bpy.types.Operator):
	bl_idname = "uv.textools_setup_split_uv"
	bl_label = "Split"
	bl_description = "Unwrap model by sharp edges of topology"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):

		if not bpy.context.active_object:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing operator_split_setup")

	if bpy.context.active_object.mode != 'EDIT':
		bpy.ops.object.mode_set(mode='EDIT')



	#Store selection
	utilities_uv.selectionStore()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()


	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
	bpy.ops.mesh.select_all(action='DESELECT')

	# Select Sharp Edges
	bpy.ops.mesh.edges_select_sharp(sharpness=(75 * math.pi/180))
	bpy.ops.mesh.mark_seam(clear=False)

	# Unwrap all faces
	bpy.ops.uv.select_all(action='SELECT')
	bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)


	#Start Mode
	bpy.context.scene.tool_settings.use_uv_select_sync = True
	bpy.ops.uv.select_all(action='DESELECT')
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

	print("Setup splti setup")