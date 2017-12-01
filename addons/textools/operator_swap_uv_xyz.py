import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv


class operator_swap_uv_xyz(bpy.types.Operator):
	bl_idname = "uv.textools_swap_uv_xyz"
	bl_label = "Swap UV 2 XYZ"
	bl_description = "Swap UV to XYZ coordinates"


	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#One or more objects selected
		if len(bpy.context.selected_objects) == 0:
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 	#self.report({'WARNING'}, "Object must have more than one UV map")


		return True


	def execute(self, context):
		
		swap(context)
		return {'FINISHED'}


def swap(context):
	print("....")

	
	bpy.ops.object.mode_set(mode='EDIT')

	obj = bpy.context.active_object;
	bm = bmesh.from_edit_mesh(obj.data);
	uvLayer = bm.loops.layers.uv.verify();

	for face in bm.faces:
		# indexFace = face.index;
		for loop in face.loops:
			# if loop[uvLayer].select is True:
			uv = loop[uvLayer].uv
			# print("uv: "+str(uv.x)+" , "+str(uv.y))
			# print("Info: "+str(loop.vert.co))
			loop.vert.co[0] = uv.x;
			loop.vert.co[1] = uv.y;
			loop.vert.co[2] = 0;
			print("Info: "+str(uv))
			
	# Change Display Mode
	obj.show_wire = True
	obj.show_all_edges = True

	# obj.show_bounds = True
	bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
	box = bpy.ops.object.empty_add(type='CUBE', view_align=False, location=obj.location)
	bpy.context.active_object.rotation_quaternion = obj.rotation_quaternion
	bpy.ops.transform.resize(value=(1, 1, 0), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', proportional='DISABLED')

	print("Box? "+str(box))




	#SHape Keys: How to set: https://blender.stackexchange.com/questions/15593/how-to-change-shapekey-vertex-position-through-python




	#### simple uv > co
	# import bpy

	# print("######### Script Starting #########")

	# bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
	# print("Duplicated the object")

	# me = bpy.context.object.data
	# uv_layer = me.uv_layers.active.data

	# bpy.ops.object.shape_key_add(from_mix=True)
	# print("Added Base shapekey")

	# for poly in me.polygons:
	#     for loop_index in poly.loop_indices:
	#         i = me.loops[loop_index].vertex_index
	#         co = uv_layer[loop_index].uv
	#         me.vertices[i].co[0] = co[0] * 2    ## To resize result of UV mesh,
	#         me.vertices[i].co[1] = co[1] * 2    ## change the multiplied ammount
	#         me.vertices[i].co[2] = 0
	# print("Flattened Based on UV")

	# bpy.ops.object.shape_key_add(from_mix=False)
	# print("Added Morphed shapekey")

	# print("######### Script Complete #########")












	# me = bpy.context.object.data
	# uv_layer = me.uv_layers.active.data

	# for poly in me.polygons:
	# 	for loop_index in poly.loop_indices:
	# 		i = me.loops[loop_index].vertex_index
	# 		co = uv_layer[loop_index].uv
	# 		me.vertices[i].co[0] = co[0] - 0.5
	# 		me.vertices[i].co[1] = co[1] - 0.5
	# 		me.vertices[i].co[2] = 0




	# https://blenderartists.org/forum/showthread.php?403105-Flatten-Mesh-to-UV

	#convert a mesh's UV's into a second mesh using a script?
	# https://blender.stackexchange.com/questions/14074/is-there-a-way-to-convert-a-meshs-uvs-into-a-second-mesh-using-a-script

	#B-Mesh
	# obj = bpy.context.active_object
	# bm = bmesh.from_edit_mesh(obj.data);
	# uvLayer = bm.loops.layers.uv.verify();
	# uvLayer = obj.data.uv_layers.active.data

	

	# for poly in obj.data.polygons:
	# 	for loop_index in poly.loop_indices:
	# 		i = obj.data.loops[loop_index].vertex_index
	# 		# pos_uv = uvLayer.data[loop_index].uv
	# 		pos_uv = uvLayer[loop_index].uv
	# 		obj.data.vertices[i].co[0] = pos_uv[0] - 0.5
	# 		obj.data.vertices[i].co[1] = pos_uv[1] - 0.5
	# 		obj.data.vertices[i].co[2] = 0



	# for f in bm.faces:
	# 	if f.select:
	# 		for l in f.loops:
	# 			luv = l[uvLayer]
	# 			if luv.select:
	# 				# print("Idx: "+str(luv.uv))
	# 				if direction == "top":
	# 					luv.uv[1] = boundsAll['max'].y
	# 				elif direction == "bottom":
	# 					luv.uv[1] = boundsAll['min'].y
	# 				elif direction == "left":
	# 					luv.uv[0] = boundsAll['min'].x
	# 				elif direction == "right":
	# 					luv.uv[0] = boundsAll['max'].x



	# bmesh.update_edit_mesh(obj.data)


#if __name__ == "__main__":
 	# test call