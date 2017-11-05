import bpy
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi



def main(context):
	print("Executing operator_IslandsPack main() ")
   
	

class operator_islandsPack(bpy.types.Operator):
	bl_idname = "uv.textools_islands_pack"
	bl_label = "Pack Islands"
	bl_description = "Pack islands and remain scale"

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