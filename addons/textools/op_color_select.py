import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_select"
	bl_label = "Assign Color"
	bl_description = "..."
	bl_options = {'REGISTER', 'UNDO'}
	
	index = bpy.props.IntProperty(description="Color Index", default=0)

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if bpy.context.active_object not in bpy.context.selected_objects:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		return True
	
	def execute(self, context):
		select_color(self, context, self.index)
		return {'FINISHED'}



def select_color(self, context, index):
	obj = bpy.context.active_object
	
	if bpy.context.active_object.mode != 'EDIT':
		bpy.ops.object.mode_set(mode='EDIT')