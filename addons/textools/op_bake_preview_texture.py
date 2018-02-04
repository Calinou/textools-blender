import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict

from . import utilities_color
from . import utilities_bake

material_prefix = "TT_atlas_"
gamma = 2.2

class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_preview_texture"
	bl_label = "Preview Texture"
	bl_description = "Preview the current UV image view background image on the selected object."
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

			#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 

		# Only when we have a background image
		for area in bpy.context.screen.areas:
			if area.type == 'IMAGE_EDITOR':
				return area.spaces[0].image

		return False
	
	def execute(self, context):
		preview_texture(self, context)
		return {'FINISHED'}



def preview_texture(self, context):
	obj = bpy.context.active_object

	if obj.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')
	
	print("Preview texture")


	image = None
	for area in bpy.context.screen.areas:
		if area.type == 'IMAGE_EDITOR':
			image = area.spaces[0].image
			break

	if image:
		print("Assign image {}".format(image.name))

		for i in range(len(obj.material_slots)):
			bpy.ops.object.material_slot_remove()


		#Create material with image
		bpy.ops.object.material_slot_add()
		obj.material_slots[0].material = utilities_bake.get_image_material(image)
		

		#Change View mode to TEXTURED
		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				for space in area.spaces:
					if space.type == 'VIEW_3D':
						space.viewport_shade = 'MATERIAL'

		'''
		# Get Material
		material = None
		if image.name in bpy.data.materials:
			material = bpy.data.materials[image.name]
		else:
			material = bpy.data.materials.new(image.name)
			material.use_nodes = True

		tree = material.node_tree

		node_image = tree.nodes.new("ShaderNodeTexImage")
		node_image.name = "bake"
		node_image.select = True
		node_image.image = image
		tree.nodes.active = node_image

		node_diffuse = tree.nodes['Diffuse BSDF']


		tree.links.new(node_image.outputs[0], node_diffuse.inputs[0])

		return material
		'''


	#Display UVs
	# bpy.ops.object.mode_set(mode='EDIT')

