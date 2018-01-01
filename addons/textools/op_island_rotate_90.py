import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_rotate_90"
	bl_label = "Rotate 90 degrees"
	bl_description = "Rotate the selected UV island 90 degrees left or right"
   
	angle = bpy.props.FloatProperty(name="Angle")


	@classmethod
	def poll(cls, context):

		if not bpy.context.active_object:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False


		return True


	def execute(self, context):

		main(context)
		return {'FINISHED'}


def main(context):
	
	#Store selection
	utilities_uv.selectionStore()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()
	
	# bpy.ops.transform.rotate(-math.pi / 2)
	# row.operator("transform.rotate", text="-90°", icon_value = getIcon("turnLeft")).value = -math.pi / 2
	# row.operator("transform.rotate", text="+90°", icon_value = getIcon("turnRight")).value = math.pi / 2
		

	#Restore selection
	utilities_uv.selectionRestore()