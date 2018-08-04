import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_size"
	bl_label = "Scale to Size"
	bl_description = "Scale Islands to match their width or height"
	bl_options = {'REGISTER', 'UNDO'}

	mode = bpy.props.StringProperty(name="Mode", default="HEIGHT")
	
	@classmethod
	def poll(cls, context):
		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		if not bpy.context.active_object:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True


	def execute(self, context):
		#Store selection
		utilities_uv.selection_store()

		main(context)

		#Restore selection
		utilities_uv.selection_restore()

		return {'FINISHED'}



def main(context):
	print("Executing operator_island_align_edge")

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uv_layer = bm.loops.layers.uv.verify()
	
	# Face mode
	bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

	islands = utilities_uv.getSelectionIslands()


	#Rotate to minimal bounds
	for i in range(0, len(islands)):

		bpy.ops.uv.select_all(action='DESELECT')
		utilities_uv.set_selected_uv_faces(islands[i])

		# Collect BBox sizes
		bounds = utilities_uv.getSelectionBBox()

		print("ISland {}  = {} x {}".format(i, bounds['width'], bounds['height']))
		# allSizes[i] = max(bounds['width'], bounds['height']) + i*0.000001;#Make each size unique
		# allBounds[i] = bounds;
		# print("Rotate compact:  "+str(allSizes[i]))
