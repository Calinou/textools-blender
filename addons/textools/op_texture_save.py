import bpy
import bmesh
import operator
import math

from . import settings
from . import utilities_bake


class op(bpy.types.Operator):
	bl_idname = "uv.textools_texture_save"
	bl_label = "Save Texture"
	bl_description = "Save the texture"

	name = bpy.props.StringProperty(
		name="image name",
		default = ""
	)

	@classmethod
	def poll(cls, context):
		return True
	
	def execute(self, context):
		save_texture(self, context)
		return {'FINISHED'}



def save_texture(self, context):

	print("Info")
	if self.name in bpy.data.images:
		image = bpy.data.images[self.name]

		# Set background image
		if self.name in bpy.data.images:
			image = bpy.data.images[self.name]
			for area in bpy.context.screen.areas:
				if area.type == 'IMAGE_EDITOR':
					area.spaces[0].image = image

		# bpy.ops.image.save_as(save_as_render=False, filepath="file.png", show_multiview=False, use_multiview=False)
		
		

		bpy.ops.image.save_as(file_type='PNG', path="", filename="", directory="", filter_blender=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_folder=True, filemode=9)
		


		# bpy.ops.image.save_as(save_as_render=False, filepath="//test__sdsadasdauzanne_normal_tangent.png", show_multiview=False, use_multiview=False)

		# https://meshlogic.github.io/posts/blender/addons/extra-image-list/
		# https://docs.blender.org/api/blender_python_api_2_78_release/bpy.ops.image.html
		# print("filepath: {}".format(image.filepath))

		



'''
class op_ui_image_save(bpy.types.Operator):
	bl_idname = "uv.textools_ui_image_save"
	bl_label = "Save image"
	bl_description = "Save this image"

	image_name = bpy.props.StringProperty(
		name="image name",
		default = ""
	)

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		# bpy.context.scene.tool_settings.use_uv_select_sync = False
		# bpy.ops.mesh.select_all(action='SELECT')

		print("Saving image {}".format(self.image_name))
		# bpy.ops.image.save_as()
		return {'FINISHED'}

'''