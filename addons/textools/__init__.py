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
	"version": (0, 7, 0),
	"blender": (2, 79, 0),
	"category": "UV",
	"location": "UV Image Editor > UVs > TexTools panel",
	"warning": "Early release, expect bugs and missing features.",
	"wiki_url": "https://bitbucket.org/renderhjs/textools-blender"
}

# Import local modules
# More info: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
	import imp
	imp.reload(utilities_gui)
	imp.reload(utilities_bake)
	imp.reload(settings)
	
	imp.reload(op_islands_align_sort)
	imp.reload(op_texture_checker)
	imp.reload(op_align)
	imp.reload(op_textures_reload)
	imp.reload(op_bake)
	imp.reload(op_bake_explode)
	imp.reload(op_swap_uv_xyz)
	imp.reload(op_island_align_edge)
	imp.reload(op_select_islands_identical)
	imp.reload(op_select_islands_overlap)
	imp.reload(op_select_islands_outline)
	imp.reload(op_island_mirror)
	imp.reload(op_island_relax_straighten_edges)
	imp.reload(op_island_straighten_edge_loops)
	imp.reload(op_island_rotate_90)
	imp.reload(op_setup_split_uv)
	imp.reload(op_faces_iron)

	
else:
	from . import utilities_gui
	from . import utilities_bake
	from . import settings

	from . import op_islands_align_sort
	from . import op_texture_checker
	from . import op_align
	from . import op_textures_reload
	from . import op_bake
	from . import op_bake_explode
	from . import op_swap_uv_xyz
	from . import op_island_align_edge
	from . import op_select_islands_identical
	from . import op_select_islands_overlap
	from . import op_select_islands_outline
	from . import op_island_mirror
	from . import op_island_relax_straighten_edges
	from . import op_island_straighten_edge_loops
	from . import op_island_rotate_90
	from . import op_setup_split_uv
	from . import op_faces_iron
	

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


class SomeAddonPrefs(bpy.types.AddonPreferences):
	bl_idname = __name__
	# here you define the addons customizable props
	some_prop = bpy.props.FloatProperty(default=1.0)

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


def on_size_dropdown_select(self, context):
	size = int(bpy.context.scene.texToolsSettings.size_dropdown)

	bpy.context.scene.texToolsSettings.size[0] = size;
	bpy.context.scene.texToolsSettings.size[1] = size;
	bpy.context.scene.texToolsSettings.padding = 8


class TexToolsSettings(bpy.types.PropertyGroup):
	#Width and Height
	size = bpy.props.IntVectorProperty(
		name = "Size",
		size=2, 
		description="Texture & UV size in pixels",
		default = (1024,1024),
		subtype = "XYZ"
	)

	size_dropdown = bpy.props.EnumProperty(items= [('64', '64', ''), 
		('128', '128', ''), 
		('256', '256', ''), 
		('512', '512', ''), 
		('1024', '1024', ''), 
		('2048', '2048', ''), 
		('4096', '4096', '')], name = "Texture Size", update = on_size_dropdown_select, default = '1024'
	)

	#Padding
	padding = bpy.props.IntProperty(
		name = "Padding",
		description="padding size in pixels",
		default = 4,
		min = 1,
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
		name="Freeze Selection",
		description="When frozen baking sets are not updated",
		default = False
	)


	bake_do_save = bpy.props.BoolProperty(
		name="Save",
		description="Save the baked texture?",
		default = False)

	id_palette = None;#bpy.types.UILayout.template_palette()



def getIcon(name):
	return preview_icons[name].icon_id


