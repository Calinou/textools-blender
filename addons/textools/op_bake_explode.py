import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings


margin = 0.1


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
	
	print("Explode---------------")

	set_bounds = {}	
	sets = settings.sets
	for set in sets:
		bounds = []
		objects = set.objects_low + set.objects_high + set.objects_cage
		for obj in objects:
			bounds.append( get_bbox(obj) )

		set_bounds[set] = merge_bounds(bounds)

	# All combined bounding boxes
	bbox_all = merge_bounds(list(set_bounds.values()))

	# Offset sets into their direction
	offsets_dir = {}
	for set in set_bounds:
		

		delta_center = set_bounds[set]['center'] - bbox_all['center']
		# set_bounds[set]['size']
		print("Bounds: '{}' 	= {:.2},{:.2},{:.2}".format(set.name, delta_center.x, delta_center.y, delta_center.z ))

		size = set_bounds[set]['size']

		# Which Direction?
		delta_max = max(abs(delta_center.x), abs(delta_center.y), abs(delta_center.z))
		if abs(delta_center.x) == delta_max:
			offset_set(set, Vector((delta_center.x/abs(delta_center.x), 0,0 )), size.x, offsets_dir)
			
		elif abs(delta_center.y) == delta_max:
			offset_set(set, Vector((0, delta_center.y/abs(delta_center.y), 0 )), size.y, offsets_dir)

		elif abs(delta_center.z) == delta_max:
			offset_set(set, Vector((0,0, delta_center.z/abs(delta_center.z) )), size.z, offsets_dir)




def offset_set(set, dir, length, offsets_dir):
	# http://blenderscripting.blogspot.com.au/2011/05/inspired-by-post-on-ba-it-just-so.html

	
	objects = set.objects_low + set.objects_high + set.objects_cage

	print("Move {}x  at {}".format(len(objects), (dir*0.5) ))

	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:
		obj.select = True
		obj.location += dir * 0.2
	# bpy.ops.transform.translate(value=dir*0.5)
	# bpy.ops.transform.translate(value=(1,0,0), release_confirm=False)



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