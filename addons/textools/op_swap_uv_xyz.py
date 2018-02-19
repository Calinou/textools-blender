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

	#Collect UV islands
	islands = utilities_uv.getSelectionIslands(bm, uvLayer)

	# Get object bounds
	bounds = get_bbox(obj)

	# Map clusters to 
	uvs = {}
	clusters = []
	uv_to_clusters = {}
	vert_to_clusters = {}

	for face in bm.faces:

		print("Face {}".format(face.index))
		# print("Loop 0 {}".format(face.loops[0] ))

		for i in range(len(face.loops)):
			v = face.loops[i]
			uv = Get_UVSet(uvs, bm, uvLayer, face.index, i)

			# 	# clusters
			isMerged = False
			for cluster in clusters:
				d = (uv.pos() - cluster.uvs[0].pos()).length
				if d <= 0.0000001:
					#Merge
					cluster.append(uv)
					uv_to_clusters[uv] = cluster
					if v not in vert_to_clusters:
						vert_to_clusters[v] = cluster
					isMerged = True;
					break;
			if not isMerged:
				#New Group
				clusters.append( UVCluster(v, [uv]) )
				uv_to_clusters[uv] = clusters[-1]
				if v not in vert_to_clusters:
					vert_to_clusters[v] = clusters[-1]

		# for loop in face.loops:
		# 	v = loop.vert
		# 	uv = loop[uvLayer]
		# 	uvset = UVSet(bm, uvLayer, face.index, )

		# 	# clusters
		# 	isMerged = False
		# 	for cluster in clusters:
		# 		d = (uv.uv - cluster.uvs[0].uv).length
		# 		if d <= 0.0000001:
		# 			#Merge
		# 			cluster.append(uv)
		# 			uv_to_clusters[uv] = cluster
		# 			if v not in vert_to_clusters:
		# 				vert_to_clusters[v] = cluster
		# 			isMerged = True;
		# 			break;
		# 	if not isMerged:
		# 		#New Group
		# 		clusters.append( UVCluster(v, [uv]) )
		# 		uv_to_clusters[uv] = clusters[-1]
		# 		if v not in vert_to_clusters:
		# 			vert_to_clusters[v] = clusters[-1]


	

	print("Islands {}x".format(len(islands)))
	print("Clusters {}x".format(len(clusters)))

	# for key in uv_to_clusters.keys():
	# 	print("Key {}".format(key))



	m_vert_cluster = []
	m_verts_org = []
	m_verts = []
	m_faces = []
	
	for island in islands:
		print("\nIsland {}x".format(len(island) ))

		# c = []
		# v = []
		# f = []
		# org_vert = []

		for face in island:


			# dbg = []
			f = []
			for i in range(len(face.loops)):
				# print("Loop {}".format( loop[uvLayer]) )

				


				v = face.loops[i].vert
				uv = Get_UVSet(uvs, bm, uvLayer, face.index, i)
				
				

				# if uvs not in uvs_to_clusters:
				# 	idx = get_uv_index(face.index, i)
				# 	print("Issue: {} idx {}".format(loop.vert.index, idx))
				# 	# print("type: {} ".format(uv))
				# 	i+=1
				# 	continue
				# if uv in uv_to_clusters:
				c = uv_to_clusters[ uv ]

				# index = get_uv_index(face.index, i)
				# dbg.append( "{}>{}".format( index, index in uvs))
				# dbg.append( "{}".format( m_vert_cluster.index(c) ))


				index = 0
				if c in m_vert_cluster:
					index = m_vert_cluster.index(c)

				else:
					index = len(m_vert_cluster)
					m_vert_cluster.append(c)
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

	bpy.ops.object.select_all(action='DESELECT')
	bpy.context.scene.objects.active = mesh_obj
	mesh_obj.select = True

	mesh_obj.location += Vector((-2.5, 0, 0))
	# bpy.ops.transform.translate(value=(-2, 0, 0))
	# bpy.ops.transform.translate(value=(-2, 0, 0))



	# bmesh.ops.split(bm, geom, dest, use_only_faces)
	# Split Off Geometry.
	# Disconnect geometry from adjacent edges and faces, optionally into a destination mesh.



def Get_UVSet(uvs, bm, layer, index_face, index_loop):
	index = get_uv_index(index_face, index_loop)
	if index not in uvs:
		uvs[index] = UVSet(bm, layer, index_face, index_loop)

	return uvs[index]



class UVSet:
	bm = None
	layer = None
	index_face = 0
	index_loop = 0

	def __init__(self, bm, layer, index_face, index_loop):
		self.bm = bm
		self.layer = layer
		self.index_face = index_face
		self.index_loop = index_loop
		
	def uv(self):
		face = self.bm.faces[self.index_face]
		return face.loops[self.index_loop][self.layer]

	def pos(self):
		return self.uv().uv

	def vertex(self):
		return face.loops[self.index_loop].vertex



def get_uv_index(index_face, index_loop):
	return (index_face*1000000)+index_loop
	# return str(index_face)+"_"+str( index_loop)

	

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