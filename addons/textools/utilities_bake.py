import bpy
import bmesh
import operator
import time
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings


keywords_low = ["low","lowpoly","l"]
keywords_high = ["high","highpoly","h"]
keywords_cage = ["cage","c"]

split_chars = ['_','.','-']


def store_bake_settings():
	print("store_bake_settings")
	settings.bake_render_engine = bpy.context.scene.render.engine


def restore_bake_settings():
	print("restore_bake_settings")

	if settings.bake_render_engine is not '':
		bpy.context.scene.render.engine = settings.bake_render_engine



def get_bake_name(obj):
	name = obj.name.lower()
	
	# Split by ' ','_','.' etc.
	split = name
	for char in split_chars:
		split = split.replace(char,' ')
	strings = split.split(' ')

	# Remove all keys from name
	keys = keywords_cage+keywords_high+keywords_low
	new_strings = []
	for string in strings:
		is_found = False
		for key in keys:
			if string == key:
				is_found = True
				break
		if not is_found:
			new_strings.append(string)

	return "_".join(new_strings)



def get_bake_type(obj):
	typ = ''

	# Detect by subdevision modifier
	if obj.modifiers:
		for modifier in obj.modifiers:
			if modifier.type == 'SUBSURF':
				typ = 'high'
				break

	# Detect by name pattern
	if typ == '':

		split = obj.name
		for char in split_chars:
			split = split.replace(char,' ')
		strings = split.split(' ')

		for string in strings:
			if typ == '':
				for key in keywords_cage:
					if key == string:
						typ = 'cage'
						break
			if typ == '':
				for key in keywords_low:
					if key == string:
						typ = 'low'
						break
			if typ == '':
				for key in keywords_high:
					if key == string:
						typ = 'high'
						break

	# if nothing was detected, assume its low
	if typ == '':
		typ = 'low'

	return typ


def get_bake_pairs():
	filtered = {}
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			filtered[obj] = get_bake_type(obj)
	
	groups = []
	# Group by names
	for key in filtered:
		name = get_bake_name(key)

		if len(groups)==0:
			groups.append([key])
		else:
			isFound = False
			for group in groups:
				groupName = get_bake_name(group[0])
				if name == groupName:
					group.append(key)
					isFound = True
					break

			if not isFound:
				groups.append([key])

	bake_sets = []
	for group in groups:
		low = []
		high = []
		cage = []
		for obj in group:
			if filtered[obj] == 'low':
				low.append(obj)
			elif filtered[obj] == 'high':
				high.append(obj)
			elif filtered[obj] == 'cage':
				cage.append(obj)

		name = get_bake_name(group[0])
		bake_sets.append(BakeSet(name, low, cage, high))

	return bake_sets


class BakeSet:
	objects_low = []
	objects_cage = []
	objects_high = []
	name = ""
	def __init__(self, name, objects_low, objects_cage, objects_high):
		self.objects_low = objects_low
		self.objects_cage = objects_cage
		self.objects_high = objects_high
		self.name = name
