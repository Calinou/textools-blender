import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi


class op(bpy.types.Operator):
	bl_idname = "uv.textools_texel_density_get"
	bl_label = "Get Texel size"
	bl_description = "Get Pixel per unit ratio or Texel density"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):

		if not bpy.context.active_object:
			return False
		
		if len(bpy.context.selected_objects) == 0:
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
		get_texel_density(self, context)
		return {'FINISHED'}



def get_texel_density(self, context):
	print("Get texel density")