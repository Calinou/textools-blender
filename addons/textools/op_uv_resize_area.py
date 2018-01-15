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



def on_dropdown_size_x(self, context):
	self.size_x = int(self.dropdown_size_x)

def on_dropdown_size_y(self, context):
	self.size_y = int(self.dropdown_size_y)


class op(bpy.types.Operator):
	bl_idname = "uv.textools_uv_resize_uv"
	bl_label = "Resize Area"
	bl_description = "Resize or extend the UV area"
	bl_options = {'REGISTER', 'UNDO'}

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
		update = on_dropdown_size_x, 
		default = '1024'
	)
	dropdown_size_y = bpy.props.EnumProperty(
		items = utilities_ui.size_textures, 
		name = "", 
		update = on_dropdown_size_y, 
		default = '1024'
	)

	direction = bpy.props.EnumProperty(name='direction', items=(
		('TL',' ','Top Left', utilities_ui.icon_get("op_extend_canvas_TL_active"),0),
		('BL',' ','Bottom Left', utilities_ui.icon_get("op_extend_canvas_BL_active"),2),
		('TR',' ','Top Right', utilities_ui.icon_get("op_extend_canvas_TR_active"),1),
		('BR',' ','Bottom Right', utilities_ui.icon_get("op_extend_canvas_BR_active"),3)
	))
	
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

		return True


	def execute(self, context):


		#Store selection
		utilities_uv.selectionStore()

		# Get start and end size
		size_A = Vector([ 
			bpy.context.scene.texToolsSettings.size[0],
			bpy.context.scene.texToolsSettings.size[1]
		)
		size_B = Vector([ 
			self.size_x,
			self.size_y
		)

		resize_uv(
			self,
			self.direction,
			size_A, 
			size_B
		)
		resize_image(
			self.direction,
			size_A,
			size_B
		)

		#Restore selection
		utilities_uv.selectionRestore()

		return {'FINISHED'}


	def invoke(self, context, event):
		print("Invoke resize area")
		self.size_x = bpy.context.scene.texToolsSettings.size[0]
		self.size_y = bpy.context.scene.texToolsSettings.size[1]

		for item in utilities_ui.size_textures:
			if int(item[0]) == self.size_x:
				self.dropdown_size_x = item[0]
				break
		for item in utilities_ui.size_textures:
			if int(item[0]) == self.size_y:
				self.dropdown_size_y = item[0]
				break


		return context.window_manager.invoke_props_dialog(self, width = 120)


	def draw(self, context):
		# https://b3d.interplanety.org/en/creating-pop-up-panels-with-user-ui-in-blender-add-on/
		layout = self.layout


		layout.separator()


		layout.label(text="Size")
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
		
		col = layout.column(align=True)
		col.label("Direction")
		row = col.row(align=True)
		row.prop(self,'direction', expand=True)

		layout.separator()



def resize_uv(self, mode, size_A, size_B):
	# direction = bpy.context.scene.texToolsSettings.canvas_extend_direction
	
	# print("Execute op_extend_canvas: {} to {}".format(size_A, size_B))

	size_B.x*=2

	# Set pivot
	bpy.context.space_data.pivot_point = 'CURSOR'
	if mode == 'TL':
		bpy.ops.uv.cursor_set(location=Vector([0,1]))
	elif mode == 'TR':
		bpy.ops.uv.cursor_set(location=Vector([1,1]))
	elif mode == 'BL':
		bpy.ops.uv.cursor_set(location=Vector([0,0]))
	elif mode == 'BR':
		bpy.ops.uv.cursor_set(location=Vector([1,0]))

	# Select all UV faces
	bpy.ops.uv.select_all(action='SELECT')

	# Resize
	scale_x = size_A.x / size_B.x
	scale_y = size_A.y / size_B.y
	print("Scale {} | {}".format(scale_x, scale_y))
	bpy.ops.transform.resize(value=(scale_x, scale_y, 1.0), proportional='DISABLED')



def resize_image(mode, size_A, size_B):
	print("resize image")
	
	# check if current image not 'None'


