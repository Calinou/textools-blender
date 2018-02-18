import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv


id_shape_key_mesh = "mesh"
id_shape_key_uv = "uv"

class op(bpy.types.Operator):
	bl_idname = "uv.textools_swap_uv_xyz"
	bl_label = "Swap UV 2 XYZ"
	bl_description = "Swap UV to XYZ coordinates"
	bl_options = {'REGISTER', 'UNDO'}

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
		swap_uv_xyz(context)
		return {'FINISHED'}


def swap_uv_xyz(context):
	print("....")


	# Add shape keys
	# obj.shape_key_add(id_shape_key_mesh)
	# obj.shape_key_add(id_shape_key_uv)
	
	obj = bpy.context.active_object
	bpy.ops.object.mode_set(mode='EDIT')

	bm = bmesh.from_edit_mesh(obj.data)
	uvLayer = bm.loops.layers.uv.verify()

	# bpy.data.shape_keys["Key"].key_blocks[id_shape_key_uv].value = 1

	# Select all
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.uv.select_all(action='SELECT')



	clusters = []
	uv_to_clusters = {}
	vert_to_clusters = {}

	for face in bm.faces:
		for loop in face.loops:
			vert = loop.vert
			uv = loop[uvLayer]
			
			# vert_to_uv
			# if vert not in vert_to_uv:
			# 	vert_to_uv[vert] = [uv];
			# else:
			# 	vert_to_uv[vert].append(uv)

			# uv_to_vert
			# if uv not in uv_to_vert:
			# 	uv_to_vert[ uv ] = vert;
			# if uv not in uv_to_face:
			# 	uv_to_face[ uv ] = face;

			# clusters
			isMerged = False
			for cluster in clusters:
				d = (uv.uv - cluster.uvs[0].uv).length
				if d <= 0.0000001:
					#Merge
					cluster.append(uv)
					uv_to_clusters[uv] = cluster
					if vert not in vert_to_clusters:
						vert_to_clusters[vert] = cluster
					isMerged = True;
					break;
			if not isMerged:
				#New Group
				clusters.append( UVCluster(vert, [uv]) )
				uv_to_clusters[uv] = clusters[-1]
				if vert not in vert_to_clusters:
					vert_to_clusters[vert] = clusters[-1]


	#Collect UV islands
	islands = utilities_uv.getSelectionIslands()

	print("Islands {}x".format(len(islands)))


	m_vert_cluster = []
	m_verts_org = []
	m_verts = []
	m_faces = []
	

	for island in islands:
		print("Island,  {}x".format(len(island) ))

		# c = []
		# v = []
		# f = []
		# org_vert = []

		for face in island:

			f = []
			for loop in face.loops:
				# print("Loop {}".format( loop[uvLayer]) )

				v = loop.vert

				index = 0
				if v in m_verts_org:
					index = m_verts_org.index(v)

				if v not in m_verts_org:
					index = len(m_verts_org)
					m_verts_org.append(v)
					m_verts.append( v.co.copy() )
					
				f.append(index)

			m_faces.append(f)
			print("Face {}".format(f))


	bpy.ops.object.mode_set(mode='OBJECT')
	# bpy.ops.object.select_all(action='TOGGLE')


	mesh = bpy.data.meshes.new("mesh_texture")
	mesh.from_pydata(m_verts, [], m_faces)
	mesh.update()

	mesh_obj = bpy.data.objects.new("mesh_texture_obj", mesh)
	bpy.context.scene.objects.link(mesh_obj)
	mesh_obj.select = True
	# bmesh.ops.split(bm, geom, dest, use_only_faces)
	# Split Off Geometry.
	# Disconnect geometry from adjacent edges and faces, optionally into a destination mesh.


	
	



class UVCluster:
	uvs = []
	vertex = None
	
	def __init__(self, vertex, uvs):
		self.vertex = vertex
		self.uvs = uvs

	def append(self, uv):
		self.uvs.append(uv)













	# id_shape_key_mesh =
	# id_shape_key_uv = "


	# print("Shape keys '{0}'".format(obj.data.shape_keys))
	'''
	for face in bm.faces:
		for loop in face.loops:
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
	'''



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