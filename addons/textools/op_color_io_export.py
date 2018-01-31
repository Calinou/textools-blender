import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_io_export"
	bl_label = "Export"
	bl_description = "Export current color palette to clipboard"

	@classmethod
	def poll(cls, context):
		
		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		return True
	
	def execute(self, context):
		export_colors(self, context)
		return {'FINISHED'}



def export_colors(self, context):
	
	hex_colors = []
	for i in range(bpy.context.scene.texToolsSettings.color_ID_count):
		color = getattr(bpy.context.scene.texToolsSettings, "color_ID_color_{}".format(i))
		hex_colors.append( utilities_color.color_to_hex( color) )

	bpy.context.window_manager.clipboard = ", ".join(hex_colors)
	
	
	# popup panel https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
	# 2n option: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Interface#A_popup_dialog

