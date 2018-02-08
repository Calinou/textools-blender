import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict

from . import utilities_color
from . import utilities_bake
from . import utilities_ui


class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_convert_to_vertex_colors"
	bl_label = "Pack Texture"
	bl_description = "Pack ID Colors into single texture and UVs"
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
		convert_vertex_colors(self, context)
		return {'FINISHED'}



def convert_vertex_colors(self, context):
	obj = bpy.context.active_object
	name = material_prefix+obj.name

	if obj.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')

	'''

	# Edit mesh
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
	bpy.ops.mesh.select_all(action='SELECT')
	# bpy.ops.uv.smart_project(angle_limit=1)
	bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.0078)


	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify();

	for face in bm.faces:
		index = face.material_index

		# Get UV coordinates for index
		x = index%size_square
		y = math.floor(index/size_square)

		x*= (size_pixel / size_image_pow) 
		y*= (size_pixel / size_image_pow)
		x+= size_pixel/size_image_pow/2
		y+= size_pixel/size_image_pow/2

		for loop in face.loops:
			loop[uvLayer].uv = (x, y)

	# Remove Slots & add one
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.uv.textools_color_clear()
	bpy.ops.object.material_slot_add()


	'''