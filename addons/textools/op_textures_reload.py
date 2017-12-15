import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

class op(bpy.types.Operator):
	bl_idname = "uv.textools_textures_reload"
	bl_label = "Reload Textures"
	bl_description = "Reload all textures"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	#Reload all File images
	for img in bpy.data.images :
	    if img.source == 'FILE' :
	         img.reload()
