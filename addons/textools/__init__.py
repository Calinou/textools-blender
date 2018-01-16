#    Blender TexTools, 
#    <TexTools, Blender addon for editing UVs and Texture maps.>
#    Copyright (C) <2017> <renderhjs>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
	"name": "TexTools",
	"description": "UV and texture Tools for Blender, based on ideas of the original TexTools for 3dsMax.",
	"author": "renderhjs",
	"version": (0, 8, 2),
	"blender": (2, 79, 0),
	"category": "UV",
	"location": "UV Image Editor > UVs > TexTools panel",
	"warning": "Early release, expect bugs and missing features.",
	"wiki_url": "https://bitbucket.org/renderhjs/textools-blender"
}

def get_tab_name():
	return "TexTools {}.{}".format(bl_info['version'][0], bl_info['version'][1])


# Import local modules
# More info: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
	import imp
	imp.reload(settings)
	imp.reload(utilities_bake)
	imp.reload(utilities_ui)
	
	imp.reload(op_align)
	imp.reload(op_bake)
	imp.reload(op_bake_explode)
	imp.reload(op_bake_organize_names)
	imp.reload(op_faces_iron)
	imp.reload(op_island_align_edge)
	imp.reload(op_island_mirror)
	imp.reload(op_island_relax_straighten_edges)
	imp.reload(op_island_rotate_90)
	imp.reload(op_island_straighten_edge_loops)
	imp.reload(op_islands_align_sort)
	imp.reload(op_select_islands_identical)
	imp.reload(op_select_islands_outline)
	imp.reload(op_select_islands_overlap)
	imp.reload(op_swap_uv_xyz)
	imp.reload(op_texel_density_get)
	imp.reload(op_texel_density_set)
	imp.reload(op_texture_checker)
	imp.reload(op_textures_reload)
	imp.reload(op_uv_channel_add)
	imp.reload(op_uv_channel_swap)
	imp.reload(op_uv_resize_area)

	
else:
	from . import settings
	from . import utilities_bake
	from . import utilities_ui

	from . import op_align
	from . import op_bake
	from . import op_bake_explode
	from . import op_bake_organize_names
	from . import op_faces_iron
	from . import op_island_align_edge
	from . import op_island_mirror
	from . import op_island_relax_straighten_edges
	from . import op_island_rotate_90
	from . import op_island_straighten_edge_loops
	from . import op_islands_align_sort
	from . import op_select_islands_identical
	from . import op_select_islands_outline
	from . import op_select_islands_overlap
	from . import op_swap_uv_xyz
	from . import op_texel_density_get
	from . import op_texel_density_set
	from . import op_texture_checker
	from . import op_textures_reload
	from . import op_uv_channel_add
	from . import op_uv_channel_swap
	from . import op_uv_resize_area
	

# Import general modules. Important: must be placed here and not on top
import bpy
import os
import math
import string
import bpy.utils.previews

from bpy.props import (StringProperty,
					   BoolProperty,
					   IntProperty,
					   FloatProperty,
					   FloatVectorProperty,
					   EnumProperty,
					   PointerProperty,
					   )


class Panel_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	# here you define the addons customizable props
	# some_prop = bpy.props.FloatProperty(default=1.0)

	# here you specify how they are drawn
	def draw(self, context):
		layout = self.layout

		layout.label(text="Additional Links")

		row = layout.row()
		split = row.split(percentage=0.33)
		
		c = split.column()
		c.operator("wm.url_open", text="Donate", icon='HELP').url = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZC9X4LE7CPQN6"
		c = split.column()
		c.operator("wm.url_open", text="GIT Source", icon='WORDWRAP_ON').url = "https://bitbucket.org/renderhjs/textools-blender/src"
		c = split.column()
		c.operator("wm.url_open", text="BlederArtist BBS", icon='BLENDER').url = "https://blenderartists.org/forum/showthread.php?443182-TexTools-for-Blender"



class op_debug(bpy.types.Operator):
	bl_idname = "uv.textools_debug"
	bl_label = "Debug"
	bl_description = "Open console and enable dbug mode"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		bpy.ops.wm.console_toggle()# Toggle Console (Windows only)
		bpy.app.debug = True# Debug Vertex indexies
		bpy.context.object.data.show_extra_indices = True
		bpy.app.debug_value = 1 #Set to Non '0
		return {'FINISHED'}



