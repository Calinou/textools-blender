import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi
import math
from . import utilities_mesh_texture


class op(bpy.types.Operator):
	bl_idname = "uv.textools_mesh_texture_wrap"
	bl_label = "Wrap Mesh Texture"
	bl_description = "Swap UV to XYZ coordinates"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		# Wrap texture mesh around UV mesh
		if len(bpy.context.selected_objects) >= 2:
			if utilities_mesh_texture.find_uv_mesh(bpy.context.selected_objects):
				return True

		return False

	def execute(self, context):
		wrap_mesh_texture(self)
		return {'FINISHED'}



def wrap_mesh_texture(self):
	# Wrap the mesh texture around the 
	print("Wrap Mesh Texture :)")

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

	# Undo wrapping
	if bpy.context.scene.texToolsSettings.meshtexture_wrap > 0:
		bpy.context.scene.texToolsSettings.meshtexture_wrap = 0
		# Remove Solidify and push modifiers
		return
	
	# Setup Thickness
	utilities_mesh_texture.uv_mesh_fit(obj_uv, obj_textures)

	
	for obj in obj_textures:
		# Delete previous modifiers
		for modifier in obj.modifiers:
			if modifier.type == 'MESH_DEFORM':
				obj.modifiers.remove(modifier)
				break

		# Add mesh modifier
		modifier_deform = obj.modifiers.new(name="MeshDeform", type='MESH_DEFORM')
		modifier_deform.object = obj_uv
		modifier_deform.use_dynamic_bind = len(obj.modifiers) > 1
		modifier_deform.precision = int(bpy.context.scene.texToolsSettings.meshtexture_precission)

		obj.select = True
		bpy.context.scene.objects.active = obj
		bpy.ops.object.meshdeform_bind(modifier="MeshDeform")

	# Apply wrapped morph state
	bpy.context.scene.texToolsSettings.meshtexture_wrap = 1
