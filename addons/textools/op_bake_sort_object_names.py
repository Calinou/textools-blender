import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict
from math import pi


class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_sort_object_names"
	bl_label = "Sort Names"
	bl_description = "Find bake pairs by location and volume and match high poly to low poly names."
	# bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):

		return True


	def execute(self, context):
		
		sort_objects(context)
		return {'FINISHED'}

def sort_objects(context):
	print("Sort objects")

	objects = []
	bounds = {}
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH':
			objects.append(obj)
			bounds[obj] = get_bbox(obj)

	print("Objects {}x".format(len(objects)))

	# Compare against each other
	unprocessed = objects.copy()
	for A in objects:
		if A in unprocessed:
			unprocessed.remove(A)

			for B in unprocessed:
				score = get_score(A,B)

				print("C {:.4} 	{} : {} ".format(score, A.name[:8], B.name[:8] ))





	

def get_score(A, B):
	# Position
	delta_pos = ( get_bbox_center(B) - get_bbox_center(A) ).length

	# Volume
	volume_A = A.dimensions.x * A.dimensions.y * A.dimensions.z
	volume_B = B.dimensions.x * B.dimensions.y * B.dimensions.z
	delta_vol = math.sqrt(max(volume_A, volume_B) - min(volume_A, volume_B))

	# print("Compare {0} : {1} = d:{2:.3f} 	v:{3:.6f}".format(A.name[:3], B.name[:3], delta_pos, delta_vol))
	return delta_pos + delta_vol



def get_center(obj):
	bbox = get_bbox(obj)
	return bbox['min'] + bbox['size']/2



def get_bbox(obj):
	corners = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]

	min = Vector(corners[0].x, corners[0].y, corners[0].z)
	max = Vector(corners[0].x, corners[0].y, corners[0].z)
	for corner in corners:
		min.x = min(min.x, corner.x)
		min.y = min(min.y, corner.y)
		min.z = min(min.z, corner.z)
		
		max.x = max(max.x, corner.x)
		max.y = max(max.y, corner.y)
		max.z = max(max.z, corner.z)

	return {'min':min, 'max':max, 'size':(max-min)}



def is_colliding(bbox_A, bbox_B):
	# http://www.cbcity.de/simple-3d-collision-detection-with-python-scripting-in-blender


	return False



# def get_bake_type(obj):
# 	typ = ''

# 	# Detect by subdevision modifier
# 	if obj.modifiers:
# 		for modifier in obj.modifiers:
# 			if modifier.type == 'SUBSURF':
# 				typ = 'high'
# 				break
# 			elif modifier.type == 'MIRROR':
# 				typ = 'high'
# 				break


# 	# if nothing was detected, assume its low
# 	if typ == '':
# 		typ = 'low'

# 	return typ