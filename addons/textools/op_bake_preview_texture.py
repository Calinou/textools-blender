import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict

from . import utilities_color

material_prefix = "TT_atlas_"
gamma = 2.2

class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_preview_texture"
	bl_label = "Preview Texture"
	bl_description = "Preview the current UV image view background image on the selected object."
	bl_options = {'REGISTER', 'UNDO'}
	

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if bpy.context.active_object not in bpy.context.selected_objects:
			return False

		if len(bpy.context.selected_objects) != 1:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

			#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 

		# Only when we have a background image
		for area in bpy.context.screen.areas:
			if area.type == 'IMAGE_EDITOR':
				return area.spaces[0].image

		return False
	
	def execute(self, context):
		preview_texture(self, context)
		return {'FINISHED'}



def preview_texture(self, context):
	obj = bpy.context.active_object
	