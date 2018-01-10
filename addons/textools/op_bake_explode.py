import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings


class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_explode"
	bl_label = "Explode"
	bl_description = "Explode selected bake pairs with animation keyframes"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if len(settings.sets) == 0:
			return False

		return True


	def execute(self, context):
		explode(self)

		return {'FINISHED'}




def explode(self):
	
	print("_________________\nExplode\n")

	set_bounds = {}	
	sets = settings.sets

	avg_side = 0
	for set in sets:
		set_bounds[set] = get_bbox_set(set)

		avg_side+=set_bounds[set]['size'].x
		avg_side+=set_bounds[set]['size'].y
		avg_side+=set_bounds[set]['size'].z
	avg_side/=(len(sets)*3)

	# All combined bounding boxes
	bbox_all = merge_bounds(list(set_bounds.values()))
	# bbox


	# Offset sets into their direction
	dir_offset_last_bbox = {}
	for i in range(0,6):
		dir_offset_last_bbox[i] = bbox_all

	# Process each set
	for set in set_bounds:
		delta = set_bounds[set]['center'] - bbox_all['center']
		offset_set(set, delta, avg_side*0.1, dir_offset_last_bbox )

	print("\n\n")

def offset_set(set, delta, margin, dir_offset_last_bbox):
	objects = set.objects_low + set.objects_high + set.objects_cage
	print("\nSet '{}' with {}x".format(set.name, len(objects) ))

	# Which Direction?
	delta_max = max(abs(delta.x), abs(delta.y), abs(delta.z))
	direction = [0,0,0]
	if delta_max > 0:
		for i in range(0,3):
			if abs(delta[i]) == delta_max:
				direction[i] = delta[i]/abs(delta[i])
			else:
				direction[i] = 0
	else:
		# Default when not delta offset was measure move up
		direction = [0,0,1]

	delta = Vector((direction[0], direction[1], direction[2]))
	# delta = Vector((0,0,0))

	# Get Key
	key = get_delta_key(delta)
	
	# print("dir: {}, Key {} inside? {}, keys: {}".format(delta, key, key in dir_offset_last_bbox, dir_offset_last_bbox.keys() ))

	# Calculate Offset
	bbox = get_bbox_set(set)
	bbox_last = dir_offset_last_bbox[key]
	
	offset = Vector((0,0,0))

	if delta.x == 1:
		offset = delta * ( bbox_last['max'].x - bbox['min'].x )
	elif delta.x == -1:
		offset = delta * -( bbox_last['min'].x - bbox['max'].x )
	
	elif delta.y == 1:
		offset = delta * ( bbox_last['max'].y - bbox['min'].y )
	elif delta.y == -1:
		offset = delta * -( bbox_last['min'].y - bbox['max'].y )
	
	elif delta.z == 1:
		offset = delta * ( bbox_last['max'].z - bbox['min'].z )
	elif delta.z == -1:
		offset = delta * -( bbox_last['min'].z - bbox['max'].z )

	# Add margin
	offset+= delta * margin

	# if abs(delta.x) == 1:
	# 	offset = delta * ( bbox_last['max'].x - bbox['min'].x )

	# elif abs(delta.y) == 1:
	# 	offset = delta * ( bbox_last['max'].y - bbox['min'].y )

		# print("   '{:.2}' - '{:.2}' = Offset:{:.2}".format(
		# 	bbox_last['max'].x, 
		# 	bbox['min'].x,
		# 	( bbox_last['max'].x - bbox['min'].x )
		# ))

	# Offset items
	for obj in objects:
		obj.location += offset
	bpy.context.scene.update()

	# Update last bbox in direction
	dir_offset_last_bbox[key] = get_bbox_set(set)

	# 
	print("   Off {:.2},{:.2},{:.2}, max.x:{:.2}".format(offset.x, offset.y, offset.z, dir_offset_last_bbox[key]['max'].x ))
	# print("")



def get_delta_key(delta):
	# print("Get key {} is: {}".format(delta, delta.y == -1 ))
	if delta.x == -1:
		return 0
	elif delta.x == 1:
		return 1
	if delta.y == -1:
		return 2
	elif delta.y == 1:
		return 3
	if delta.z == -1:
		return 4
	elif delta.z == 1:
		return 5

	



# def offset_set(set, dir, length, offsets_dir):
# 	# http://blenderscripting.blogspot.com.au/2011/05/inspired-by-post-on-ba-it-just-so.html

	
# 	objects = set.objects_low + set.objects_high + set.objects_cage

# 	print("Move {}x  at {}".format(len(objects), (dir*0.5) ))

# 	bpy.ops.object.select_all(action='DESELECT')
# 	for obj in objects:
# 		obj.select = True
		# obj.location += dir * 0.2
	# bpy.ops.transform.translate(value=dir*0.5)
	# bpy.ops.transform.translate(value=(1,0,0), release_confirm=False)

def max_bbox(bounds):
	return bounds[0]


def merge_bounds(bounds):

	box_min = bounds[0]['min'].copy()
	box_max = bounds[0]['max'].copy()
	
	for bbox in bounds:
		# box_min.x = -8
		box_min.x = min(box_min.x, bbox['min'].x)
		box_min.y = min(box_min.y, bbox['min'].y)
		box_min.z = min(box_min.z, bbox['min'].z)
		
		box_max.x = max(box_max.x, bbox['max'].x)
		box_max.y = max(box_max.y, bbox['max'].y)
		box_max.z = max(box_max.z, bbox['max'].z)

	return {
		'min':box_min, 
		'max':box_max, 
		'size':(box_max-box_min),
		'center':box_min+(box_max-box_min)/2
	}


def get_bbox_set(set):
	objects = set.objects_low + set.objects_high + set.objects_cage
	bounds = []
	for obj in objects:
		bounds.append( get_bbox(obj) )
	return merge_bounds(bounds)


def get_bbox(obj):
	corners = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]

	# Get world space Min / Max
	box_min = Vector((corners[0].x, corners[0].y, corners[0].z))
	box_max = Vector((corners[0].x, corners[0].y, corners[0].z))
	for corner in corners:
		# box_min.x = -8
		box_min.x = min(box_min.x, corner.x)
		box_min.y = min(box_min.y, corner.y)
		box_min.z = min(box_min.z, corner.z)
		
		box_max.x = max(box_max.x, corner.x)
		box_max.y = max(box_max.y, corner.y)
		box_max.z = max(box_max.z, corner.z)

	return {
		'min':box_min, 
		'max':box_max, 
		'size':(box_max-box_min),
		'center':box_min+(box_max-box_min)/2
	}