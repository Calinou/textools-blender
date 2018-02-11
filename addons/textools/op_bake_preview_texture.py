import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict

from . import settings
from . import utilities_color
from . import utilities_bake

material_prefix = "TT_atlas_"
gamma = 2.2

class op(bpy.types.Operator):
	bl_idname = "uv.textools_bake_preview_texture"
	bl_label = "Preview Texture"
	bl_description = "Preview the current UV image view background image on the selected object."
	bl_options = {'REGISTER', 'UNDO'}
	

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if len(settings.sets) == 0:
			return False
		
		# Only when we have a background image
		for area in bpy.context.screen.areas:
			if area.type == 'IMAGE_EDITOR':
				return area.spaces[0].image

		return False
	
	def execute(self, context):
		preview_texture(self, context)
		return {'FINISHED'}



def preview_texture(self, context):

	# Collect all low objects from bake sets
	objects = [obj for s in settings.sets for obj in s.objects_low if obj.data.uv_layers]



	image = None
	for area in bpy.context.screen.areas:
		if area.type == 'IMAGE_EDITOR':
			image = area.spaces[0].image
			break

	if image:

		#Change View mode to TEXTURED
		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				for space in area.spaces:
					if space.type == 'VIEW_3D':
						space.viewport_shade = 'MATERIAL'

		for obj in objects:
			print("Map {}".format(obj.name))

			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			obj.select = True
			bpy.context.scene.objects.active = obj

			
			print("Preview texture")

			print("Assign image {}".format(image.name))

			for i in range(len(obj.material_slots)):
				bpy.ops.object.material_slot_remove()


			#Create material with image
			bpy.ops.object.material_slot_add()
			obj.material_slots[0].material = utilities_bake.get_image_material(image)
			
			obj.draw_type = 'TEXTURED'