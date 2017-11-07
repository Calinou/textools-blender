import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

class operator_reloadTextures(bpy.types.Operator):
	"""UV Operator description"""
	bl_idname = "uv.textools_reload_textures"
	bl_label = "Reload Textures"
	bl_description = "Reload all textures"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing operator_checkerMap main()")

	#Reload all File images
	for img in bpy.data.images :
	    if img.source == 'FILE' :
	         img.reload()