class TexToolsPanel(bpy.types.Panel):
	bl_label = "TexTools"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	
	def draw_header(self, _):
		layout = self.layout
		layout.label(text="", icon_value=getIcon("logo"))


	def draw(self, context):
		layout = self.layout
		
		if bpy.app.debug or bpy.app.debug_value != 0:
			layout.operator(op_debug.bl_idname, icon="CONSOLE")
		
		#---------- Settings ------------
		row = layout.row()
		col = row.column(align=True)
		col.prop(context.scene.texToolsSettings, "size_dropdown", text="Size")
		
		col.prop(context.scene.texToolsSettings, "size", text="")
		col.prop(context.scene.texToolsSettings, "padding", text="Padding")

		if bpy.app.debug_value != 0:
			layout.alert = True
			row = layout.row(align=True)
			row.operator(op_swap_uv_xyz.op.bl_idname, text="Swap UV/XYZ", icon_value = getIcon("swap_uv_xyz"))
			row.operator(op_island_straighten_edge_loops.op.bl_idname, text="Straight & Relax", icon_value = getIcon("island_relax_straighten_edges"))
			row.operator(op_setup_split_uv.op.bl_idname, text="Split", icon_value = getIcon("setup_split_uv"))
			
			row = layout.row(align=True)
			row.operator(op_island_mirror.op.bl_idname, text="Mirror", icon_value = getIcon("mirror")).is_stack = False;
			row.operator(op_island_mirror.op.bl_idname, text="Stack", icon_value = getIcon("mirror")).is_stack = True;
		
			layout.alert = False

		#---------- Layout ------------
		# layout.label(text="Layout")

		box = layout.box()
		col = box.column(align=True)
		row = col.row(align=True)
		row.operator(op_island_align_edge.op.bl_idname, text="Align Edge", icon_value = getIcon("island_align_edge"))
		# col.operator(op_island_relax_straighten_edges.op.bl_idname, text="Straight & Relax", icon_value = getIcon("island_relax_straighten_edges"))

		row = col.row(align=True)
		row.operator(op_island_rotate_90.op.bl_idname, text="-90°", icon_value = getIcon("island_rotate_90_left")).angle = -math.pi / 2
		row.operator(op_island_rotate_90.op.bl_idname, text="+90°", icon_value = getIcon("island_rotate_90_right")).angle = math.pi / 2

		
		row = box.row(align=True)
		col = row.column(align=True)
		col.label(text="")
		col.operator(op_align.op.bl_idname, text="←", icon_value = getIcon("alignLeft")).direction = "left"
		
		col = row.column(align=True)
		col.operator(op_align.op.bl_idname, text="↑", icon_value = getIcon("alignTop")).direction = "top"
		col.operator(op_align.op.bl_idname, text="↓", icon_value = getIcon("alignBottom")).direction = "bottom"

		col = row.column(align=True)
		col.label(text="")
		col.operator(op_align.op.bl_idname, text="→", icon_value = getIcon("alignRight")).direction = "right"


		aligned = box.row(align=True)
		op = aligned.operator(op_islands_align_sort.op.bl_idname, text="Sort H", icon_value = getIcon("islands_align_sort_h"))
		op.is_vertical = False;
		op.padding = utilities_gui.get_padding()
		
		op = aligned.operator(op_islands_align_sort.op.bl_idname, text="Sort V", icon_value = getIcon("islands_align_sort_v"))
		op.is_vertical = True;
		op.padding = utilities_gui.get_padding()

		aligned = box.row(align=True)
		col = aligned.column(align=True)
		row = col.row(align=True)
		
		col.operator(op_faces_iron.op.bl_idname, text="Iron Faces", icon_value = getIcon("faces_iron"))
		

		#---------- Selection ------------
		layout.label(text="Select")
		row = layout.row()
		box = row.box()
		col = box.column(align=True)
		row = col.row(align=True)
		row.operator(op_select_islands_identical.op.bl_idname, text="Similar", icon_value = getIcon("islands_select_identical"))
		row.operator(op_select_islands_overlap.op.bl_idname, text="Overlap", icon_value = getIcon("islands_select_overlapping"))
		# aligned = box.row(align=True)
		col.operator(op_select_islands_outline.op.bl_idname, text="Island Bounds", icon_value = getIcon("op_select_islands_outline"))
		

		#---------- Textures ------------
		layout.label(text="Textures")
		row = layout.row()
		box = row.box()
		col = box.column(align=True)
		col.operator(op_texture_checker.op.bl_idname, text ="Checker", icon_value = getIcon("checkerMap"))
		col.operator(op_textures_reload.op.bl_idname, text="Reload All", icon_value = getIcon("textures_reload"))

		#----------- Baking -------------
		layout.separator()

		row = layout.row()
		box = row.box()
		col = box.column(align=True)

		if not bpy.context.scene.texToolsSettings.bake_freeze_selection:
			# Update sets
			settings.sets = utilities_bake.get_bake_pairs()

		# Bake Button, Samples, Single option
		count = 0
		if bpy.context.scene.texToolsSettings.bake_force_single and len(settings.sets) > 0:
			count = 1
		else:
			count = len(settings.sets)
		col.operator(op_bake.op.bl_idname, text = "Bake {}x".format(count), icon_value = getIcon("op_bake"));
		col.prop(context.scene.texToolsSettings, "bake_sampling", icon_value =getIcon("bake_anti_alias"))
		
		row = col.row(align=True)
		row.prop(context.scene.texToolsSettings, "bake_force_single", text="Single")
		if len(settings.sets) > 0 and bpy.context.scene.texToolsSettings.bake_force_single:
			row.label(text="'{}'".format(settings.sets[0].name))
		else:
			row.label(text="")

		col.separator()


		# Bake Mode
		col.template_icon_view(context.scene, "TT_bake_mode")
		settings.bake_mode = str(bpy.context.scene.TT_bake_mode).replace(".png","").replace("bake_" ,"")
		col.separator()
		
		
		# Optional Parameters
		for set in settings.sets:
			if len(set.objects_low) > 0 and len(set.objects_high) > 0:
				col.prop(context.scene.texToolsSettings, "bake_ray_distance")
				break		
		
		if settings.bake_mode == 'ao':
			col.prop(context.scene.texToolsSettings, "bake_samples")
		


		# List bake sets
		row = box.row()
		split = row.split(percentage=0.4)
		c = split.column()

		for s in range(0, len(settings.sets)):
			set = settings.sets[s]
			r = c.row()
			r.active = not (bpy.context.scene.texToolsSettings.bake_force_single and s > 0)
			r.label(text=set.name)


		c = split.column()
		for set in settings.sets:
			r = c.row(align=True)

			if len(set.objects_low) > 0:
				r.label(text="{}".format(len(set.objects_low)), icon_value = getIcon("bake_obj_low"))
			else:
				r.label(text="")

			if len(set.objects_high) > 0:
				r.label(text="{}".format(len(set.objects_high)), icon_value = getIcon("bake_obj_high"))
			else:
				r.label(text="")

			if len(set.objects_cage) > 0:
				r.label(text="{}".format(len(set.objects_cage)), icon_value = getIcon("bake_obj_cage"))
			else:
				r.label(text="")
		
		# box.separator()
		icon = 'LOCKED' if bpy.context.scene.texToolsSettings.bake_freeze_selection else 'UNLOCKED'
		box.prop(context.scene.texToolsSettings, "bake_freeze_selection", icon=icon)


		if bpy.app.debug_value != 0:
			box.alert = True
			box.operator(op_bake_explode.op.bl_idname, text = "Explode", icon_value = getIcon("op_bake_explode"));
		
		

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
		


