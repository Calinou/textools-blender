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
	"description": "UV and texture Tools for Blender. Based on ideas of the original TexTools for 3dsMax.",
	"author": "renderhjs",
	"version": (1, 0, 0),
	"blender": (2, 71, 0),
	"category": "UV",
	"location": "UV Image Editor > UVs > Misc : TexTools panel",
	"warning": "",
	"wiki_url": "http://renderhjs.net/textools/"
}

# Import local modules
# More info: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
	import imp
	imp.reload(utilities_gui)
	imp.reload(settings)
	
	imp.reload(op_islands_align_sort)
	imp.reload(op_checkerMap)
	imp.reload(op_align)
	imp.reload(op_textures_reload)
	imp.reload(op_bake)
	imp.reload(op_swap_uv_xyz)
	imp.reload(op_island_align_edge)
	imp.reload(op_select_islands_identical)
	imp.reload(op_islands_select_overlap)
	imp.reload(op_islands_select_outline)
	imp.reload(op_island_symmetry)
	imp.reload(op_island_relax_straighten_edges)
	imp.reload(op_setup_split_uv)
	imp.reload(op_faces_iron)
	
	
	
else:
	from . import utilities_gui
	from . import settings

	from . import op_islands_align_sort
	from . import op_checkerMap
	from . import op_align
	from . import op_textures_reload
	from . import op_bake
	from . import op_swap_uv_xyz
	from . import op_island_align_edge
	from . import op_select_islands_identical
	from . import op_islands_select_overlap
	from . import op_islands_select_outline
	from . import op_island_symmetry
	from . import op_island_relax_straighten_edges
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



#Vector Int Property: https://blender.stackexchange.com/questions/22855/how-to-customise-add-properties-to-existing-blender-data
# Store in Scene for UV: https://blender.stackexchange.com/questions/35007/how-can-i-add-a-checkbox-in-the-tools-ui

class TexToolsSettings(bpy.types.PropertyGroup):
	#Width and Height
	size = bpy.props.IntVectorProperty(
		name = "Size",
		size=2, 
		description="Texture & UV size in pixels",
		default = (1024,1024),
		subtype = "XYZ"
	)

	

	#Padding
	padding = IntProperty(
		name = "Padding",
		description="padding size in pixels",
		default = 4,
		min = 1,
		max = 16384
	)
	
	baking_do_save = bpy.props.BoolProperty(
		name="Save",
    	description="Save the baked texture?",
    	default = False)

	id_palette = None;#bpy.types.UILayout.template_palette()



def getIcon(name):
	return preview_icons[name].icon_id

