import bpy
import bmesh
import operator
import time
from mathutils import Vector
from collections import defaultdict
from math import pi
from mathutils import Color

from . import settings
from . import utilities_color


keywords_low = ['lowpoly','low','lowp','lp','l']
keywords_high = ['highpoly','high','highp','hp','h']
keywords_cage = ['cage','c']
keywords_float = ['floater','float','f']

split_chars = [' ','_','.','-']



class BakeMode:
	material = ""					#Material name from external blend file
	type = 'EMIT'
	normal_space = 'TANGENT'
	setVColor = None				#Set Vertex color method
	color = (0.23, 0.23, 0.23, 1)	#Background color
	engine = 'CYCLES'				#render engine, by default CYCLES
	composite = None				#use composite scene to process end result
	params = []						#UI Parameters from scene settings

	def __init__(self, material="", type='EMIT', normal_space='TANGENT', setVColor=None, color= (0.23, 0.23, 0.23, 1), engine='CYCLES', params = [], composite=None):
		self.material = material
		self.type = type
		self.normal_space = normal_space
		self.setVColor = setVColor
		self.color = color
		self.engine = engine
		self.params = params
		self.composite = composite



def store_bake_settings():
	# Render Settings
	settings.bake_render_engine = bpy.context.scene.render.engine

	# Disable Objects that are meant to be hidden
	sets = settings.sets
	objects_sets = []
	for set in sets:
		for obj in set.objects_low:
			if obj not in objects_sets:
				objects_sets.append(obj)
		for obj in set.objects_high:
			if obj not in objects_sets:
				objects_sets.append(obj)
		for obj in set.objects_cage:
			if obj not in objects_sets:
				objects_sets.append(obj)

	settings.bake_objects_hide_render = []



	for obj in bpy.context.scene.objects:
		if obj.hide_render == False and obj not in objects_sets:
			# Check if layer is active
			for l in range(0, len(obj.layers)):
				if obj.layers[l] and bpy.context.scene.layers[l]:
					settings.bake_objects_hide_render.append(obj)
					break

	for obj in settings.bake_objects_hide_render:
		obj.hide_render = True
		# obj.cycles_visibility.shadow = False



def restore_bake_settings():
	# Render Settings
	if settings.bake_render_engine != '':
		bpy.context.scene.render.engine = settings.bake_render_engine

	# Restore Objects that were hidden for baking
	for obj in settings.bake_objects_hide_render:
		if obj:
			obj.hide_render = False
			# obj.cycles_visibility.shadow = True



stored_materials = {}
stored_material_faces = {}
def store_materials_clear():
	stored_materials.clear()
	stored_material_faces.clear()



def store_materials(obj):
	stored_materials[obj] = []
	stored_material_faces[obj] = []

	# Enter edit mode
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj

	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(obj.data);

	# for each slot backup the material 
	for s in range(len(obj.material_slots)):
		slot = obj.material_slots[s]

		stored_materials[obj].append(slot.material)
		stored_material_faces[obj].append( [face.index for face in bm.faces if face.material_index == s] )
		
		# print("Faces: {}x".format( len(stored_material_faces[obj][-1])  ))

		if slot and slot.material:
			slot.material.name = "backup_"+slot.material.name
			print("- Store {} = {}".format(obj.name,slot.material.name))

	# Back to object mode
	bpy.ops.object.mode_set(mode='OBJECT')



def restore_materials():
	for obj in stored_materials:
		# Enter edit mode
		bpy.context.scene.objects.active = obj
		bpy.ops.object.mode_set(mode='EDIT')
		bm = bmesh.from_edit_mesh(obj.data);

		# Restore slots
		for index in range(len(stored_materials[obj])):
			material = stored_materials[obj][index]
			faces = stored_material_faces[obj][index]
			
			if material:
				material.name = material.name.replace("backup_","")
				obj.material_slots[index].material = material

				# Face material indexies
				for face in bm.faces:
					if face.index in faces:
						face.material_index = index

		# Back to object mode
		bpy.ops.object.mode_set(mode='OBJECT')

		# Remove material slots if none before
		if len(stored_materials[obj]) == 0:
			for i in range(len(obj.material_slots)):
				bpy.ops.object.material_slot_remove()