class op_select_bake_set(bpy.types.Operator):
	bl_idname = "uv.textools_select_bake_set"
	bl_label = "Select"
	bl_description = "Select this bake set in scene"

	select_set = bpy.props.StringProperty(default="")

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		print("Set: "+self.select_set)
		if self.select_set != "":
			for set in settings.sets:
				if set.name == self.select_set:
					# Select this entire set
					bpy.ops.object.select_all(action='DESELECT')
					for obj in set.objects_low:
						obj.select = True
					for obj in set.objects_high:
						obj.select = True
					for obj in set.objects_cage:
						obj.select = True
					# Set active object to low poly to better visualize high and low wireframe color
					if len(set.objects_low) > 0:
						bpy.context.scene.objects.active = set.objects_low[0]

					break
		return {'FINISHED'}



class op_select_bake_type(bpy.types.Operator):
	bl_idname = "uv.textools_select_bake_type"
	bl_label = "Select"
	bl_description = "Select bake objects of this type"

	select_type = bpy.props.StringProperty(default='low')

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		objects = []
		for set in settings.sets:
			if self.select_type == 'low':
				objects+=set.objects_low
			elif self.select_type == 'high':
				objects+=set.objects_high
			elif self.select_type == 'cage':
				objects+=set.objects_cage
			elif self.select_type == 'issue' and set.has_issues:
				objects+=set.objects_low
				objects+=set.objects_high
				objects+=set.objects_cage

		bpy.ops.object.select_all(action='DESELECT')
		for obj in objects:
			obj.select = True

		return {'FINISHED'}



def on_dropdown_size(self, context):
	size = int(bpy.context.scene.texToolsSettings.size_dropdown)
	bpy.context.scene.texToolsSettings.size[0] = size;
	bpy.context.scene.texToolsSettings.size[1] = size;

	if size <= 128:
		bpy.context.scene.texToolsSettings.padding = 2
	elif size <= 512:
		bpy.context.scene.texToolsSettings.padding = 4
	else:
		bpy.context.scene.texToolsSettings.padding = 8



def on_dropdown_uv_channel(self, context):
	if bpy.context.active_object != None:
		if bpy.context.active_object.type == 'MESH':
			if bpy.context.object.data.uv_layers:

				# Change Mesh UV Channel
				index = int(bpy.context.scene.texToolsSettings.uv_channel)
				if index < len(bpy.context.object.data.uv_textures):
					bpy.context.object.data.uv_textures.active_index = index



def get_dropdown_uv_values(self, context):
	# Dynamic Dropdowns: https://blender.stackexchange.com/questions/35223/whats-the-correct-way-of-implementing-dynamic-dropdown-menus-in-python
	
	# Requires mesh and UV data
	if bpy.context.active_object != None:
		if bpy.context.active_object.type == 'MESH':
			if bpy.context.object.data.uv_layers:
				options = []
				step = 0
				for uvLoop in bpy.context.object.data.uv_layers:
					# options.append((str(step), "#{}  {}".format(step+1, uvLoop.name), "Change UV channel to '{}'".format(uvLoop.name), step))
					options.append((str(step), "#{}".format(step+1), "Change UV channel to '{}'".format(uvLoop.name), step))
					step+=1

				return options
	return []




