import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_straighten_edge_loops"
	bl_label = "Straight edge loops"
	bl_description = "Straighten edge loops of UV Island and relax rest"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):

		if not bpy.context.active_object:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		if bpy.context.scene.tool_settings.uv_select_mode != 'EDGE':
		 	return False


		return True


	def execute(self, context):

		main(context)
		return {'FINISHED'}




def main(context):
	print("____________________________")
   	
	#Store selection
	utilities_uv.selection_store()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()
	
	# Collect XYZ verts
	verts = []
	for face in bm.faces:
		if face.select:
			for loop in face.loops:
				if loop[uvLayer].select:
					if loop.vert not in verts:
						verts.append( loop.vert )

	print("Verts {}x".format(len(verts)))

	# Select verts
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
	bpy.ops.mesh.select_all(action='DESELECT')
	for vert in verts:
		vert.select = True

	# Get selected Edges
	bpy.ops.mesh.select_mode(use_extend=True, use_expand=False, type='EDGE') #BUG, Does not convert vert to edge selection
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
	edges = []
	for edge in bm.edges:
		if edge.select:
			edges.append(edge)

	print("Edges {}x".format(len(edges)))

	# Get edge groups
	groups = get_edge_groups(bm, edges)

	print("Groups {}x".format(len(groups)))
	
	# Restore 3D face selection
	utilities_uv.selection_restore()

	for edges in groups:
		straighten_edges(bm, uvLayer, edges)


	#Restore selection
	# utilities_uv.selection_restore()
	



def straighten_edges(bm, uvLayer, edges):
	print("straighten "+str(len(edges))+"x")

	# Get island faces
	islands = utilities_uv.getSelectionIslands()
	faces = [f for island in islands for f in island ]

	# Get Vert to UV within faces
	vert_to_uv = {}
	for face in faces:
		for loop in face.loops:
			vert = loop.vert
			uv = loop[uvLayer]
			if vert not in vert_to_uv:
				vert_to_uv[vert] = [uv];
			else:
				vert_to_uv[vert].append(uv)

	# Get edge lengths
	edge_length = {}
	for e in edges:
		uv1 = vert_to_uv[e.verts[0]][0].uv
		uv2 = vert_to_uv[e.verts[1]][0].uv
		edge_length[e] = (uv2 - uv1).length



	# TODO: sort by length? or middle edge of chain?
	edge_main = edges[0]

	# Rotate island to match main edge
	uv1 = vert_to_uv[edge_main.verts[0]][0].uv
	uv2 = vert_to_uv[edge_main.verts[1]][0].uv
	diff = uv2 - uv1
	angle = math.atan2(diff.y, diff.x)%(math.pi)

	bpy.context.space_data.pivot_point = 'CURSOR'
	bpy.ops.uv.select_linked(extend=False)
	bpy.ops.uv.cursor_set(location=uv1 + diff/2)
	bpy.ops.transform.rotate(value=angle, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')

	# Expand edges and straighten
	count = len(edges)
	processed = [edge_main]
	for i in range(count):
		if(len(processed) < len(edges)):
			verts = set([v for e in processed for v in e.verts])
			edges_expand = [e for e in edges if e not in processed and (e.verts[0] in verts or e.verts[1] in verts)]
			verts_ends = [v for e in edges_expand for v in e.verts if v in verts]
			
			for edge in edges_expand:
				
				v1 = [v for v in edge.verts if v in verts_ends][0]
				v2 = [v for v in edge.verts if v not in verts_ends][0]
				# direction
				previous_edge = [e for e in processed if e.verts[0] in edge.verts or e.verts[1] in edge.verts][0]
				prev_v1 = [v for v in previous_edge.verts if v != v1][0]
				prev_v2 = [v for v in previous_edge.verts if v == v1][0]
				direction = (vert_to_uv[prev_v2][0].uv - vert_to_uv[prev_v1][0].uv).normalized()

				for uv in vert_to_uv[v2]:
					uv.uv = vert_to_uv[v1][0].uv + direction * edge_length[edge]

			print("Procesed {}x Expand {}x".format(len(processed), len(edges_expand) ))
			print("verts_ends: {}x".format(len(verts_ends)))

			processed.extend(edges_expand)



	print("Faces: {}x".format(len(faces)))
	# Need more than 1 edge to continue
	# if len(edges) > 1:
		# Find average edge as origin


class EdgeSet:
	bm = None
	edges = []
	length = 0

	def __init__(self, bm, edges):
		self.bm = bm
		self.edges = edges

	def straighten(self):
		pass
		




def get_edge_groups(bm, edges):
	print("Get edge groups, edges {}x".format(len(edges))+"x")

	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')	

	unmatched = edges.copy()

	groups = []

	for edge in edges:
		if edge in unmatched:

			# Loop select edge
			bpy.ops.mesh.select_all(action='DESELECT')
			edge.select = True
			bpy.ops.mesh.loop_multi_select(ring=False)

			# Isolate group within edges
			group = [e for e in bm.edges if e.select and e in edges]
			groups.append(group)

			# Remove from unmatched
			for e in group:
				if e in unmatched:
					unmatched.remove(e)

			print("  Edge {} : Group: {}x , unmatched: {}".format(edge.index, len(group), len(unmatched)))

			# return
			# group = [edge]
			# for e in bm.edges:
			# 	if e.select and e in unmatched:
			# 		unmatched.remove(e)
			# 		group.append(edge)

			
					
	return groups


