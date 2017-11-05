import bpy
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi



def main(context):
	print("Executing operator_align main()")
   
	

class operator_align(bpy.types.Operator):
	bl_idname = "uv.textools_align"
	bl_label = "Align"
	bl_description = "Align vertices, edges or shells"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


#if __name__ == "__main__":
 	# test call