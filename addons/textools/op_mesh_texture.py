import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv


id_shape_key_mesh = "mesh"
id_shape_key_uv = "uv"



# Find a mesh that contains UV mesh shape keys 
def find_uv_mesh(objects):
	for obj in objects:
		# Requires mesh & UV channel
		if obj.type == 'MESH' and not obj.data.uv_layers:
			if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) == 2:
				if "uv" in obj.data.shape_keys.key_blocks:
					if "model" in obj.data.shape_keys.key_blocks:
						if "Solidify" in obj.modifiers:
							return obj
	return None



def get_mode():
	# Create UV mesh from face selection
	if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT':
		if not find_uv_mesh([bpy.context.active_object]):
			return 'CREATE_FACES'

	# Wrap texture mesh around UV mesh
	if len(bpy.context.selected_objects) >= 2 and find_uv_mesh(bpy.context.selected_objects):
		return 'WRAP'

	# Create UV mesh from whole object
	if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
		return 'CREATE_OBJECT'

	return 'UNDEFINED'



class op(bpy.types.Operator):
	bl_idname = "uv.textools_mesh_texture"
	bl_label = "Swap UV 2 XYZ"
	bl_description = "Swap UV to XYZ coordinates"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		if get_mode() == 'UNDEFINED':
			return False
		return True


	def execute(self, context):

		mode = get_mode()
		if mode == 'CREATE_FACES' or mode == 'CREATE_OBJECT':
			create_uv_mesh(self, bpy.context.active_object)	
				
		elif mode == 'WRAP':
			wrap_mesh_texture(self)

		return {'FINISHED'}



def create_uv_mesh(self, obj):
	
	mode = bpy.context.active_object.mode

	# Select
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj

	
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="FACE")
	bpy.context.scene.tool_settings.use_uv_select_sync = False


	# Select all if OBJECT mode
	if mode == 'OBJECT':
		bpy.ops.mesh.select_all(action='SELECT')
		# bpy.ops.uv.select_all(action='SELECT')

	# Create UV Map
	if not obj.data.uv_layers:
		if mode == 'OBJECT':
			bpy.ops.uv.smart_project(
				angle_limit=65, 
				island_margin=0.5, 
				user_area_weight=0, 
				use_aspect=True, 
				stretch_to_bounds=True
			)
		elif mode == 'EDIT':
			bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0)
			bpy.ops.uv.textools_unwrap_faces_iron()

	bpy.ops.uv.select_all(action='SELECT')

	bm = bmesh.from_edit_mesh(obj.data)
	uvLayer = bm.loops.layers.uv.verify()

	#Collect UV islands
	islands = utilities_uv.getSelectionIslands(bm, uvLayer)

	# Get object bounds
	bounds = get_bbox(obj)

	# Collect clusters 
	uvs = {}
	clusters = []
	uv_to_clusters = {}
	vert_to_clusters = {}
	for face in bm.faces:
		if face.select:
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
	

	print("Islands {}x".format(len(islands)))
	print("UV Vert Clusters {}x".format(len(clusters)))

	# for key in uv_to_clusters.keys():
	# 	print("Key {}".format(key))

	uv_size = max(bounds['size'].x, bounds['size'].y, bounds['size'].z)

	m_vert_cluster = []
	m_verts_org = []
	m_verts_A = []
	m_verts_B = []
	m_faces = []
	
	for island in islands:
		for face in island:
			f = []
			for i in range(len(face.loops)):
				v = face.loops[i].vert
				uv = Get_UVSet(uvs, bm, uvLayer, face.index, i)
				c = uv_to_clusters[ uv ]

				index = 0
				if c in m_vert_cluster:
					index = m_vert_cluster.index(c)

				else:
					index = len(m_vert_cluster)
					m_vert_cluster.append(c)
					m_verts_org.append(v)

					m_verts_A.append( Vector((uv.pos().x*uv_size -uv_size/2, uv.pos().y*uv_size -uv_size/2, 0)) )
					m_verts_B.append( obj.matrix_world * v.co - bpy.context.scene.cursor_location  )
					
				f.append(index)

			m_faces.append(f)

	# Add UV bounds as edges
	# uv_size/2
	verts = [
		Vector((-uv_size/2, -uv_size/2, 0)),
		Vector(( uv_size/2, -uv_size/2, 0)),
		Vector(( uv_size/2, uv_size/2, 0)),
		Vector((-uv_size/2, uv_size/2, 0)),
	]
	m_verts_A = m_verts_A+verts;
	m_verts_B = m_verts_B+verts;

	bpy.ops.object.mode_set(mode='OBJECT')

	# Create Mesh
	mesh = bpy.data.meshes.new("mesh_texture")
	mesh.from_pydata(m_verts_A, [], m_faces)
	mesh.update()
	mesh_obj = bpy.data.objects.new("mesh_texture_obj", mesh)
	mesh_obj.location = bpy.context.scene.cursor_location
	bpy.context.scene.objects.link(mesh_obj)


	# Add shape keys
	mesh_obj.shape_key_add(name="uv", from_mix=True)
	mesh_obj.shape_key_add(name="model", from_mix=True)
	mesh_obj.active_shape_key_index = 1

	# Select
	bpy.context.scene.objects.active = mesh_obj
	mesh_obj.select = True

	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(mesh_obj.data)
	

	if hasattr(bm.faces, "ensure_lookup_table"): 
		bm.faces.ensure_lookup_table()
		bm.verts.ensure_lookup_table()

	bm.edges.new((bm.verts[-4], bm.verts[-3]))
	bm.edges.new((bm.verts[-3], bm.verts[-2]))
	bm.edges.new((bm.verts[-2], bm.verts[-1]))
	bm.edges.new((bm.verts[-1], bm.verts[-4]))


	for i in range(len(m_verts_B)):
		bm.verts[i].co = m_verts_B[i]
	bpy.ops.object.mode_set(mode='OBJECT')


	# Display as edges only
	mesh_obj.show_wire = True
	mesh_obj.show_all_edges = True
	mesh_obj.draw_type = 'WIRE'

	# Add solidify modifier
	bpy.ops.object.modifier_add(type='SOLIDIFY')
	bpy.context.object.modifiers["Solidify"].offset = 1
	bpy.context.object.modifiers["Solidify"].thickness = 0 #uv_size * 0.1
	bpy.context.object.modifiers["Solidify"].use_even_offset = True
	bpy.context.object.modifiers["Solidify"].thickness_clamp = 0

	# Add empty cube
	# bpy.ops.object.empty_add(type='CUBE', location=mesh_obj.location)
	# cube = bpy.context.object
	# cube.empty_draw_size = uv_size/2
	# cube.scale = (1, 1, 0)
	# cube.parent = mesh_obj
	# cube.location = (0, 0, 0)

	bpy.ops.object.select_all(action='DESELECT')
	mesh_obj.select = True
	bpy.context.scene.objects.active = mesh_obj
	# mesh_obj.location += Vector((-2.5, 0, 0))





