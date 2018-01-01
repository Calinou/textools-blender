import bpy
import bmesh
import operator
import time
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings

def get_bake_pairs():
	keywords_low = ["low","lowpoly"]
	keywords_high = ["high","highpoly"]
	keywords_cage = ["cage"]

	

	filtered = {}
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			# Detect type
			obj_type = ''
			name = obj.name.lower()
			
			# check type
			for key in keywords_cage:
				if key in name:
					obj_type = 'cage'

			if obj_type == '':
				for key in keywords_low:
					if key in name:
						obj_type = 'low'

			if obj_type == '':
				for key in keywords_high:
					if key in name:
						obj_type = 'high'

			if obj_type == '':
				obj_type == 'low'

			filtered[obj] = obj_type
	
	# sets = []
	low = []
	high = []
	cage = []
	for key in filtered:
		if filtered[key] == 'low':
			low.append(key)
		elif filtered[key] == 'high':
			high.append(key)
		elif filtered[key] == 'cage':
			cage.append(key)

	if len(filtered) == 0:
		return []
	else:
		return [BakeSet("test", low, cage, high )]


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
	
	def append(self, uv):
		self.uvs.append(uv)
