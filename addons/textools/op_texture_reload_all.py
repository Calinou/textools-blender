import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

class op(bpy.types.Operator):
	bl_idname = "uv.textools_texture_reload_all"
	bl_label = "Reload Textures and remove unused Textures"
	bl_description = "Reload all textures"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	# Clean up unused images
	for img in bpy.data.images:
		if not img.users:
			bpy.data.images.remove(img)
			
	#Reload all File images
	for img in bpy.data.images :
		if img.source == 'FILE' :
			img.reload()

	