def get_bake_name_base(obj):

	def remove_digits(name):
		# Remove blender naming digits, e.g. cube.001, cube.002,...
		if len(name)>= 4 and name[-4] == '.' and name[-3].isdigit() and name[-2].isdigit() and name[-1].isdigit():
			return name[:-4]
		return name

	# Reference parent as base name
	if obj.parent:
		return remove_digits(obj.parent.name).lower()

	# Reference group name as base name
	elif len(obj.users_group) == 1:
		return remove_digits(obj.users_group[0].name).lower()

	# Use Object name
	else:
		return remove_digits(obj.name).lower()



def get_bake_name(obj):
	# Get Basic name
	name = get_bake_name_base(obj)

	# Split by ' ','_','.' etc.
	split = name.lower()
	for char in split_chars:
		split = split.replace(char,' ')
	strings = split.split(' ')

	# Remove all keys from name
	keys = keywords_cage + keywords_high + keywords_low + keywords_float
	new_strings = []
	for string in strings:
		is_found = False
		for key in keys:
			if string == key:
				is_found = True
				break
		if not is_found:
			new_strings.append(string)
		else:
			# No more strings once key is found
			break

	return "_".join(new_strings)



def get_object_type(obj):

	name = get_bake_name_base(obj)

	# Detect by name pattern
	split = name.lower()
	for char in split_chars:
		split = split.replace(char,' ')
	strings = split.split(' ')

	# Detect float, more rare than low
	for string in strings:		
		for key in keywords_float:
			if key == string:
				return 'float'

	# Detect by modifiers
	if obj.modifiers:
		for modifier in obj.modifiers:
			if modifier.type == 'SUBSURF' and modifier.render_levels > 0:
				return 'high'
			elif modifier.type == 'BEVEL':
				return 'high'


	# Detect High first, more rare
	for string in strings:
		for key in keywords_high:
			if key == string:
				return 'high'
	
	# Detect cage, more rare than low
	for string in strings:		
		for key in keywords_cage:
			if key == string:
				return 'cage'

	

	# Detect low
	for string in strings:
		for key in keywords_low:
			if key == string:
				return 'low'


	# if nothing was detected, assume its low
	return 'low'



def get_bake_sets():
	filtered = {}
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			filtered[obj] = get_object_type(obj)
	
	groups = []
	# Group by names
	for obj in filtered:
		name = get_bake_name(obj)

		if len(groups)==0:
			groups.append([obj])
		else:
			isFound = False
			for group in groups:
				groupName = get_bake_name(group[0])
				if name == groupName:
					group.append(obj)
					isFound = True
					break

			if not isFound:
				groups.append([obj])

	# Sort groups alphabetically
	keys = [get_bake_name(group[0]) for group in groups]
	keys.sort()
	sorted_groups = []
	for key in keys:
		for group in groups:
			if key == get_bake_name(group[0]):
				sorted_groups.append(group)
				break
				
	groups = sorted_groups			
	# print("Keys: "+", ".join(keys))


	bake_sets = []
	for group in groups:
		low = []
		high = []
		cage = []
		float = []
		for obj in group:
			if filtered[obj] == 'low':
				low.append(obj)
			elif filtered[obj] == 'high':
				high.append(obj)
			elif filtered[obj] == 'cage':
				cage.append(obj)
			elif filtered[obj] == 'float':
				float.append(obj)


		name = get_bake_name(group[0])
		bake_sets.append(BakeSet(name, low, cage, high, float))

	return bake_sets



