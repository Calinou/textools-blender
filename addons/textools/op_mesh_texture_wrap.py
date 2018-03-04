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
	if obj_uv.data.shape_keys.key_blocks["model"].value > 0:
		# Undo wrapping
		obj_uv.data.shape_keys.key_blocks["model"].value = 0
		return
	
	# Clear first shape transition
	obj_uv.data.shape_keys.key_blocks["model"].value = 0

	min_z = obj_uv.location.z
	max_z = obj_uv.location.z
	for i in range(len(obj_textures)):
		obj = obj_textures[i]
		
		# Min Max Z
		if i == 0:
			min_z = get_bbox(obj)['min'].z
			max_z = get_bbox(obj)['max'].z
		else:
			min_z = min(min_z, get_bbox(obj)['min'].z)
			max_z = max(max_z, get_bbox(obj)['max'].z)

		# Removeexistingmesh form modifiers
		for modifier in obj.modifiers:
			print("M {}".format(modifier.type))
			if modifier.type == 'MESH_DEFORM':
				obj.modifiers.remove(modifier)
				break
		
	# Set thickness
	obj_uv.modifiers["Solidify"].thickness = (max_z - min_z) * 1.0

	# Set offset
	p_z = (obj_uv.location.z - min_z) / (max_z - min_z)
	obj_uv.modifiers["Solidify"].offset = -(p_z-0.5)/0.5

	for obj in obj_textures:
		use_dynamic_bind = len(obj.modifiers) > 1

		# Add mesh modifier
		obj.select = True
		bpy.context.scene.objects.active = obj
		bpy.ops.object.modifier_add(type='MESH_DEFORM')
		bpy.context.object.modifiers["MeshDeform"].object = obj_uv
		bpy.context.object.modifiers["MeshDeform"].use_dynamic_bind = use_dynamic_bind
		bpy.ops.object.meshdeform_bind(modifier="MeshDeform")

		print(">>>"+str(bpy.context.object.modifiers["MeshDeform"]))





	
	obj_uv.data.shape_keys.key_blocks["model"].value = 1

	# Set morph back to 0
	# measure bounds (world) of mesh textures
	# set solidify size to size + offset to capture fully

	# unbind if already bind
	# Apply mesh deform modifier (if not existing)
	# enable dynamic bind if other modifiers
	# Set morph to 1
	
	# bind

	# use:
	# bpy.context.object.modifiers["MeshDeform"].use_dynamic_bind = True
	# bpy.context.object.modifiers["MeshDeform"].show_on_cage = True


def get_bbox(obj):
	corners = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]

	# Get world space Min / Max
	box_min = Vector((corners[0].x, corners[0].y, corners[0].z))
	box_max = Vector((corners[0].x, corners[0].y, corners[0].z))
	for corner in corners:
		# box_min.x = -8
		box_min.x = min(box_min.x, corner.x)
		box_min.y = min(box_min.y, corner.y)
		box_min.z = min(box_min.z, corner.z)
		
		box_max.x = max(box_max.x, corner.x)
		box_max.y = max(box_max.y, corner.y)
		box_max.z = max(box_max.z, corner.z)

	return {
		'min':box_min, 
		'max':box_max, 
		'size':(box_max-box_min),
		'center':box_min+(box_max-box_min)/2
	}
