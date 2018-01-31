import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_elements_setup"
	bl_label = "Color Elements"
	bl_description = "Color unique mesh elements with ID Colors."
	bl_options = {'REGISTER', 'UNDO'}
	

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if bpy.context.active_object not in bpy.context.selected_objects:
			return False

		if len(bpy.context.selected_objects) != 1:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		return True
	
	def execute(self, context):
		setup_elements(self, context)
		return {'FINISHED'}



def setup_elements(self, context):
	obj = bpy.context.active_object
	
	# Setup Edit & Face mode
	if obj.mode != 'EDIT':
		bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
	


	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);


	# Collect groups
	faces_processed = []
	groups = []

	for face in bm.faces:
		if face not in faces_processed:
			# Select face & extend
			bpy.ops.mesh.select_all(action='DESELECT')
			face.select = True
			bpy.ops.mesh.select_linked(delimit={'NORMAL'})

			faces = [f for f in bm.faces if (f.select and f not in faces_processed)]
			for f in faces:
				faces_processed.append(f)
			groups.append(faces)




	index = 0
	for group in groups:
		# Select group
		bpy.ops.mesh.select_all(action='DESELECT')
		for face in group:
			face.select = True

		bpy.ops.uv.textools_color_assign(index=index)
		index = (index+1) % bpy.context.scene.texToolsSettings.color_ID_count

	# for face in bm.faces:
	# 	if face not in faces_processed:
	# 		# Select face & extend
	# 		bpy.ops.mesh.select_all(action='DESELECT')
	# 		face.select = True
	# 		bpy.ops.mesh.select_linked(delimit={'NORMAL'})

	# 		#Select similar by perimeter
	# 		bpy.ops.mesh.select_similar(type='PERIMETER', threshold=0.01)
	# 		bpy.ops.mesh.select_linked(delimit={'NORMAL'})

	# 		faces = [f for f in bm.faces if (f.select and f not in faces_processed)]

	# 		for f in faces:
	# 			faces_processed.append(f)

	# 		groups.append(faces)

	# print("Elements {}x".format(len(groups)))

	


	bpy.ops.object.mode_set(mode='OBJECT')

	# bpy.ops.mesh.select_linked_pick(deselect=False, delimit={'NORMAL'}, index=208)
	# bpy.ops.mesh.select_similar(type='AREA', threshold=0.01)



	# for face in bm.faces:
	# 	face.material_index = 0









def get_bounds(faces):
	boundsMin = Vector((99999999.0,99999999.0))
	boundsMax = Vector((-99999999.0,-99999999.0))
	for face in faces:
		center = face.calc_center_bounds
		boundsMin.x = min(boundsMin.x, center.x)
		boundsMin.y = min(boundsMin.y, center.y)
		boundsMax.x = max(boundsMax.x, center.x)
		boundsMax.y = max(boundsMax.y, center.y)

	bbox = {}
	bbox['min'] = boundsMin
	bbox['max'] = boundsMax
	bbox['width'] = (boundsMax - boundsMin).x
	bbox['height'] = (boundsMax - boundsMin).y

	return bbox;