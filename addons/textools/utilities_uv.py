import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi


def setSelectedFaces(faces):
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();

	for face in faces:
		for loop in face.loops:
			loop[uvLayer].select = True

#def getSelectedFaces:


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
	bbox['area'] = bbox['width'] * bbox['height']
	bbox['minLength'] = min(bbox['width'], bbox['height'])
				
	return bbox;


def getSelectionIslands():
	print("Get UV islands")
	
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
		