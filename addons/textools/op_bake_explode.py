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
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):

		return True


	def execute(self, context):
		
		# swap(context)
		return {'FINISHED'}

def explode():
	sets = settings.sets
	for set in sets:
		print("Explode '{}'".format(set.name))
