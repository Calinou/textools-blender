import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi
import math

from . import utilities_mesh_texture




class op(bpy.types.Operator):
	bl_idname = "uv.textools_mesh_texture_trim"
	bl_label = "Trim"
	bl_description = "Trim Mesh Texture"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		# Wrap texture mesh around UV mesh
		if len(bpy.context.selected_objects) >= 2:
			if utilities_mesh_texture.find_uv_mesh(bpy.context.selected_objects):
				return True

		return False

	def execute(self, context):
		trim(self)
		return {'FINISHED'}



def trim(self):
	# Wrap the mesh texture around the 
	print("Trim Mesh Texture :)")

	# Collect UV mesh
	obj_uv = utilities_mesh_texture.find_uv_mesh(bpy.context.selected_objects)
	if not obj_uv:
		self.report({'ERROR_INVALID_INPUT'}, "No UV mesh found" )
		return

	# Collect texture meshes
	obj_textures = []
	for obj in bpy.context.selected_objects:
		if obj != obj_uv:
			if obj.type == 'MESH':
				obj_textures.append(obj)

	if len(obj_textures) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No meshes found for mesh textures" )
		return

	print("Wrap {} texture meshes".format(len(obj_textures)))
	# Clear first shape transition
	obj_uv.data.shape_keys.key_blocks["model"].value = 0

	# Apply bool modifier to trim
	for obj in obj_textures:
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True
		bpy.context.scene.objects.active = obj
		# bpy.ops.object.convert(target='MESH')

		bpy.ops.object.modifier_add(type='BOOLEAN')
		bpy.context.object.modifiers["Boolean"].object = obj_uv