def wrap_mesh_texture(self):
	# Wrap the mesh texture around the 
	print("Wrap Mesh Texture :)")

	# Collect UV mesh
	obj_uv = find_uv_mesh(bpy.context.selected_objects)
	if not obj_uv:
		self.report({'ERROR_INVALID_INPUT'}, "No UV mesh found" )
		return

	# Collect texture meshes
	obj_textures = []
	for obj in bpy.context.selected_objects:
		if obj != obj_uv:
			if obj.type == 'MESH':
				obj_textures.append(obj)

	if len(obj_textures) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No meshes found for mesh textures" )
		return

	print("Wrap {} texture meshes".format(len(obj_textures)))

	obj_uv.data.shape_keys.key_blocks["model"].value = 0
	



	min_z = 0
	max_z = 0
	for i in range(len(obj_textures)):
		obj = obj_textures[i]
		
		# Min Max Z
		if i == 0:
			min_z = get_bbox(obj)['min'].z
			max_z = get_bbox(obj)['max'].z
		else:
			min_z = min(min_z, get_bbox(obj)['min'].z)
			max_z = max(max_z, get_bbox(obj)['max'].z)

		# Check existing modifiers
		for modifier in obj.modifiers:
			print("M {}".format(modifier.type))
			if modifier.type == 'MESH_DEFORM':
				obj.modifiers.remove(modifier)
				break
		
	# Set thickness
	obj_uv.modifiers["Solidify"].thickness = (max_z - min_z)*1.1

	for obj in obj_textures:
		use_dynamic_bind = len(obj.modifiers) > 1

		# Add mesh modifier
		obj.select = True
		bpy.context.scene.objects.active = obj
		bpy.ops.object.modifier_add(type='MESH_DEFORM')
		bpy.context.object.modifiers["MeshDeform"].object = obj_uv
		bpy.context.object.modifiers["MeshDeform"].use_dynamic_bind = use_dynamic_bind
		bpy.ops.object.meshdeform_bind(modifier="MeshDeform")

		print(">>>"+str(bpy.context.object.modifiers["MeshDeform"]))





	
	obj_uv.data.shape_keys.key_blocks["model"].value = 1

	# Set morph back to 0
	# measure bounds (world) of mesh textures
	# set solidify size to size + offset to capture fully

	# unbind if already bind
	# Apply mesh deform modifier (if not existing)
	# enable dynamic bind if other modifiers
	# Set morph to 1
	
	# bind

	# use:
	# bpy.context.object.modifiers["MeshDeform"].use_dynamic_bind = True
	# bpy.context.object.modifiers["MeshDeform"].show_on_cage = True



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
