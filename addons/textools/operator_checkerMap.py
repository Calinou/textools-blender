import bpy
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi



def main(context):
	print("Executing IslandsAlignSort main")
   
	

class CheckerMap(bpy.types.Operator):
	"""UV Operator description"""
	bl_idname = "uv.textools_checker_map"
	bl_label = "Add Checker Map"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


if __name__ == "__main__":
 	# test call
	lastOperator = bpy.context.area.type;
	if bpy.context.area.type != 'IMAGE_EDITOR':
		bpy.context.area.type = 'IMAGE_EDITOR'

	bpy.ops.uv.textools_checker_map()

	#restore context, e.g. back to code editor instead of uv editor
	bpy.context.area.type = lastOperator