import bpy
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi



def main(context):
    print("Executing IslandsAlignSort main")
   


class IslandsAlignSort(bpy.types.Operator):
    """UV Operator description"""
    bl_idname = "uv.simple_operator"
    bl_label = "Simple UV Operator"

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def execute(self, context):
        main(context)
        return {'FINISHED'}

if __name__ == "__main__":
    #register()
    print("Calling from __main__")
    # test call
    #bpy.ops.uv.simple_operator()










def CollectUVIslands():
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
        


def GetSelectionBBox():
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
    bbox['center'] = boundsCenter / countFaces
    bbox['minLength'] = (boundsMax - boundsMin).x * (boundsMax - boundsMin).y 
                
    return bbox;
    

def AlignIslandMinimalBounds(uvLayer, faces):
    print("Align island")
    
    
    
    
    #Select Island
    bpy.ops.uv.select_all(action='DESELECT')

    for face in faces:
        for loop in face.loops:
            loop[uvLayer].select = True


    iterations = 4
    steps = 8
    angle = 90 / steps
    
    lengthA = 0
    lengthB = 0
    
    for i in range(0, iterations):
        
        angleBest = 0
        
        bbox = GetSelectionBBox()
        lengthA = bbox['minLength']
        
        for j in range(1, steps-1):
            bpy.ops.transform.rotate(value=(angle * pi / 180), axis=(-0, -0, -1))
        
            bbox = GetSelectionBBox()
            lengthB = bbox['minLength']
            if lengthB < lengthA:
                lengthA = lengthB;
                angleBest = j*angle
        
        angleCorrection = angleBest - angle*(steps-1)
        #if i != 
        
        bpy.ops.transform.rotate(value=(angleCorrection * pi / 180), axis=(-0, -0, -1))
            
            
        #print("BBox Size "+str(bbox['minLength']))    
    
    print("Angle: "+str(angle))
    
    




def SortAndPack():
    #Only in Edit mode
    if bpy.context.active_object.mode != 'EDIT':
        return

    #Requires UV map
    if not bpy.context.object.data.uv_layers:
         #self.report({'WARNING'}, "Object must have more than one UV map")
        return {'CANCELLED'}
    
    #Only in UV editor mode
    lastOperator = bpy.context.area.type;
    if bpy.context.area.type != 'IMAGE_EDITOR':
        bpy.context.area.type = 'IMAGE_EDITOR'
    
    #not in Synced mode
    if bpy.context.scene.tool_settings.use_uv_select_sync == False:
        #Only in Face or Island mode
        if bpy.context.scene.tool_settings.uv_select_mode is not 'FACE' or 'ISLAND':
            bpy.context.scene.tool_settings.uv_select_mode = 'FACE'
    
        #Select all linked islands
        #bpy.ops.uv.select_linked(extend=False)
        
        bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
        uvLayer = bm.loops.layers.uv.verify();
        
        islands = CollectUVIslands()
        
        for island in islands:
            AlignIslandMinimalBounds(uvLayer, island)
    
    
#    
    
    #restore context, e.g. back to code editor instead of uv editor
    bpy.context.area.type = lastOperator


# SortAndPack()