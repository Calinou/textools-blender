import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_elements_setup"
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



def setup_elements(self, context):
	obj = bpy.context.active_object
	
	# Store previous mode
	previous_mode = bpy.context.active_object.mode
	if bpy.context.active_object.mode != 'EDIT':
		bpy.ops.object.mode_set(mode='EDIT')

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);



	faces_processed = []
	# bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'NORMAL'}, index=208)
	# bpy.ops.mesh.select_similar(type='AREA', threshold=0.01)



	# for face in bm.faces:
	# 	face.material_index = 0


	bpy.ops.object.mode_set(mode=previous_mode)