class TexToolsSettings(bpy.types.PropertyGroup):
	#Width and Height
	size = bpy.props.IntVectorProperty(
		name = "Size",
		size=2, 
		description="Texture & UV size in pixels",
		default = (512,512),
		subtype = "XYZ"
	)

	size_dropdown = bpy.props.EnumProperty(
		items = utilities_ui.size_textures, 
		name = "Texture Size", 
		update = on_dropdown_size, 
		default = '1024'
	)

	uv_channel = bpy.props.EnumProperty(
		items = get_dropdown_uv_values, 
		name = "UV", 
		update = on_dropdown_uv_channel
	)

	#Padding
	padding = bpy.props.IntProperty(
		name = "Padding",
		description="padding size in pixels",
		default = 4,
		min = 0,
		max = 256
	)
	
	bake_samples = bpy.props.FloatProperty(
		name = "Samples",
		description = "Samples in Cycles for Baking. The higher the less noise. Default: 64",
		default = 64,
		min = 1,
		max = 4000
	)
	bake_ray_distance = bpy.props.FloatProperty(
		name = "Ray Dist.",
		description = "Ray distance when baking. When using cage used as extrude distance",
		default = 0.01,
		min = 0.000,
		max = 100.00
	)
	bake_force_single = bpy.props.BoolProperty(
		name="Single Texture",
		description="Force a single texture bake accross all selected objects",
		default = False
	)
	bake_sampling = bpy.props.EnumProperty(items= 
		[('1', 'None', 'No Anti Aliasing (Fast)'), 
		('2', '2x', 'Render 2x and downsample'), 
		('4', '4x', 'Render 2x and downsample')], name = "AA", default = '1'
	)
	bake_freeze_selection = bpy.props.BoolProperty(
		name="Lock",
		description="Lock baking sets, don't change with selection",
		default = False
	)
	texel_mode_scale = bpy.props.EnumProperty(items= 
		[('ISLAND', 'Islands', 'Scale UV islands to match Texel Density'), 
		('ALL', 'All', 'Scale all UVs together to match Texel Density')], 
		name = "Mode", 
		default = 'ISLAND'
	)
	texel_density = bpy.props.FloatProperty(
		name = "Texel",
		description = "Texel size or Pixels per 1 unit ratio",
		default = 256,
		min = 0.0,
		max = 100.00
	)

	# bake_do_save = bpy.props.BoolProperty(
	# 	name="Save",
	# 	description="Save the baked texture?",
	# 	default = False)



class Panel_Units(bpy.types.Panel):
	bl_label = " "
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = get_tab_name()
	

	def draw_header(self, _):
		layout = self.layout
		layout.label(text="Size: {} x {}".format(bpy.context.scene.texToolsSettings.size[0], bpy.context.scene.texToolsSettings.size[1]))

	def draw(self, context):
		layout = self.layout
		
		if bpy.app.debug_value != 0:
			row = layout.row()
			row.alert =True
			row.operator(op_debug.bl_idname, icon="CONSOLE")
		
		#---------- Settings ------------
		row = layout.row()
		col = row.column(align=True)
		col.prop(context.scene.texToolsSettings, "size_dropdown", text="Size")
		
		r = col.row(align = True)
		r.prop(context.scene.texToolsSettings, "size", text="")
		col.prop(context.scene.texToolsSettings, "padding", text="Padding")
		
		
		col.operator(op_uv_resize_area.op.bl_idname, text="Resize", icon_value = icon_get("op_extend_canvas_open"))
		# r = col.row(align = True)
		col.separator()
		col.operator(op_texture_checker.op.bl_idname, text ="Checker", icon_value = icon_get("checkerMap"))
		col.operator(op_textures_reload.op.bl_idname, text="Reload Textures", icon_value = icon_get("textures_reload"))

		# col.operator(op_extend_canvas.op.bl_idname, text="Resize", icon_value = icon_get("op_extend_canvas"))
		

		# UV Channel
		
		row = layout.row()

		has_uv_channel = False
		if bpy.context.active_object != None and len(bpy.context.selected_objects) == 1:
			if bpy.context.active_object in bpy.context.selected_objects:
				if bpy.context.active_object.type == 'MESH':
					
					split = row.split(percentage=0.25)
					c = split.column(align=True)
					c.label(text="UV")#, icon='GROUP_UVS'

					
					if not bpy.context.object.data.uv_layers:
						c = split.column(align=True)
						row = c.row(align=True)
						# row.label(text="None", icon= 'ERROR')

						row.operator(op_uv_channel_add.op.bl_idname, text="Add", icon = 'ZOOMIN')
					else:
						c = split.column(align=True)
						row = c.row(align=True)
						row.prop(context.scene.texToolsSettings, "uv_channel", text="")

						c = split.column(align=True)
						row = c.row(align=True)
						row.alignment = 'RIGHT'

						r = row.row(align=True)
						r.active = bpy.context.object.data.uv_textures.active_index > 0
						r.operator(op_uv_channel_swap.op.bl_idname, text="", icon = 'TRIA_UP_BAR').is_down = False;
						
						r = row.row(align=True)
						r.active = bpy.context.object.data.uv_textures.active_index < (len(bpy.context.object.data.uv_textures)-1)
						r.operator(op_uv_channel_swap.op.bl_idname, text="", icon = 'TRIA_DOWN_BAR').is_down = True;

					has_uv_channel = True
		if not has_uv_channel:
			row.label(text="UV")
			

