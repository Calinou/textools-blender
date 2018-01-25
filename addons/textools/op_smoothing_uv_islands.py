import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv
from . import utilities_ui

class op(bpy.types.Operator):
	bl_idname = "uv.textools_smoothing_uv_islands"
	bl_label = "Smooth UV Islands"
	bl_description = "Set mesh smoothing by uv islands"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False
		
		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True
	
	def execute(self, context):
		smooth_uv_islands(self, context)
		return {'FINISHED'}



def smooth_uv_islands(self, context):
	if bpy.context.active_object.mode != 'EDIT':
		bpy.ops.object.mode_set(mode='EDIT')

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	uvLayer = bm.loops.layers.uv.verify();

	# Smooth everything
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.faces_shade_smooth()
	bpy.ops.mesh.mark_sharp(clear=True)

	# Select Edges
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
	bpy.ops.uv.textools_select_islands_outline()
	bpy.ops.mesh.mark_sharp()

	# Apply Edge split modifier
	bpy.ops.object.modifier_add(type='EDGE_SPLIT')
	bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False

	bpy.ops.object.mode_set(mode='OBJECT')