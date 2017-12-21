import bpy
import bmesh
import operator
import time
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings

def selectionStore():
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();

	# https://blender.stackexchange.com/questions/5781/how-to-list-all-selected-elements-in-python
	print("selectionStore")
	settings.selection_uv_mode = bpy.context.scene.tool_settings.uv_select_mode
	settings.selection_uv_pivot = bpy.context.space_data.pivot_point
	# https://blender.stackexchange.com/questions/3532/obtain-uv-selection-in-python

	#VERT Selection
	settings.selection_mode = tuple(bpy.context.scene.tool_settings.mesh_select_mode)
	settings.selection_verts = []
	for vert in bm.verts:
		if vert.select:
			settings.selection_verts.append(vert)

	#Face selections (Loops)
	settings.selection_uv_loops = []
	for face in bm.faces:
		for loop in face.loops:
			if loop[uvLayer].select:
				settings.selection_uv_loops.append(loop[uvLayer])


def selectionRestore():

	print("selectionRestore")
	bpy.context.scene.tool_settings.uv_select_mode = settings.selection_uv_mode
	bpy.context.space_data.pivot_point = settings.selection_uv_pivot
	
	#VERT Selection
	bpy.context.scene.tool_settings.mesh_select_mode = settings.selection_mode
	bpy.ops.mesh.select_all(action='SELECT')
	# for vert in settings.selection_verts:
	# 	if vert:
	# 		vert.select = True

	#UV Face-UV Selections (Loops)
	bpy.ops.uv.select_all(action='DESELECT')
	for loop in settings.selection_uv_loops:
		loop.select = True

	bpy.context.scene.update()


def getSelectedFaces():
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	faces = [];
	for face in bm.faces:
		if face.select:
			faces.append(face)

	return faces


def setSelectedFaces(faces):
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	for face in faces:
		for loop in face.loops:
			loop[uvLayer].select = True

	# print("Done selecting "+str(len(faces))+" faces")



def getSelectionBBox():
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();
	
	bbox = {}
	
	boundsMin = Vector((99999999.0,99999999.0))
	boundsMax = Vector((-99999999.0,-99999999.0))
	boundsCenter = Vector((0.0,0.0))
	countFaces = 0;
	
	for face in bm.faces:
		# if face.select == True:
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
	
	if countFaces == 0:
		bbox['center'] = boundsMin
	else:
		bbox['center'] = boundsCenter / countFaces

	bbox['area'] = bbox['width'] * bbox['height']
	bbox['minLength'] = min(bbox['width'], bbox['height'])
				
	return bbox;


def getSelectionIslands():
	time_A = time.time()

'''
Islands: 1x, 0.00 seconds
Islands: 208x, 0.95 seconds
Islands: 104x
'''

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	#Reference A: https://github.com/nutti/Magic-UV/issues/41
	#Reference B: https://github.com/c30ra/uv-align-distribute/blob/v2.2/make_island.py

	#Extend selection
	if bpy.context.scene.tool_settings.use_uv_select_sync == False:
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
			
	# print("Faces: "+str(len(selectedFaces)))
	
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

	
	print("Islands: {}x, {:.4f} seconds".format(len(islands), time.time() - time_A))
	return islands
		