class Panel_Layout(bpy.types.Panel):
	bl_label = "UV Layout"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = get_tab_name()
	
	# def draw_header(self, _):
	# 	layout = self.layout
	# 	layout.label(text="", icon_value=icon("logo"))


	def draw(self, context):
		layout = self.layout
		
		
		if bpy.app.debug_value != 0:
			col = layout.column(align=True)
			col.alert = True
			col.operator(op_swap_uv_xyz.op.bl_idname, text="Swap UV/XYZ", icon_value = icon_get("swap_uv_xyz"))
			col.operator(op_island_straighten_edge_loops.op.bl_idname, text="Straight & Relax", icon_value = icon_get("island_relax_straighten_edges"))
			row = col.row(align=True)
			row.operator(op_island_mirror.op.bl_idname, text="Mirror", icon_value = icon_get("mirror")).is_stack = False;
			row.operator(op_island_mirror.op.bl_idname, text="Stack", icon_value = icon_get("mirror")).is_stack = True;

		#---------- Layout ------------
		# layout.label(text="Layout")

		box = layout.box()
		col = box.column(align=True)
		row = col.row(align=True)
		row.operator(op_island_align_edge.op.bl_idname, text="Align Edge", icon_value = icon_get("island_align_edge"))
		# col.operator(op_island_relax_straighten_edges.op.bl_idname, text="Straight & Relax", icon_value = icon_get("island_relax_straighten_edges"))

		row = col.row(align=True)
		row.operator(op_island_rotate_90.op.bl_idname, text="-90°", icon_value = icon_get("island_rotate_90_left")).angle = -math.pi / 2
		row.operator(op_island_rotate_90.op.bl_idname, text="+90°", icon_value = icon_get("island_rotate_90_right")).angle = math.pi / 2

		
		row = box.row(align=True)
		col = row.column(align=True)
		col.label(text="")
		col.operator(op_align.op.bl_idname, text="←", icon_value = icon_get("alignLeft")).direction = "left"
		
		col = row.column(align=True)
		col.operator(op_align.op.bl_idname, text="↑", icon_value = icon_get("alignTop")).direction = "top"
		col.operator(op_align.op.bl_idname, text="↓", icon_value = icon_get("alignBottom")).direction = "bottom"

		col = row.column(align=True)
		col.label(text="")
		col.operator(op_align.op.bl_idname, text="→", icon_value = icon_get("alignRight")).direction = "right"


		aligned = box.row(align=True)
		op = aligned.operator(op_islands_align_sort.op.bl_idname, text="Sort H", icon_value = icon_get("islands_align_sort_h"))
		op.is_vertical = False;
		op.padding = utilities_ui.get_padding()
		
		op = aligned.operator(op_islands_align_sort.op.bl_idname, text="Sort V", icon_value = icon_get("islands_align_sort_v"))
		op.is_vertical = True;
		op.padding = utilities_ui.get_padding()

		aligned = box.row(align=True)
		col = aligned.column(align=True)
		row = col.row(align=True)
		
		col.operator(op_faces_iron.op.bl_idname, text="Iron Faces", icon_value = icon_get("faces_iron"))
		

		#---------- Selection ------------
		layout.label(text="Select")
		row = layout.row()
		box = row.box()
		col = box.column(align=True)
		row = col.row(align=True)
		row.operator(op_select_islands_identical.op.bl_idname, text="Similar", icon_value = icon_get("islands_select_identical"))
		row.operator(op_select_islands_overlap.op.bl_idname, text="Overlap", icon_value = icon_get("islands_select_overlapping"))
		# aligned = box.row(align=True)
		col.operator(op_select_islands_outline.op.bl_idname, text="Island Bounds", icon_value = icon_get("op_select_islands_outline"))
		

		#---------- Texel ------------
		if bpy.app.debug_value != 0:
		
			layout.label(text="Texels")
			# row = layout.row()
			box = layout.box()
			col = box.column(align=True)

			col.separator()
			col = box.column(align=True)
			col.alert = True
			
			row = col.row(align=True)
			row.prop(context.scene.texToolsSettings, "texel_density", text="")
			row.operator(op_texel_density_get.op.bl_idname, text="", icon = 'EYEDROPPER')

			row = col.row(align=True)
			row.operator(op_texel_density_set.op.bl_idname, text="Apply", icon = 'FACESEL_HLT')
			row.prop(context.scene.texToolsSettings, "texel_mode_scale", text = "", expand=False)
		
			# col.prop(context.scene.texToolsSettings, "bake_force_single", text="Per Island")
			# col = box.column(align=True)
			# row = col.row(align=True)
			# row.label(text="Mode")
			# row.prop(context.scene.texToolsSettings, "texel_mode_scale", expand=True)
		
			
		# 
		
		#---------- ID Colors ------------
		#Example custom UI list: https://blender.stackexchange.com/questions/47840/is-bpy-props-able-to-create-a-list-of-lists
		#Example assign vertex colors: https://blender.stackexchange.com/questions/30841/how-to-view-vertex-colors
		#Color Palette: https://blender.stackexchange.com/questions/73122/how-do-i-create-palette-ui-object

		# row = layout.row()
		# box = row.box()
		# box.label(text="ID Colors")
		# box.operator(bpy.ops.paint.sample_color.idname())
		# box.template_palette(context.scene.texToolsSettings, "id_palette", color=True)
		


