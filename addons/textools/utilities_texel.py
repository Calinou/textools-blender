import bpy
import bmesh
import operator
import time
import math
from mathutils import Vector


image_material_prefix = "TT_checker_"


# Return all faces of selected objects or only selected faces
def get_selected_object_faces():
	object_faces_indexies = {}

	previous_mode = bpy.context.object.mode

	if bpy.context.object.mode == 'EDIT':
		# Only selected Mesh faces
		obj = bpy.context.active_object
		if obj.type == 'MESH' and obj.data.uv_layers:
			bm = bmesh.from_edit_mesh(obj.data)
			bm.faces.ensure_lookup_table()
			object_faces_indexies[obj] = [face.index for face in bm.faces if face.select]
	else:
		# Selected objects with all faces each
		selected_objects = [obj for obj in bpy.context.selected_objects]
		for obj in selected_objects:
			if obj.type == 'MESH' and obj.data.uv_layers:
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.scene.objects.active = obj
				obj.select = True

				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(obj.data)
				bm.faces.ensure_lookup_table()
				object_faces_indexies[obj] = [face.index for face in bm.faces]

	bpy.ops.object.mode_set(mode=previous_mode)

	return object_faces_indexies



def get_object_texture_image(obj):

	print("Get img for '{}'".format(obj.name))

	previous_mode = bpy.context.active_object.mode
	bpy.ops.object.mode_set(mode='OBJECT')


	# Search in material & texture slots
	for slot_mat in obj.material_slots:
		# Check for traditional texture slots in material
		for slot_tex in slot_mat.material.texture_slots:
			if slot_tex and slot_tex.texture and hasattr(slot_tex.texture , 'image'):
				return slot_tex.texture.image
		
		# Check if material uses Nodes
		if slot_mat.material:
			if hasattr(slot_mat.material , 'node_tree'):
				if slot_mat.material.node_tree:
					for node in slot_mat.material.node_tree.nodes:
						if type(node) is bpy.types.ShaderNodeTexImage:
							if node.image:
								return node.image

	# Search in UV editor background image
	if len(obj.data.uv_textures) > 0:
		if len(obj.data.uv_textures[0].data) > 0:
			if obj.data.uv_textures[0].data[0].image:
				return obj.data.uv_textures[0].data[0].image

	return None



def image_resize(image, size_x, size_y):
	if image and image.source == 'FILE' or image.source == 'GENERATED':
		image.generated_width = int(size_x)
		image.generated_height = int(size_y)
		image.scale( int(size_x), int(size_y) )
	
	

def checker_images_cleanup():
	# Clean up unused images
	for image in bpy.data.images:
		if image_material_prefix in image.name:
			if not image.users:
				print("Remove unused image {}".format(image.name))
				bpy.data.images.remove(image)

			# Check if name missmatches size
			name = get_checker_name(image.size[0], image.size[1])
			if image.name != name:
				# In cycles find related material as well
				if image.name in bpy.data.materials:
					bpy.data.materials[image.name].name = name
				image.name = name


def get_checker_name(size_x, size_y):
	return (image_material_prefix+"{}x{}").format(size_x, size_y)



def get_area_triangle_uv(A,B,C, size_x, size_y):
	scale_x = size_x / max(size_x, size_y)
	scale_y = size_y / max(size_x, size_y)
	A.x/=scale_x
	B.x/=scale_x
	C.x/=scale_x
	
	A.y/=scale_y
	B.y/=scale_y
	C.y/=scale_y

	return get_area_triangle(A,B,C)



def get_area_triangle(A,B,C):
	# Heron's formula: http://www.1728.org/triang.htm
	# area = square root (s • (s - a) • (s - b) • (s - c))
	a = (B-A).length
	b = (C-B).length
	c = (A-C).length
	s = (a+b+c)/2
	return math.sqrt(s * (s-a) * (s-b) * (s-c))