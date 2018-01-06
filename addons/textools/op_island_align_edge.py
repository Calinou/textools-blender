import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_edge"
	bl_label = "Align Island by Edge"
	bl_description = "Align the island by selected edge"
	bl_options = {'REGISTER', 'UNDO'}
	
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

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()
	
	# > bmesh.from_edit_mesh(bpy.context.active_object.data).verts[0].select
	
	selectedVerts = []

	for face in bm.faces:
		if face.select:
			del selectedVerts[:]#Clear List
			for loop in face.loops:
				if loop[uvLayer].select:
					selectedVerts.append(loop[uvLayer].uv)
					print("Vert selected "+str(face.index))

			if len(selectedVerts) >= 2:
				print("Selected edge "+str(selectedVerts[0]))
				break;
			# break;
	
	if len(selectedVerts) >= 2:
		diff = selectedVerts[1] - selectedVerts[0]
		angle = math.atan2(diff.y, diff.x)%(math.pi/2)
		print("edges: "+str(diff)+" = "+str(angle * 180 / math.pi))

		bpy.ops.uv.select_linked(extend=False)

		bpy.context.space_data.pivot_point = 'CURSOR'
		bpy.ops.uv.cursor_set(location=selectedVerts[0] + diff/2)

		if angle >= (math.pi/4):
			angle = angle - (math.pi/2)

		bpy.ops.transform.rotate(value=angle, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')

		# angle = math.atan2


		# isUVFaceSelected = True;
		# for loop in face.loops:
		# 	if loop[uvLayer].select is False:
		# 		isUVFaceSelected = False;
		# 		continue

	#Restore selection
	utilities_uv.selectionRestore()