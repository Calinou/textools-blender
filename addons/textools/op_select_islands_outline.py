import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv


class op(bpy.types.Operator):
	bl_idname = "uv.textools_select_islands_outline"
	bl_label = "Select Overlap"
	bl_description = "Select overlapping islands"
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

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False 

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False


		return True


	def execute(self, context):
		
		select_outline(context)
		return {'FINISHED'}


def select_outline(context):

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();

	#Store selection
	utilities_uv.selectionStore()


	bpy.context.scene.tool_settings.use_uv_select_sync = False

	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
	bpy.ops.mesh.select_all(action='SELECT')

	bpy.context.scene.tool_settings.uv_select_mode = 'VERTEX'
	bpy.ops.uv.select_all(action='SELECT')

	islands = utilities_uv.getSelectionIslands()
	edges = []
	for island in islands:

		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
		print("Process island..."+str(len(island))+" faces ")
		
		verts = []
		for face in island:
			for loop in face.loops:
				# loop.vert.select = True
				if loop.vert not in verts:
					verts.append(loop.vert)
				# loop[uvLayer].select = True
		# bpy.ops.mesh.select_mode(use_extend=True, use_expand=True, type='FACE')

		bpy.ops.mesh.select_all(action='DESELECT')
		for vert in verts:
			vert.select = True

		# print("Select Faces: "+str(len(verts)))
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=True, type='EDGE')
		bpy.ops.mesh.region_to_loop()

		# bpy.context.scene.update()

		edges.extend( [edge for edge in bm.edges if (edge.select and edge not in edges)] )
	
	bpy.ops.mesh.select_all(action='DESELECT')
	for edge in edges:
		edge.select = True