keymaps = []

def registerIcon(fileName):
	# global custom_icons
	name = fileName.split('.')[0]   # Don't include file extension
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	preview_icons.load(name, os.path.join(icons_dir, fileName), 'IMAGE')
	
def register():
	bpy.utils.register_module(__name__)
	
	#Register settings
	# bpy.utils.register_class(TexToolsSettings)
	bpy.types.Scene.texToolsSettings = bpy.props.PointerProperty(type=TexToolsSettings)
	
	#GUI Utilities
	utilities_gui.register()

	# Register global Icons
	global preview_icons
	preview_icons = bpy.utils.previews.new()
	registerIcon("logo.png")
	registerIcon("islands_align_sort_h.png")
	registerIcon("islands_align_sort_v.png")
	registerIcon("checkerMap.png")
	registerIcon("swap_uv_xyz.png")
	registerIcon("island_rotate_90_left.png")
	registerIcon("island_rotate_90_right.png")
	registerIcon("textures_reload.png")
	registerIcon("island_align_edge.png")
	registerIcon("island_relax_straighten_edges.png")
	registerIcon("op_select_islands_outline.png")
	registerIcon("alignBottom.png")
	registerIcon("alignLeft.png")
	registerIcon("alignRight.png")
	registerIcon("alignTop.png")
	registerIcon("mirror.png")
	registerIcon("setup_split_uv.png")
	registerIcon("faces_iron.png")
	registerIcon("islands_select_identical.png")
	registerIcon("islands_select_overlapping.png")
	registerIcon("op_bake.png")
	registerIcon("op_bake_explode.png")
	registerIcon("bake_obj_low.png")
	registerIcon("bake_obj_high.png")
	registerIcon("bake_obj_cage.png")
	registerIcon("bake_anti_alias.png")
	registerIcon("explode.png")
	

	#Key Maps
	wm = bpy.context.window_manager
	if wm.keyconfigs.addon is not None:
		# https://github.com/RayMairlot/UV-Rotate-Shortcuts/blob/master/UV%20Rotate.py

		km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
		kmi = km.keymap_items.new(op_align.op.bl_idname, 'UP_ARROW', 'PRESS', alt=True)
		kmi.properties.direction = "top"
		keymaps.append((km, kmi))

		km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
		kmi = km.keymap_items.new(op_align.op.bl_idname, 'DOWN_ARROW', 'PRESS', alt=True)
		kmi.properties.direction = "bottom"
		keymaps.append((km, kmi))

		km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
		kmi = km.keymap_items.new(op_align.op.bl_idname, 'LEFT_ARROW', 'PRESS', alt=True)
		kmi.properties.direction = "left"
		keymaps.append((km, kmi))

		km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
		kmi = km.keymap_items.new(op_align.op.bl_idname, 'RIGHT_ARROW', 'PRESS', alt=True)
		kmi.properties.direction = "right"
		keymaps.append((km, kmi))

		km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
		kmi = km.keymap_items.new(op_island_mirror.op.bl_idname, 'M', 'PRESS', alt=True)
		kmi.properties.is_stack = False
		keymaps.append((km, kmi))


def unregister():

	bpy.utils.unregister_module(__name__)

	#Unregister Settings
	del bpy.types.Scene.texToolsSettings

	#GUI Utilities
	utilities_gui.unregister()

	# Unregister icons
	global preview_icons
	bpy.utils.previews.remove(preview_icons)

	#handle the keymap
	for km, kmi in keymaps:
		km.keymap_items.remove(kmi)
	keymaps.clear()


if __name__ == "__main__":
	register()
