import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv
from . import utilities_ui



utilities_ui.icon_register("op_extend_canvas_TL_active.png")
utilities_ui.icon_register("op_extend_canvas_TR_active.png")
utilities_ui.icon_register("op_extend_canvas_BL_active.png")
utilities_ui.icon_register("op_extend_canvas_BR_active.png")


class op(bpy.types.Operator):
	bl_idname = "uv.textools_uv_extend_canvas"
	bl_label = "Extend Canvas"
	bl_description = "Resize the UV canvas size"
	bl_options = {'REGISTER', 'UNDO'}

	# size = bpy.props.IntVectorProperty(
	# 	name = "Size",
	# 	size=2, 
	# 	description="Texture & UV size in pixels",
	# 	default = (512,512),
	# 	subtype = "XYZ"
	# )
	size_x = bpy.props.IntProperty(
		name = "Width",
		description="padding size in pixels",
		default = 1024,
		min = 1,
		max = 8192
	)
	size_y = bpy.props.IntProperty(
		name = "Height",
		description="padding size in pixels",
		default = 1024,
		min = 1,
		max = 8192
	)
	dropdown_size_x = bpy.props.EnumProperty(
		items = utilities_ui.size_textures, 
		name = "", 
		# update = on_size_dropdown_select, 
		default = '1024'
	)
	dropdown_size_y = bpy.props.EnumProperty(
		items = utilities_ui.size_textures, 
		name = "", 
		# update = on_size_dropdown_select, 
		default = '1024'
	)

	direction = bpy.props.EnumProperty(name='direction', items=(
		('TL',' ','Top Left', utilities_ui.icon_get("op_extend_canvas_TL_active"),0),
		('BL',' ','Bottom Left', utilities_ui.icon_get("op_extend_canvas_BL_active"),2),
		('TR',' ','Top Right', utilities_ui.icon_get("op_extend_canvas_TR_active"),1),
		('BR',' ','Bottom Right', utilities_ui.icon_get("op_extend_canvas_BR_active"),3)
	))
	# direction = bpy.props.EnumProperty(name='direction', items=(
	# 	('TL','up name','description'),
	# 	('TR','down name','description'),
	# 	('BL','down name','description'),
	# 	('BR','down name','description')
	# ))


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
		
		extend_canvas(self)
		return {'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self, width = 200)

	def draw(self, context):
		# https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
		layout = self.layout


		layout.separator()


		layout.label(text="New Size")
		col = layout.column(align=True)

		row = col.row(align=True)
		row.prop(self, "size_x", text="X",expand=True)
		row.prop(self, "dropdown_size_x", text="")

		row = col.row(align=True)
		row.prop(self, "size_y", text="Y",expand=True)
		row.prop(self, "dropdown_size_y", text="")


		# split = row.split(percentage=0.65)
		# c = split.column(align=True)
		# c.prop(self, "size_x", text="",expand=True)
		# c = split.column(align=True)
		# c.prop(self, "dropdown_size_x", text="")
		



		
		# box = layout.box()
		col = layout.column(align=True)
		col.label("Direction")
		row = col.row(align=True)
		row.prop(self,'direction', expand=True)

		layout.separator()


def extend_canvas(self):
	# direction = bpy.context.scene.texToolsSettings.canvas_extend_direction
	print("Execute op_extend_canvas: {}".format(222))

	#Only in Edit mode
	# if bpy.context.active_object.mode != 'EDIT':
	# 	return False



