import bpy
import bmesh
import operator
import time
import math
from mathutils import Vector

def get_object_texture_image(obj):

	print("Get img for '{}'".format(obj.name))

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