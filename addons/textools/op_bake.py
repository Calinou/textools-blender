import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi
from random import random
from mathutils import Color

from . import settings
from . import utilities_bake

# Get last-loaded material, such as ~.002.
# def _getAppendedMaterial(material_name):
#     # Get material name list.
#     material_names = [m.name for m in bpy.data.materials if material_name in m.name]
#     # Return last material in the sorted order.
#     material_names.sort()
#     return material_names[-1]




class op_setup_material(bpy.types.Operator):
	bl_idname = "uv.textools_bake_setup_material"
	bl_label = "Setup Material"
	bl_description = "Setup Bake materials"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		execute_setup_material(context)
		return {'FINISHED'}



def execute_setup_material(context):
	print("Executing operator_bake_render main()")
	print("Mode: "+str(context.scene.texToolsSettings.baking_mode))



class op_bake(bpy.types.Operator):
	bl_idname = "uv.textools_bake"
	bl_label = "Bake"
	bl_description = "Bake selected objects"

	@classmethod
	def poll(cls, context):
		if len(bpy.context.selected_objects) == 0:
			return False

		return True

	def execute(self, context):
		utilities_bake.store_bake_settings()
		execute_render(
			self, context, settings.bake_mode, 
			bpy.context.scene.texToolsSettings.size[0], bpy.context.scene.texToolsSettings.size[1], 
			bpy.context.scene.texToolsSettings.samples,
			bpy.context.scene.texToolsSettings.ray_distance
		)
		# utilities_bake.restore_bake_settings()
		return {'FINISHED'}







def execute_render(self, context, mode, width, height, samples, ray_distance):

	# Setup
	if bpy.context.scene.render.engine != 'CYCLES':
		bpy.context.scene.render.engine = 'CYCLES'
	bpy.context.scene.cycles.samples = samples

	if bpy.context.object.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')

	


	sets = utilities_bake.get_bake_pairs()

	print("________________________________\nBake {}x '{}'".format(len(sets), mode))

	for set in sets:
		name = "{}_{}".format(set.name, mode)
		path = bpy.path.abspath("//{}.tga".format(name))

		# Requires 1+ low poly objects
		if len(set.objects_low) == 0:
			self.report({'ERROR_INVALID_INPUT'}, "No low poly object selected for {}".format(set.name) )
			return

		# Check for UV maps
		for obj in set.objects_low:
			if len(obj.data.uv_layers) == 0:
				print("ERROR: NO UV MAP FOUND FOR {} ".format(obj.name))
				return

		# Assign Material
		material = get_material(mode)
		material_empty = bpy.data.materials.new(name="bakemat")
		material_empty.use_nodes = True

		if len(set.objects_high) == 0:
			# Assign material to lowpoly
			for obj in set.objects_low:
				assign_vertex_colors(obj, mode)
				assign_material(obj, material if material != None else material_empty)
		else:
			# Low poly require empty material to bake into image
			for obj in set.objects_low:
				assign_material(obj, material_empty)

			# Assign material to highpoly
			for obj in set.objects_high:
				assign_vertex_colors(obj, mode)
				assign_material(obj, material)

		# BRM BakeUI: https://github.com/leukbaars/BRM-BakeUI/blob/master/BRM_BakeUI.py


		# Setup Material
		image = bpy.data.images.new(name, width=width, height=height) #context.scene.bakeWidth
		# image = bpy.ops.image.new(name=name, width=width, height=height, color= (0.5, 0.5, 1.0, 1.0)) #context.scene.bakeWidth
		# if mode is 'normal':
			# image.paste(, [0,0,image.size[0],image.size[1]])


		image.file_format = 'TARGA'
		image.filepath_raw = path

		if len(set.objects_low[0].data.materials) <= 0:
			print("ERROR, need spare material to setup active image texture to bake!!!")
		else:
			tree = set.objects_low[0].data.materials[0].node_tree
			node = tree.nodes.new("ShaderNodeTexImage")
			node.select = True
			node.image = image
			node.name = "TT_bake_image"
			tree.nodes.active = node


		print("Bake {} = {}".format(set.name, name))

		for i in range(len(set.objects_low)):
			obj_low = set.objects_low[i]
			obj_cage = None if i >= len(set.objects_cage) else set.objects_cage[i]

			bpy.ops.object.select_all(action='DESELECT')
			for obj_high in set.objects_high:
				obj_high.select = True
			obj_low.select = True
			bpy.context.scene.objects.active = obj_low

			cycles_bake(mode, samples, ray_distance, len(set.objects_high) > 0, obj_cage)

		# for obj_low in set.objects_low:
		# 	# Select Objects (High first, then current low)
		# 	bpy.ops.object.select_all(action='DESELECT')
		# 	for obj_high in set.objects_high:
		# 		obj_high.select = True
		# 	obj_low.select = True
		# 	bpy.context.scene.objects.active = obj_low

		# 	print("Now bake '{}'".format(path))
		# 	cycles_bake(mode, samples, len(set.objects_high) > 0, None if set)
			

		# 
		# image.save()



