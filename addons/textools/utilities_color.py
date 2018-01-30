import bpy
import bmesh
import operator
import time
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings


material_prefix = "TT_color_"



def hex_to_color(hex):
	gamma = 2.2
	hex = hex.strip('#')
	lv = len(hex)
	fin = list(int(hex[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
	r = pow(fin[0] / 255, gamma)
	g = pow(fin[1] / 255, gamma)
	b = pow(fin[2] / 255, gamma)
	fin.clear()
	fin.append(r)
	fin.append(g)
	fin.append(b)
	# fin.append(1.0)
	return tuple(fin)



def get_material_name(index):
	return material_prefix+str(index)



def get_color(index):
	if index < bpy.context.scene.texToolsSettings.color_ID_count:
		return getattr(bpy.context.scene.texToolsSettings, "color_ID_color_{}".format(index))
	return (0, 0, 0)



def get_material(index):
	name = get_material_name(index)

	# Material already exists?
	if name in bpy.data.materials:
		return bpy.data.materials[name];


	print("Could nt find {} , create a new one??".format(name))

	# Create new image instead
	material = bpy.data.materials.new(name)
	assign_material_color(index)
	return material


def assign_material_color(index):
	material = get_material(index)
	if material:
		# material.use_nodes = False
		material.diffuse_color = get_color(index)

		if bpy.context.scene.render.engine == 'BLENDER_RENDER' or bpy.context.scene.render.engine == 'BLENDER_GAME':
			# These viewports require lights or unlit shading to be visible
			material.use_shadeless = True