import bpy
import bmesh
import operator
import math

from mathutils import Vector
from collections import defaultdict


from . import utilities_uv
import imp
imp.reload(utilities_uv)


class operator_islandsAlignSort(bpy.types.Operator):
	bl_idname = "uv.textools_islands_align_sort"
	bl_label = "Align & Sort"
	bl_description = "Rotates UV islands to minimal bounds and sorts them horizontal or vertical"
    # bl_options = {'REGISTER', 'UNDO'}
	is_vertical = bpy.props.BoolProperty(description="Vertical or Horizontal orientation", default=True)

	@classmethod
	def poll(cls, context):

		if not bpy.context.active_object:
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False
		
		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 	#self.report({'WARNING'}, "Object must have more than one UV map")

		#Not in Synced mode
		# if bpy.context.scene.tool_settings.use_uv_select_sync == True:
		# 	return False

		return True


	def execute(self, context):
		
		print("is_vertical: "+str(self.is_vertical))

		main(context, self.is_vertical)
		return {'FINISHED'}


def main(context, isVertical):
	print("Executing IslandsAlignSort main")
   	
	#Store selection
	utilities_uv.selectionStore()

	if bpy.context.space_data.pivot_point != 'CENTER':
		bpy.context.space_data.pivot_point = 'CENTER'

	#Only in Face or Island mode
	if bpy.context.scene.tool_settings.uv_select_mode is not 'FACE' or 'ISLAND':
		bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	

	boundsAll = utilities_uv.getSelectionBBox()


	islands = utilities_uv.getSelectionIslands()
	allSizes = {}	#https://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value
	allBounds = {}

	print("Islands: "+str(len(islands))+"x")

	bpy.context.window_manager.progress_begin(0, len(islands))

	#Rotate to minimal bounds
	for i in range(0, len(islands)):
		alignIslandMinimalBounds(uvLayer, islands[i])

		# Collect BBox sizes
		bounds = utilities_uv.getSelectionBBox()
		allSizes[i] = bounds['area'] + i*0.000001;#Make each size unique
		allBounds[i] = bounds;
		print("Rotate compact:  "+str(allSizes[i]))

		bpy.context.window_manager.progress_update(i)

	bpy.context.window_manager.progress_end()


	#Position by sorted size in row
	sortedSizes = sorted(allSizes.items(), key=operator.itemgetter(1))#Sort by values, store tuples
	sortedSizes.reverse()
	offset = 0.0
	for sortedSize in sortedSizes:
		index = sortedSize[0]
		island = islands[index]
		bounds = allBounds[index]

		#Select Island
		bpy.ops.uv.select_all(action='DESELECT')
		utilities_uv.setSelectedFaces(island)
		
		#Offset Island
		if(isVertical):
			delta = Vector((boundsAll['min'].x - bounds['min'].x, boundsAll['max'].y - bounds['max'].y));
			bpy.ops.transform.translate(value=(delta.x, delta.y-offset, 0))
			offset += bounds['height']+0.01
	# 	else:
	# 		print("Horizontal")


	#Restore selection
	utilities_uv.selectionRestore()















	#pos =  #Vector((99999999.0,99999999.0))

	# Sort islands by minimum size
	# sortedIslands = sorted(sizes.values())

	# for size in sortedIslands:


	# print("Sizes "+str(sortedIslands))



	
	# for i in range(0, len(sortedIslands)):
	# 	print(">> Select "+str(i)+" sorted: "+str(len(sortedIslands))+"x, islands: "+str(len(islands))+"x")
	# 	island = islands[ sortedIslands[i] ]
	# 	selectFaces( island )




	# for index, length in sizes.items():
	#     if length == sortedIslands[0]:
	#         print("Found shorted island "+str(index))
	#         break




	# index = sizes[sortedIslands[0]]
	# print("Index smallest: "+str(index))




	# for island in islands:
	# 	alignIslandMinimalBounds(uvLayer, island)
		
	# 	bbox = utilities.getSelectionBBox()
	# 	sizes[island] = bbox['minLength'];




def alignIslandMinimalBounds(uvLayer, faces):
	# Select Island
	bpy.ops.uv.select_all(action='DESELECT')
	utilities_uv.setSelectedFaces(faces)

	steps = 8
	angle = 45;	# Starting Angle, half each step

	bboxPrevious = utilities_uv.getSelectionBBox()

	for i in range(0, steps):
		# Rotate right
		bpy.ops.transform.rotate(value=(angle * pi / 180), axis=(0, 0, 1))
		bbox = utilities_uv.getSelectionBBox()

		if i == 0:
			sizeA = bboxPrevious['width'] * bboxPrevious['height']
			sizeB = bbox['width'] * bbox['height']
			if abs(bbox['width'] - bbox['height']) <= 0.0001 and sizeA < sizeB:
				# print("Already squared")
				bpy.ops.transform.rotate(value=(-angle * pi / 180), axis=(0, 0, 1))
				break;


		if bbox['minLength'] < bboxPrevious['minLength']:
			bboxPrevious = bbox;	# Success
		else:
			# Rotate Left
			bpy.ops.transform.rotate(value=(-angle*2 * pi / 180), axis=(0, 0, 1))
			bbox = utilities_uv.getSelectionBBox()
			if bbox['minLength'] < bboxPrevious['minLength']:
				bboxPrevious = bbox;	# Success
			else:
				# Restore angle of this iteration
				bpy.ops.transform.rotate(value=(angle * pi / 180), axis=(0, 0, 1))

		angle = angle / 2

	if bboxPrevious['width'] < bboxPrevious['height']:
		bpy.ops.transform.rotate(value=(90 * pi / 180), axis=(0, 0, 1))



if __name__ == "__main__":
	print("__main__ called from islandsAlignSort.py")

	# test call
	# lastOperator = bpy.context.area.type;
	# if bpy.context.area.type != 'IMAGE_EDITOR':
	# 	bpy.context.area.type = 'IMAGE_EDITOR'

	# bpy.ops.uv.textools_IslandsAlignSort()

	# #restore context, e.g. back to code editor instead of uv editor
	# bpy.context.area.type = lastOperator
