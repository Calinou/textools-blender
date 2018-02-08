import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_from_elements"
	bl_label = "Color Elements"
	bl_description = "Assign a color ID to each mesh element"
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
	
	# Collect groups
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	faces_indices_processed = []
	groups = []

	for face in bm.faces:
		if face.index not in faces_indices_processed:
			# Select face & extend
			bpy.ops.mesh.select_all(action='DESELECT')
			face.select = True
			bpy.ops.mesh.select_linked(delimit={'NORMAL'})

			faces = [f.index for f in bm.faces if (f.select and f.index not in faces_indices_processed)]
			for f in faces:
				faces_indices_processed.append(f)
			groups.append(faces)


	# Assign Groups to colors
	index_color = 0
	for group in groups:
		# rebuild bmesh data (e.g. left edit mode previous loop)
		bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
		if hasattr(bm.faces, "ensure_lookup_table"): 
			bm.faces.ensure_lookup_table()

		# Select group
		bpy.ops.mesh.select_all(action='DESELECT')
		for index_face in group:
			bm.faces[index_face].select = True

		# Assign to selection
		bpy.ops.uv.textools_color_assign(index=index_color)

		index_color = (index_color+1) % bpy.context.scene.texToolsSettings.color_ID_count

	bpy.ops.object.mode_set(mode='OBJECT')



# def get_bounds(faces):
# 	boundsMin = Vector((99999999.0,99999999.0))
# 	boundsMax = Vector((-99999999.0,-99999999.0))
# 	for face in faces:
# 		center = face.calc_center_bounds
# 		boundsMin.x = min(boundsMin.x, center.x)
# 		boundsMin.y = min(boundsMin.y, center.y)
# 		boundsMax.x = max(boundsMax.x, center.x)
# 		boundsMax.y = max(boundsMax.y, center.y)

# 	bbox = {}
# 	bbox['min'] = boundsMin
# 	bbox['max'] = boundsMax
# 	bbox['width'] = (boundsMax - boundsMin).x
# 	bbox['height'] = (boundsMax - boundsMin).y

# 	return bbox;