import bpy
import bmesh
import operator
import time
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings


material_prefix = "TT_color_"



def assign_slot(obj, index):
	if index < len(obj.material_slots):
		obj.material_slots[index].material = get_material(index)
		
		# Verify color
		assign_color(index)



def assign_color(index):
	material = get_material(index)
	if material:
		# material.use_nodes = False
		
		rgb = get_color(index)
		rgba = (rgb[0], rgb[1], rgb[2], 1)

		if material.use_nodes and bpy.context.scene.render.engine == 'CYCLES':
			# Cycles material (Preferred for baking)
			material.node_tree.nodes["Diffuse BSDF"].inputs[0].default_value = rgba

		elif not material.use_nodes and bpy.context.scene.render.engine == 'BLENDER_RENDER' or bpy.context.scene.render.engine == 'BLENDER_GAME':
			# Legacy render engine, not suited for baking
			material.diffuse_color = rgb
			material.use_shadeless = True



		# if material.use_nodes:

		# else:
		# 	material.diffuse_color = get_color(index)


		
			# These viewports require lights or unlit shading to be visible
			
		# elif  bpy.context.scene.render.engine == 'CYCLES':
			#Prevents bug where after a color bake would not bake updated color 
			# material.use_nodes = True 

		# material.update_tag(refresh='OBJECT')
		# material.tag = True



def get_material(index):
	name = get_name(index)

	# Material already exists?
	if name in bpy.data.materials:
		material = bpy.data.materials[name];

		# Check for incorrect matreials for current render engine
		if not material:
			replace_material(index)

		if not material.use_nodes and bpy.context.scene.render.engine == 'CYCLES':
			replace_material(index)

		elif material.use_nodes and bpy.context.scene.render.engine == 'BLENDER_RENDER' or bpy.context.scene.render.engine == 'BLENDER_GAME':
			replace_material(index)

		else:
			return material;

	print("Could nt find {} , create a new one??".format(name))

	material = create_material(index)
	assign_color(index)
	return material


# Replaace an existing material with a new one
# This is sometimes necessary after switching the render engine
def replace_material(index):
	name = get_name(index)

	print("Replace material and create new")
	# ....Clear exisitng matierals and replace in all objects that use it (e.g. material slots)

	# Check if material exists
	if name in bpy.data.materials:
		material = bpy.data.materials[name];

		# Collect material slots we have to re-assign
		slots = []
		for obj in bpy.context.scene.objects: 
			for slot in obj.material_slots:
				if slot.material == material:
					slots.append(slot)

		# Get new material
		material.user_clear()
		bpy.data.materials.remove(material)
		
		# Re-assign new material
		material = get_material(index)
		for slot in slots:
			slot.material = material;



def create_material(index):
	name = get_name(index)

	# Create new image instead
	material = bpy.data.materials.new(name)
	material.preview_render_type = 'FLAT'

	if bpy.context.scene.render.engine == 'CYCLES':
		# Cycles: prefer nodes as it simplifies baking
		material.use_nodes = True 

	return material



def get_name(index):
	return (material_prefix+"{:02d}").format(index)



def get_color(index):
	if index < bpy.context.scene.texToolsSettings.color_ID_count:
		return getattr(bpy.context.scene.texToolsSettings, "color_ID_color_{}".format(index))
	return (0, 0, 0)



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



def color_to_hex(color):
	r = int(color[0]*255)
	g = int(color[1]*255)
	b = int(color[2]*255)
	return "#{:02X}{:02X}{:02X}".format(r,g,b)