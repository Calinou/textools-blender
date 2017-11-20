import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

def align(context, direction):

	print("Align: "+direction)

	# Collect BBox sizes
	bounds = utilities_uv.getSelectionBBox()

	#Collect UV islands
	islands = utilities_uv.getSelectionIslands()


	# if(direction is "top"):
		#Align top

	


class operator_align(bpy.types.Operator):
	bl_idname = "uv.textools_align"
	bl_label = "Align"
	bl_description = "Align vertices, edges or shells"

	direction = bpy.props.StringProperty(name="Direction", default="top")

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False
		
		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 	#self.report({'WARNING'}, "Object must have more than one UV map")

		return True


	def execute(self, context):
		
		align(context, self.direction)
		return {'FINISHED'}


#if __name__ == "__main__":
 	# test call