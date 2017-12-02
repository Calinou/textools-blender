import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class operator_island_align_edge(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_edge"
	bl_label = "Align Island by Edge"
	bl_description = "Align the island by selected edge"
   
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
			return False

		if bpy.context.scene.tool_settings.uv_select_mode != 'EDGE':
		 	return False


		return True


	def execute(self, context):

		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing operator_island_align_edge")
   	
   	#Store selection
	utilities_uv.selectionStore()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	
	for face in bm.faces:
		if face.select:
			for loop in face.loops:
				if loop[uvLayer].select:
					print("Vert selected "+str(face.index))
			# break;
		
		# isUVFaceSelected = True;
		# for loop in face.loops:
		# 	if loop[uvLayer].select is False:
		# 		isUVFaceSelected = False;
		# 		continue

	#Restore selection
	utilities_uv.selectionRestore()