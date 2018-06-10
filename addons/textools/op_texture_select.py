import bpy
import bmesh
import operator
import math

from . import settings
from . import utilities_bake

class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_preview_texture"
	bl_label = "Select Texture"
	bl_description = "Select the texture and bake mode"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return True
	
	def execute(self, context):
		select_texture(self, context)
		return {'FINISHED'}



def select_texture(self, context):
	pass