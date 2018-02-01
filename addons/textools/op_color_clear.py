import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_clear"
	bl_label = "Clear Colors"
	bl_description = "Clear color materials on model"
	bl_options = {'REGISTER', 'UNDO'}
	

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
		clear_colors(self, context)
		return {'FINISHED'}



def clear_colors(self, context):
	obj = bpy.context.active_object
	
	# Store previous mode
	previous_mode = bpy.context.active_object.mode
	if bpy.context.active_object.mode != 'EDIT':
		bpy.ops.object.mode_set(mode='EDIT')

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);

	# Set all faces
	for face in bm.faces:
		face.material_index = 0

	# Clear all material slots
	bpy.ops.object.mode_set(mode='OBJECT')
	count = len(obj.material_slots)
	for i in range(count):
		bpy.ops.object.material_slot_remove()

	# Clear all materials
	for material in bpy.data.materials:
		if utilities_color.material_prefix in material.name:
			material.user_clear()
			bpy.data.materials.remove(material)

	# Clear all colors
	# bpy.context.scene.texToolsSettings.color_ID_count = 100
	# for i in range(bpy.context.scene.texToolsSettings.color_ID_count):
	# 	setattr(bpy.context.scene.texToolsSettings, "color_ID_color_{}".format(i), (0.5,0.5,0.5))
	# bpy.context.scene.texToolsSettings.color_ID_count = 4

	# Restore previous mode
	bpy.ops.object.mode_set(mode=previous_mode)