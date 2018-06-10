import bpy
import bmesh
import operator
import math

from . import settings
from . import utilities_bake

class op(bpy.types.Operator):
	bl_idname = "uv.textools_texture_save"
	bl_label = "Save Texture"
	bl_description = "Save the texture"


	@classmethod
	def poll(cls, context):
		return True
	
	def execute(self, context):
		save_texture(self, context)
		return {'FINISHED'}



def save_texture(self, context):
	pass