class TexToolsPanel(bpy.types.Panel):
#    """TexTools Panel"""
	bl_label = "TexTools"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	bl_category = "TexTools"
	
	def draw(self, context):
		layout = self.layout
		

		layout.operator("wm.console_toggle", text="Debug Console", icon="CONSOLE")


		#---------- Settings ------------
		row = layout.row()
		# box = row.box()
		# box.label(text="Settings")

		col = row.column(align=True)
		# aligned = col.row(align=True)
		col.prop(context.scene.texToolsSettings, "size", text="")
		col.prop(context.scene.texToolsSettings, "padding", text="Padding")


		#---------- Transform ------------
		layout.separator()
		layout.operator(op_setup_split_uv.op.bl_idname, text="Split", icon_value = getIcon("setup_split_uv"))
		layout.separator()


		#---------- Layout ------------
		layout.label(text="Layout")

		box = layout.box()
		col = box.column(align=True)
		row = col.row(align=True)
		row.operator(op_island_align_edge.op.bl_idname, text="Align Edge", icon_value = getIcon("island_align_edge"))
		col.operator(op_island_relax_straighten_edges.op.bl_idname, text="Straight & Relax", icon_value = getIcon("island_relax_straighten_edges"))

		row = col.row(align=True)
		row.operator("transform.rotate", text="-90°", icon_value = getIcon("turnLeft")).value = -math.pi / 2
		row.operator("transform.rotate", text="+90°", icon_value = getIcon("turnRight")).value = math.pi / 2
		
		
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
		aligned.operator(op_islands_align_sort.op.bl_idname, text="Sort H", icon_value = getIcon("islands_align_sort_h")).is_vertical = False;
		aligned.operator(op_islands_align_sort.op.bl_idname, text="Sort V", icon_value = getIcon("islands_align_sort_v")).is_vertical = True;
		
		aligned = box.row(align=True)
		col = aligned.column(align=True)
		row = col.row(align=True)
		row.operator(op_island_symmetry.op.bl_idname, text="Mirror", icon_value = getIcon("mirror")).is_stack = False;
		row.operator(op_island_symmetry.op.bl_idname, text="M. Stack", icon_value = getIcon("mirror")).is_stack = True;
		
		col.operator(op_faces_iron.op.bl_idname, text="Iron", icon_value = getIcon("faces_iron"))
		

		#---------- Selection ------------
		layout.label(text="Select")
		row = layout.row()
		box = row.box()
		col = box.column(align=True)
		row = col.row(align=True)
		row.operator(op_select_islands_identical.op.bl_idname, text="Similar", icon_value = getIcon("islands_select_identical"))
		row.operator(op_islands_select_overlap.op.bl_idname, text="Overlap", icon_value = getIcon("islands_select_overlapping"))
		# aligned = box.row(align=True)
		col.operator(op_islands_select_outline.op.bl_idname, text="UV Outlines")
		

		#---------- Textures ------------
		layout.label(text="Textures")
		row = layout.row()
		box = row.box()
		aligned = box.column(align=True)
		aligned.operator(op_checkerMap.op.bl_idname, text ="Checker", icon_value = getIcon("checkerMap"))
		aligned.operator(op_textures_reload.op.bl_idname, text="Reload", icon_value = getIcon("textures_reload"))


		layout.operator(op_swap_uv_xyz.op.bl_idname, text="Swap UV/XYZ", icon_value = getIcon("swap_uv_xyz"))
		

		layout.separator()

		#---------- Baking ------------
		layout.label(text="Baking")
		row = layout.row()
		box = row.box()

		aligned = box.row()
		#Alternative VectorBool? https://blender.stackexchange.com/questions/14312/how-can-i-present-an-array-of-booleans-in-a-panel
		
		aligned.template_icon_view(context.scene, "my_thumbnails")
		settings.bake_mode = str(bpy.context.scene.my_thumbnails).replace(".png","")

		# Just a way to access which one is selected
		aligned = box.row()
		aligned.label(text="Mode: " +settings.bake_mode )

	
		#Thumbnail grid view: https://blender.stackexchange.com/questions/47504/script-custom-previews-in-a-menu
		
		aligned = box.row(align=True)
		aligned.operator(op_bake.op_setup_material.bl_idname, text = "Set Material");
		aligned.operator(op_bake.op_setup_material.bl_idname, text = "Set Model");

		aligned = box.row(align=True)
		aligned.operator(op_bake.op_bake.bl_idname, text = "Bake");
		aligned.prop(context.scene.texToolsSettings, "baking_do_save")		
		layout.separator()

		#---------- ID Colors ------------
		#Example custom UI list: https://blender.stackexchange.com/questions/47840/is-bpy-props-able-to-create-a-list-of-lists
		#Example assign vertex colors: https://blender.stackexchange.com/questions/30841/how-to-view-vertex-colors
		#Color Palette: https://blender.stackexchange.com/questions/73122/how-do-i-create-palette-ui-object

		row = layout.row()
		box = row.box()
		box.label(text="ID Colors")
		box.operator(bpy.ops.paint.sample_color.idname())
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
	bpy.types.Scene.texToolsSettings = PointerProperty(type=TexToolsSettings)
	
	#GUI Utilities
	utilities_gui.register()

	# Register global Icons
	global preview_icons
	preview_icons = bpy.utils.previews.new()
	registerIcon("islands_align_sort_h.png")
	registerIcon("islands_align_sort_v.png")
	registerIcon("checkerMap.png")
	registerIcon("swap_uv_xyz.png")
	registerIcon("turnLeft.png")
	registerIcon("turnRight.png")
	registerIcon("textures_reload.png")
	registerIcon("island_align_edge.png")
	registerIcon("island_relax_straighten_edges.png")
	registerIcon("alignBottom.png")
	registerIcon("alignLeft.png")
	registerIcon("alignRight.png")
	registerIcon("alignTop.png")
	registerIcon("mirror.png")
	registerIcon("setup_split_uv.png")
	registerIcon("faces_iron.png")
	registerIcon("islands_select_identical.png")
	registerIcon("islands_select_overlapping.png")
	registerIcon("explode.png")

	#Key Maps
	wm = bpy.context.window_manager

	km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	kmi = km.keymap_items.new(op_islands_align_sort.op.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
	keymaps.append((km, kmi))

	# https://github.com/RayMairlot/UV-Rotate-Shortcuts/blob/master/UV%20Rotate.py
	# km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
 #    kmi = km.keymap_items.new("uv.rotate_selection_left", 'R', 'PRESS', ctrl=True, shift=True)
 #    keymaps.append((km, kmi))

 #    km = wm.keyconfigs.addon.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
 #    kmi = km.keymap_items.new("uv.rotate_selection_right", 'R', 'PRESS', shift=True)
 #    keymaps.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
			# kmi = km.keymap_items.new(op_align.op.bl_idname, 'UP_ARROW', 'PRESS', alt=True, ctrl=True, shift=True)
			# kmi.properties.direction = "top"
			# keymaps.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
			# kmi = km.keymap_items.new(op_align.op.bl_idname, 'DOWN_ARROW', 'PRESS', alt=True, ctrl=True, shift=True)
			# kmi.properties.direction = "bottom"
			# keymaps.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
			# kmi = km.keymap_items.new(op_align.op.bl_idname, 'LEFT_ARROW', 'PRESS', alt=True, ctrl=True, shift=True)
			# kmi.properties.direction = "left"
			# keymaps.append((km, kmi))

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
	kmi = km.keymap_items.new(op_island_symmetry.op.bl_idname, 'M', 'PRESS', alt=True)
	kmi.properties.is_stack = False
	keymaps.append((km, kmi))

	
	# wm = bpy.context.window_manager
	# if wm.keyconfigs.addon is not None:

	# print("Register keyboard bindings")

	# km = wm.keyconfigs.addon.keymaps.new(name='Align Up', space_type='IMAGE_EDITOR')
	# kmi = km.keymap_items.new(op_align.op.bl_idname, 'UP_ARROW', 'PRESS', shift=True)
	# kmi = km.keymap_items.new(op_align.op.bl_idname, 'M', 'PRESS', alt=True)
	# kmi.properties.direction = "up"
	# keymaps.append((km, kmi))
    
	# km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='IMAGE_EDITOR')
	# kmi = km.keymap_items.new(op_align.op.bl_idname, 'V', 'PRESS', ctrl=True, shift=True)
	# kmi.properties.direction = "up"
	# keymaps.append((km, kmi))

	# print("Keymaps: "+str(kmi))


	    # km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	    # kmi = km.keymap_items.new(RipFaces.bl_idname, 'V', 'PRESS', alt=True)
	    # keymaps.append((km, kmi))
	    
	    # km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	    # kmi = km.keymap_items.new(JoinFaces.bl_idname, 'V', 'PRESS', alt=True, shift=True)
	    # keymaps.append((km, kmi))





	# km = kc.keymaps.new('Frames', space_type='EMPTY', region_type='WINDOW', modal=False)
	# kmi = km.keymap_items.new('screen.frame_offset', 'UP_ARROW', 'PRESS', shift=True)
	# kmi.properties.delta = 10

	#bpy.utils.register_module(__name__)
	#handle the keymap
#    wm = bpy.context.window_manager
	
#    km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#    kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#    keymaps.append((km, kmi))
	
	

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