class Panel_Bake(bpy.types.Panel):
	bl_label = "Texture Baking"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = get_tab_name()
	
	def draw(self, context):
		layout = self.layout
		
		#----------- Baking -------------
		row = layout.row()
		box = row.box()
		col = box.column(align=True)

		if not (bpy.context.scene.texToolsSettings.bake_freeze_selection and len(settings.sets) > 0):
			# Update sets
			settings.sets = utilities_bake.get_bake_sets()


		# Bake Button, Samples, Single option
		count = 0
		if bpy.context.scene.texToolsSettings.bake_force_single and len(settings.sets) > 0:
			count = 1
		else:
			count = len(settings.sets)
		col.operator(op_bake.op.bl_idname, text = "Bake {}x".format(count), icon='RENDER_STILL');#icon_value = icon_get("op_bake")
		col.prop(context.scene.texToolsSettings, "bake_sampling", icon_value =icon_get("bake_anti_alias"))
		
		row = col.row(align=True)
		row.active = len(settings.sets) > 0
		row.prop(context.scene.texToolsSettings, "bake_force_single", text="Single")
		if len(settings.sets) > 0 and bpy.context.scene.texToolsSettings.bake_force_single:
			row.label(text="'{}'".format(settings.sets[0].name))
		else:
			row.label(text="")


		if bpy.app.debug_value != 0:
			row = col.row()
			row.alert = True
			row.prop(context.scene.texToolsSettings, "bake_force_single", text="Dither Floats")




		col.separator()


		# Bake Mode
		col.template_icon_view(context.scene, "TT_bake_mode")
		settings.bake_mode = str(bpy.context.scene.TT_bake_mode).replace(".png","").replace("bake_" ,"").lower()
		

		# Optional Parameters
		col.separator()
		for set in settings.sets:
			if len(set.objects_low) > 0 and len(set.objects_high) > 0:
				col.prop(context.scene.texToolsSettings, "bake_ray_distance")
				break		

		if settings.bake_mode == 'ao':
			col.prop(context.scene.texToolsSettings, "bake_samples")
		
		

		row = layout.row()
		box = row.box()

		col = box.column(align=True)
		col.operator(op_bake_organize_names.op.bl_idname, text = "Organize {}x".format(len(bpy.context.selected_objects)), icon = 'BOOKMARKS')
		col.operator(op_bake_explode.op.bl_idname, text = "Explode", icon_value = icon_get("op_bake_explode"));
		
		# if bpy.app.debug_value != 0:
		# 	row = box.row(align=True)
		# 	row.alert = True

			
		# Freeze Selection
		col = box.column(align=True)
		row = col.row(align=True)
		row.active = len(settings.sets) > 0 or bpy.context.scene.texToolsSettings.bake_freeze_selection
		icon = 'LOCKED' if bpy.context.scene.texToolsSettings.bake_freeze_selection else 'UNLOCKED'
		row.prop(context.scene.texToolsSettings, "bake_freeze_selection",text="Lock {}x".format(len(settings.sets)), icon=icon)


		# Select by type
		if len(settings.sets) > 0:
			row = col.row(align=True)
			row.active = len(settings.sets) > 0

			count_types = [0,0,0,0]
			for set in settings.sets:
				if set.has_issues:
					count_types[0]+=1
				if len(set.objects_low) > 0:
					count_types[1]+=1
				if len(set.objects_high) > 0:
					count_types[2]+=1
				if len(set.objects_cage) > 0:
					count_types[3]+=1

			row.label(text="Select")
			if count_types[0] > 0:
				row.operator(op_select_bake_type.bl_idname, text = "", icon = 'ERROR').select_type = 'issue'
			row.operator(op_select_bake_type.bl_idname, text = "", icon_value = icon_get("bake_obj_low")).select_type = 'low'
			row.operator(op_select_bake_type.bl_idname, text = "", icon_value = icon_get("bake_obj_high")).select_type = 'high'
			if count_types[3] > 0:
				row.operator(op_select_bake_type.bl_idname, text = "", icon_value = icon_get("bake_obj_cage")).select_type = 'cage'


		if len(settings.sets) > 0:

			# List bake sets
			box2 = box.box()

			

			row = box2.row()
			split = row.split(percentage=0.55)
			c = split.column(align=True)

			for s in range(0, len(settings.sets)):
				set = settings.sets[s]
				r = c.row(align=True)
				r.active = not (bpy.context.scene.texToolsSettings.bake_force_single and s > 0)

				if set.has_issues:
					r.operator(op_select_bake_set.bl_idname, text=set.name, icon='ERROR').select_set = set.name
				else:
					r.operator(op_select_bake_set.bl_idname, text=set.name).select_set = set.name


			c = split.column(align=True)
			for set in settings.sets:
				r = c.row(align=True)

				if len(set.objects_low) > 0:
					r.label(text="{}".format(len(set.objects_low)), icon_value = icon_get("bake_obj_low"))
				else:
					r.label(text="")

				if len(set.objects_high) > 0:
					r.label(text="{}".format(len(set.objects_high)), icon_value = icon_get("bake_obj_high"))
				else:
					r.label(text="")

				if len(set.objects_cage) > 0:
					r.label(text="{}".format(len(set.objects_cage)), icon_value = icon_get("bake_obj_cage"))
				else:
					r.label(text="")
		
			


