import bpy
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi


class operator_islandsAlignSort(bpy.types.Operator):
	bl_idname = "uv.textools_islands_align_sort"
	bl_label = "Align & Sort"
	bl_description = "Rotates UV islands to minimal bounds and sorts them horizontal or vertical"
    # bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):

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
		if bpy.context.scene.tool_settings.use_uv_select_sync == True:
			return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing IslandsAlignSort main")
   	
	if bpy.context.space_data.pivot_point != 'CENTER':
		bpy.context.space_data.pivot_point = 'CENTER'

	
	#Only in Face or Island mode
	if bpy.context.scene.tool_settings.uv_select_mode is not 'FACE' or 'ISLAND':
		bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	

	bboxAll = getSelectionBBox()


	islands = collectUVIslands()
	sizes = {}	#https://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value


	for i in range(0, len(islands)):
		alignIslandMinimalBounds(uvLayer, islands[i])

		# Collect BBox sizes
		bbox = getSelectionBBox()
		sizes[i] = bbox['minLength'];

	# Sort islands by minimum size
	sortedIslands = sorted(sizes.values())

	pos = bboxAll['min'] #Vector((99999999.0,99999999.0))
	for i in range(0, len(sortedIslands)):
		island = islands[ sortedIslands[i] ]
		selectFaces( island )

	# for island in islands:
	# 	alignIslandMinimalBounds(uvLayer, island)
		
	# 	bbox = getSelectionBBox()
	# 	sizes[island] = bbox['minLength'];


#def setSelectFaces(faces):



#def getSelectedFaces:




def alignIslandMinimalBounds(uvLayer, faces):
	# Select Island
	bpy.ops.uv.select_all(action='DESELECT')

	for face in faces:
		for loop in face.loops:
			loop[uvLayer].select = True

	steps = 8
	angle = 45;	# Starting Angle, half each step

	bboxPrevious = getSelectionBBox()

	for i in range(0, steps):
		# Rotate right
		bpy.ops.transform.rotate(value=(angle * pi / 180), axis=(0, 0, 1))
		bbox = getSelectionBBox()

		if bbox['minLength'] < bboxPrevious['minLength']:
			bboxPrevious = bbox;	# Success
		else:
			# Rotate Left
			bpy.ops.transform.rotate(value=(-angle*2 * pi / 180), axis=(0, 0, 1))
			bbox = getSelectionBBox()
			if bbox['minLength'] < bboxPrevious['minLength']:
				bboxPrevious = bbox;	# Success
			else:
				# Restore angle of this iteration
				bpy.ops.transform.rotate(value=(angle * pi / 180), axis=(0, 0, 1))

		angle = angle / 2

	if bboxPrevious['width'] < bboxPrevious['height']:
		bpy.ops.transform.rotate(value=(90 * pi / 180), axis=(0, 0, 1))


def collectUVIslands():
	print("Collect UV islands")
	
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	#Reference A: https://github.com/nutti/Magic-UV/issues/41
	#Reference B: https://github.com/c30ra/uv-align-distribute/blob/v2.2/make_island.py

	#Extend selection
	bpy.ops.uv.select_linked(extend=False)
 
	#Collect selected UV faces
	selectedFaces = [];
	for face in bm.faces:
		if face.select == False:
			continue
		
		isUVFaceSelected = True;
		for loop in face.loops:
			if loop[uvLayer].select is False:
				isUVFaceSelected = False;
				continue
				
		if isUVFaceSelected == True:
			selectedFaces.append(face)
			
	print("Faces: "+str(len(selectedFaces)))
	
	#Collect UV islands
	parsedFaces = []
	islands = []

	for face in selectedFaces:
		#Skip if already processed
		if face in parsedFaces:
			continue;
		
		#Select single face
		bpy.ops.uv.select_all(action='DESELECT')
		for loop in face.loops:
			loop[uvLayer].select = True;
		bpy.ops.uv.select_linked(extend=False)#Extend selection
		
		#Collect faces
		islandFaces = [];
		for faceAll in bm.faces:
			if faceAll.select == False or faceAll in parsedFaces:
				continue
			isUVFaceSelected = True;
			for loop in faceAll.loops:
				if loop[uvLayer].select is False:
					isUVFaceSelected = False;
					continue
					
			if isUVFaceSelected == True:
				islandFaces.append(faceAll)
				#Add to parsed list, to skip next time
				if faceAll not in parsedFaces:
					parsedFaces.append(faceAll)
					
		#Assign Faces to island
		islands.append(islandFaces)
	
	#Restore selection
	for face in selectedFaces:
		for loop in face.loops:
			loop[uvLayer].select = True

	
	print("Islands: "+str(len(islands))+"x")
	return islands
		

def getSelectionBBox():
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	
	bbox = {}
	
	boundsMin = Vector((99999999.0,99999999.0))
	boundsMax = Vector((-99999999.0,-99999999.0))
	boundsCenter = Vector((0.0,0.0))
	countFaces = 0;
	
	for face in bm.faces:
		if face.select == True:
			for loop in face.loops:
				if loop[uvLayer].select is True:
					uv = loop[uvLayer].uv
					boundsMin.x = min(boundsMin.x, uv.x)
					boundsMin.y = min(boundsMin.y, uv.y)
					boundsMax.x = max(boundsMax.x, uv.x)
					boundsMax.y = max(boundsMax.y, uv.y)
			
					boundsCenter+= uv
					countFaces+=1
	
	bbox['min'] = boundsMin
	bbox['max'] = boundsMax
	bbox['width'] = (boundsMax - boundsMin).x
	bbox['height'] = (boundsMax - boundsMin).y
	bbox['center'] = boundsCenter / countFaces
	bbox['minLength'] = min(bbox['width'], bbox['height'])
				
	return bbox;


if __name__ == "__main__":
	print("__main__ called from islandsAlignSort.py")

 	# test call
	lastOperator = bpy.context.area.type;
	if bpy.context.area.type != 'IMAGE_EDITOR':
		bpy.context.area.type = 'IMAGE_EDITOR'

	bpy.ops.uv.textools_IslandsAlignSort()

	#restore context, e.g. back to code editor instead of uv editor
	bpy.context.area.type = lastOperator