class BakeSet:
	objects_low = []	#low poly geometry
	objects_cage = []	#Cage low poly geometry
	objects_high = []	#High poly geometry
	objects_float = []	#Floating geometry
	name = ""

	has_issues = False

	def __init__(self, name, objects_low, objects_cage, objects_high, objects_float):
		self.objects_low = objects_low
		self.objects_cage = objects_cage
		self.objects_high = objects_high
		self.objects_float = objects_float
		self.name = name

		# Needs low poly objects to bake onto
		if len(objects_low) == 0:
			self.has_issues = True

		# Check Cage Object count to low poly count
		if len(objects_cage) > 0 and (len(objects_low) != len(objects_cage)):
			self.has_issues = True

		# Check for UV maps
		for obj in objects_low:
			if len(obj.data.uv_layers) == 0:
				self.has_issues = True
				break



def setup_vertex_color_selection(obj):
	bpy.ops.object.mode_set(mode='OBJECT')

	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj
	

	bpy.ops.object.mode_set(mode='VERTEX_PAINT')

	bpy.data.brushes["Draw"].color = (0, 0, 0)
	bpy.context.object.data.use_paint_mask = False
	bpy.ops.paint.vertex_color_set()

	bpy.data.brushes["Draw"].color = (1, 1, 1)
	bpy.context.object.data.use_paint_mask = True
	bpy.ops.paint.vertex_color_set()

	bpy.context.object.data.use_paint_mask = False

	# Back to object mode
	bpy.ops.object.mode_set(mode='OBJECT')



def setup_vertex_color_dirty(obj):

	print("setup_vertex_color_dirty {}".format(obj.name))

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
	bpy.ops.paint.vertex_color_dirt(dirt_angle=pi/2)
	bpy.ops.paint.vertex_color_dirt()



def setup_vertex_color_id_material(obj):
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj


	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

	bm = bmesh.from_edit_mesh(obj.data)
	# colorLayer = bm.loops.layers.color.verify()

	for i in range(len(obj.material_slots)):
		slot = obj.material_slots[i]
		if slot.material:

			# Select related faces
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='DESELECT')

			bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
			for face in bm.faces:
				if face.material_index == i:
					face.select = True

			color = utilities_color.get_color_id(i, len(obj.material_slots))

			bpy.ops.object.mode_set(mode='VERTEX_PAINT')
			bpy.data.brushes["Draw"].color = color
			bpy.context.object.data.use_paint_mask = True
			bpy.ops.paint.vertex_color_set()

	obj.data.update()

	# Back to object mode
	bpy.ops.object.mode_set(mode='OBJECT')



def setup_vertex_color_id_element(obj):
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
		color = utilities_color.get_color_id(i, len(groups))

		for face in groups[i]:
			for loop in face.loops:
				loop[colorLayer] = color
	obj.data.update()

	# Back to object mode
	bpy.ops.object.mode_set(mode='OBJECT')



def get_image_material(image):

	material = None
	if image.name in bpy.data.materials:
		material = bpy.data.materials[image.name]

		# Incorrect existing material, delete first and create new for cycles
		if bpy.context.scene.render.engine == 'CYCLES' and 'Diffuse BSDF' not in material.node_tree.nodes:
			material.user_clear()
			bpy.data.materials.remove(material)
			material = bpy.data.materials.new(image.name)
		
	else:
		material = bpy.data.materials.new(image.name)


	if bpy.context.scene.render.engine == 'CYCLES':
		material.use_nodes = True

		tree = material.node_tree
		node_image = tree.nodes.new("ShaderNodeTexImage")
		node_image.name = "image"
		node_image.select = True
		node_image.image = image
		tree.nodes.active = node_image

		node_diffuse = tree.nodes['Diffuse BSDF']

		# Make link
		tree.links.new(node_image.outputs[0], node_diffuse.inputs[0])

		return material

	elif bpy.context.scene.render.engine == 'BLENDER_RENDER' or bpy.context.scene.render.engine == 'BLENDER_GAME':
		material.use_nodes = False
		
		texture = None
		if image.name in bpy.data.textures:
			texture = bpy.data.textures[image.name]
		else:
			texture = bpy.data.textures.new(image.name, 'IMAGE')

		texture.image = image
		slot = material.texture_slots.add()
		slot.texture = texture
		slot.mapping = 'FLAT' 

		material.use_shadeless = True

	return material