keymaps = []

def icon_get(name):
	return utilities_ui.icon_get(name)

	
def register():
	bpy.utils.register_module(__name__)
	
	#Register settings
	# bpy.utils.register_class(TexToolsSettings)
	bpy.types.Scene.texToolsSettings = bpy.props.PointerProperty(type=TexToolsSettings)
	
	#GUI Utilities
	utilities_ui.register()

	# Register Icons
	icons = [
		# "logo.png", 
		"op_extend_canvas_open.png",
		"islands_align_sort_h.png", 
		"islands_align_sort_v.png", 
		"checkerMap.png", 
		"swap_uv_xyz.png", 
		"island_rotate_90_left.png", 
		"island_rotate_90_right.png", 
		"textures_reload.png", 
		"island_align_edge.png", 
		"island_relax_straighten_edges.png", 
		"op_select_islands_outline.png", 
		"alignBottom.png", 
		"alignLeft.png", 
		"alignRight.png", 
		"alignTop.png", 
		"mirror.png", 
		"setup_split_uv.png", 
		"faces_iron.png", 
		"islands_select_identical.png", 
		"islands_select_overlapping.png", 
		"op_bake.png", 
		"op_bake_explode.png", 
		"bake_obj_low.png", 
		"bake_obj_high.png", 
		"bake_obj_cage.png", 
		"bake_anti_alias.png", 
		"explode.png"
	]
	for icon in icons:
		utilities_ui.icon_register(icon)
	

	# #Key Maps
	# wm = bpy.context.window_manager
	# if wm.keyconfigs.addon is not None:
	# 	# https://github.com/RayMairlot/UV-Rotate-Shortcuts/blob/master/UV%20Rotate.py

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'UP_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "top"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'DOWN_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "bottom"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'LEFT_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "left"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_align.op.bl_idname, 'RIGHT_ARROW', 'PRESS', alt=True)
	# 	kmi.properties.direction = "right"
	# 	keymaps.append((km, kmi))

	# 	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# 	kmi = km.keymap_items.new(op_island_mirror.op.bl_idname, 'M', 'PRESS', alt=True)
	# 	kmi.properties.is_stack = False
	# 	keymaps.append((km, kmi))



def unregister():

	bpy.utils.unregister_module(__name__)

	#Unregister Settings
	del bpy.types.Scene.texToolsSettings

	#GUI Utilities
	utilities_ui.unregister()

	#handle the keymap
	for km, kmi in keymaps:
		km.keymap_items.remove(kmi)
	keymaps.clear()


if __name__ == "__main__":
	register()
