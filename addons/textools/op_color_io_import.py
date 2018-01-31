import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_io_import"
	bl_label = "Import"
	bl_description = "Import hex colors from the clipboard as current color palette"

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if bpy.context.active_object not in bpy.context.selected_objects:
			return False

		if len(bpy.context.selected_objects) != 1:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		return True
	
	def execute(self, context):
		import_colors(self, context)
		return {'FINISHED'}



def import_colors(self, context):
	# Clipboard hex strings
	hex_strings = bpy.context.window_manager.clipboard.split(',')

	for i in range(len(hex_strings)):
		hex_strings[i] = hex_strings[i].strip().strip('#')

		name = "color_ID_color_{}".format(i)
		if hasattr(bpy.context.scene.texToolsSettings, name):
			# Color Index exists
			color = utilities_color.hex_to_color( hex_strings[i] )
			setattr(bpy.context.scene.texToolsSettings, name, color)
		else:
			# More colors imported than supported
			self.report({'ERROR_INVALID_INPUT'}, "Only {}x colors have been imported instead of {}x".format(
				i,len(hex_strings)
			))
			return
	
	# Set number of colors
	bpy.context.scene.texToolsSettings.color_ID_count = len(hex_strings)


	
	





