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



def straighten_edges(edges):
	print("straighten "+str(len(edges))+"x")

	# Need more than 1 edge to continue
	# if len(edges) > 1:
		# Find average edge as origin


def get_edge_groups(edges):
	print("Get edge groups, edges {}x".format(len(edges))+"x")

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')	

	unmatched = edges.copy()

	for edge in edges:
		if edge in unmatched:
			# Loop select edge
			bpy.ops.mesh.select_all(action='DESELECT')
			edge.select = True
			bpy.ops.mesh.loop_multi_select(ring=False)

			group = [edge]
			for e in bm.edges:
				if e.select and e in unmatched:
					unmatched.remove(e)
					group.append(edge)

			print("Edge Group: "+str(len(group)))
					
	return [edges]






def main(context):
	print("Executing op_island_straighten_edge_loops")
   	
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
	groups = get_edge_groups(edges)

	for edges in groups:
		straighten_edges(edges)


	#Restore selection
	utilities_uv.selection_restore()

