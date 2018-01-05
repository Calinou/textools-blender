import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi


class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_explode"
	bl_label = "Swap UV 2 XYZ"
	bl_description = "Swap UV to XYZ coordinates"


	@classmethod
	def poll(cls, context):

		return True


	def execute(self, context):
		
		# swap(context)
		return {'FINISHED'}

