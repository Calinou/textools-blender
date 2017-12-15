import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv


class op(bpy.types.Operator):
	bl_idname = "uv.textools_islands_select_identical"
	bl_label = "Select identical"
	bl_description = "Select identical islands with similar topology"


	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False
		
		if bpy.context.active_object.type != 'MESH':
			return False

		#One or more objects selected
		if len(bpy.context.selected_objects) == 0:
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 	#self.report({'WARNING'}, "Object must have more than one UV map")


		return True


	def execute(self, context):
		
		swap(context)
		return {'FINISHED'}


def swap(context):
	print("Execute op_islands_select_identical")

	