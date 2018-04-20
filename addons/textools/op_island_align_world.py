import bpy
import os
import bmesh
import math
import operator
from mathutils import Vector
from collections import defaultdict
from itertools import chain # 'flattens' collection of iterables

from . import utilities_uv



class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_world"
	bl_label = "Align World"
	bl_description = "Align selected UV islands to world / gravity directions"
	bl_options = {'REGISTER', 'UNDO'}
	
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


		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False


		# if bpy.context.scene.tool_settings.uv_select_mode != 'FACE':
		#  	return False

		# if bpy.context.scene.tool_settings.use_uv_select_sync:
		# 	return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}



def main(context):
	print("--------------------------- Executing aling_world")

	#Store selection
	utilities_uv.selection_store()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	#Only in Face or Island mode
	if bpy.context.scene.tool_settings.uv_select_mode is not 'FACE' or 'ISLAND':
		bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	
	islands = utilities_uv.getSelectionIslands()

	print("Clusters: {}x".format(len(islands)))

	obj  = bpy.context.object

	for faces in islands:
		# Get average viewport normal of UV island
		avg_normal = Vector((0,0,0))
		for face in faces:
			avg_normal+=face.normal
		avg_normal/=len(faces)

		avg_normal = (obj.matrix_world*avg_normal).normalized()

		# Which Side
		x = 0
		y = 1
		z = 2
		max_size = max(abs(avg_normal.x), abs(avg_normal.y), abs(avg_normal.z))
		if(abs(avg_normal.x) == max_size):
			print("x normal")
			align_island(obj, uvLayer, faces, y, z)

		elif(abs(avg_normal.y) == max_size):
			print("y normal")
			align_island(obj, uvLayer, faces, x, z)

		elif(abs(avg_normal.z) == max_size):
			print("z normal")
			align_island(obj, uvLayer, faces, x, y)

		print("align island: faces {}x n:{}, max:{}".format(len(faces), avg_normal, max_size))

	

	#Restore selection
	utilities_uv.selection_restore()



def align_island(obj, uvLayer, faces, x=0, y=1):

	# Find lowest and highest verts
	minmax_val  = [0,0]
	minmax_vert = [None, None]

	print("faces {}x".format(len(faces)))




	vert_to_uv = {}
	uv_to_vert = {}

	processed = []
	for face in faces:

		# Collect UV to Vert
		for loop in face.loops:
			vert = loop.vert
			uv = loop[uvLayer]
			# vert_to_uv
			if vert not in vert_to_uv:
				vert_to_uv[vert] = [uv];
			else:
				vert_to_uv[vert].append(uv)
			# uv_to_vert
			if uv not in uv_to_vert:
				uv_to_vert[ uv ] = vert;


		for vert in face.verts:
			if vert not in processed:
				processed.append(vert)

				vert_y = (obj.matrix_world * vert.co)[y]

				if not minmax_vert[0]:
					minmax_vert[0] = vert
					minmax_val[0] = vert_y
					continue

				if not minmax_vert[1]:
					minmax_vert[1] = vert
					minmax_val[1] = vert_y
					continue

				if vert_y < minmax_val[0]:
					# Not yet defined or smaller
					minmax_vert[0] = vert
					minmax_val[0] = vert_y
					continue

				elif vert_y > minmax_val[1]:
					minmax_vert[1] = vert
					minmax_val[1] = vert_y
					continue

	if minmax_vert[0] and minmax_vert[1]:
		print("Min {} , Max {} ".format(minmax_vert[0].index, minmax_vert[1].index))
		
		vert_A = minmax_vert[0]
		vert_B = minmax_vert[1]
		uv_A = vert_to_uv[vert_A][0]
		uv_B = vert_to_uv[vert_B][0]

		delta_verts = Vector((
			vert_B.co[x] - vert_A.co[x],
			vert_B.co[y] - vert_A.co[y]
		))

		delta_uvs = Vector((
			uv_B.uv.x - uv_A.uv.x,
			uv_B.uv.y - uv_A.uv.y,

		))
		# Get angles
		angle_vert = math.atan2(delta_verts.y, delta_verts.x)
		angle_uv = math.atan2(delta_uvs.y, delta_uvs.x)

		angle_delta = angle_vert - angle_uv

		print("Delta {} | {}".format(angle_vert*180/math.pi, angle_uv*180/math.pi))
		print("Delta Angle {}".format(angle_delta*180/math.pi))

		bpy.context.space_data.pivot_point = 'MEDIAN'
		bpy.ops.transform.rotate(value=angle_delta, axis=(0, 0, 1))
		# bpy.ops.transform.rotate(value=0.58191, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SPHERE', proportional_size=0.0267348)
