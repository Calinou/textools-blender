import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi


class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_sort_object_names"
	bl_label = "Sort Names"
	bl_description = "Find bake pairs by location and volume and match high poly to low poly names."
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):

		return True


	def execute(self, context):
		
		sort_objects(context)
		return {'FINISHED'}

def sort_objects(context):
	print("Sort objects")

	filtered = {}
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			filtered[obj] = get_bake_type(obj)



def get_bake_type(obj):
	typ = ''

	# Detect by subdevision modifier
	if obj.modifiers:
		for modifier in obj.modifiers:
			if modifier.type == 'SUBSURF':
				typ = 'high'
				break
			elif modifier.type == 'MIRROR':
				typ = 'high'
				break


	# if nothing was detected, assume its low
	if typ == '':
		typ = 'low'

	return typ