import bpy
import bmesh
import operator
import time
import math
from mathutils import Vector

def get_object_texture_image(obj):

	# Search in material & texture slots
	for slot_mat in obj.material_slots:
		for slot_tex in slot_mat.material.texture_slots:
			if slot_tex and hasattr(slot_tex.texture , 'image'):
				return slot_tex.texture.image

	# Search in UV editor background image
	if len(obj.data.uv_textures) > 0:
		if len(obj.data.uv_textures[0].data) > 0:
			if obj.data.uv_textures[0].data[0].image:
				return obj.data.uv_textures[0].data[0].image

	return None


def get_area_triangle(A,B,C):
	# Heron's formula: http://www.1728.org/triang.htm
	# area = square root (s • (s - a) • (s - b) • (s - c))
	a = (B-A).length
	b = (C-B).length
	c = (A-C).length
	s = (a+b+c)/2
	return math.sqrt(s * (s-a) * (s-b) * (s-c))