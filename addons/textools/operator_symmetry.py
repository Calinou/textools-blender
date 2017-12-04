import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class operator_symmetry(bpy.types.Operator):
	"""UV Operator description"""
	bl_idname = "uv.textools_symmetry"
	bl_label = "Symmetry"
	bl_description = "Mirrors selected faces to other half or averages based on selected edge center"

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

		if bpy.context.scene.tool_settings.uv_select_mode != 'EDGE' and bpy.context.scene.tool_settings.uv_select_mode != 'FACE':
		 	return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing operator_symmetry")

	#Store selection
	utilities_uv.selectionStore()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	if bpy.context.scene.tool_settings.uv_select_mode == 'FACE':
		print( "1.) Get Face edge bounds selection")

		# Get selected UV faces
		selected_faces = []
		for face in bm.faces:
			if face.select:
				# Are all UV faces selected?
				countSelected = 0
				for loop in face.loops:
					if loop[uvLayer].select:
						countSelected+=1
						# print("Vert selected "+str(face.index))
				if countSelected == len(face.loops):
					selected_faces.append(face)

		# Select faces
		bpy.ops.mesh.select_all(action='DESELECT')
		for face in selected_faces:
			face.select = True

		# Get Face Bounds
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
		bpy.ops.mesh.region_to_loop()

		selected_verts = [v for v in bm.verts if v.select]

		print("verts "+str(len(selected_verts)))

		# https://blender.stackexchange.com/questions/53709/bmesh-how-to-map-vertex-based-uv-coordinates-to-loops
		
		bpy.ops.mesh.select_all(action='SELECT')


		bpy.context.scene.tool_settings.uv_select_mode = "VERTEX"
		bpy.ops.uv.select_all(action='DESELECT')
		

		for face in bm.faces:
			for vert, loop in zip(face.verts, face.loops):
				if vert in selected_verts:
					print("Yes "+str(vert.index))
					loop[uvLayer].select = True
				# loop[uv_layer].uv = get_uvs(vert.index, face.index,...)