def cycles_bake(mode, samples, ray_distance, isMulti, obj_cage):
	# Set samples
	if mode == 'ao' or mode == 'normal':
		bpy.context.scene.cycles.samples = samples
	else:
		bpy.context.scene.cycles.samples = 1

	# Bake margin to texture size to fully bleed out
	if mode == 'id':
		bpy.context.scene.render.bake.margin = bpy.context.scene.texToolsSettings.padding
	else:
		bpy.context.scene.render.bake.margin = max(bpy.context.scene.texToolsSettings.size[0], bpy.context.scene.texToolsSettings.size[1])

	# Bake Type
	bake_type = 'EMIT'
	if mode == 'ao':
		bake_type = 'AO'
	elif mode == 'normal':
		bake_type = 'NORMAL'

	# Bake with Cage?
	if obj_cage is None:
		bpy.ops.object.bake(type=bake_type, use_clear=True, cage_extrusion=ray_distance, use_selected_to_active=isMulti, normal_space='OBJECT')
	else:
		bpy.ops.object.bake(type=bake_type, use_clear=True, cage_extrusion=ray_distance, use_cage=True, cage_object=obj_cage.name, use_selected_to_active=isMulti, normal_space='OBJECT')



def assign_vertex_colors(obj, mode):
	# Assign Vertex Colors
	if mode == 'worn' or mode == 'cavity' or mode == 'dust':
		setup_vertex_color_dirty(obj)
	elif mode == 'id':
		setup_vertex_color_ids(obj)



def assign_material(obj, material):
	if material is None:
		return

	# Assign material
	if len(obj.data.materials) == 0:
		obj.data.materials.append(material)
	else:
		obj.data.materials[0] = material




def get_material(mode):
	if mode == 'normal' or mode == 'ao':
		return None # No material setup requires

	name_material = "bake_{}".format(mode)
	path = os.path.join(os.path.dirname(__file__), "resources/materials.blend")+"\\Material\\"
	if bpy.data.materials.get(name_material) is None:
		print("Material not yet loaded: "+mode)
		bpy.ops.wm.append(filename=name_material, directory=path, link=False, autoselect=False)

	return bpy.data.materials.get(name_material)




def setup_vertex_color_dirty(obj):
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj
	bpy.ops.object.mode_set(mode='EDIT')

	# Fill white then, 
	bm = bmesh.from_edit_mesh(obj.data)
	colorLayer = bm.loops.layers.color.verify()

	color = (1, 1, 1)
	for face in bm.faces:
		for loop in face.loops:
				loop[colorLayer] = color
	obj.data.update()

	# Back to object mode
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.paint.vertex_color_dirt()



def setup_vertex_color_ids(obj):
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj
	bpy.ops.object.mode_set(mode='EDIT')

	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

	bm = bmesh.from_edit_mesh(obj.data)
	colorLayer = bm.loops.layers.color.verify()

	# Collect elements
	processed = set([])
	groups = []
	for face in bm.faces:

		if face not in processed:
			bpy.ops.mesh.select_all(action='DESELECT')
			face.select = True
			bpy.ops.mesh.select_linked(delimit={'NORMAL'})
			linked = [face for face in bm.faces if face.select]

			for link in linked:
				processed.add(link)
			groups.append(linked)

	# Color each group
	for i in range(0,len(groups)):
		color = Color()
		color.hsv = ( i / (len(groups)) ), 1.0, 1

		for face in groups[i]:
			for loop in face.loops:
				loop[colorLayer] = color
	obj.data.update()

	# Back to object mode
	bpy.ops.object.mode_set(mode='OBJECT')
