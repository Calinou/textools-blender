import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi


class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_explode"
	bl_label = "Explode"
	bl_description = "Explode selected bake pairs with animation keyframes"


	@classmethod
	def poll(cls, context):

		return True


	def execute(self, context):
		
		# swap(context)
		return {'FINISHED'}

def explode():
	sets = utilities_bake.get_bake_pairs()
	for set in sets:
		print("Explode '{}'".format(set.name))
