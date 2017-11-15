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
	"location": "UV Image Editor > UVs > UVs to grid of squares",
	"warning": "",
	"wiki_url": "http://renderhjs.net/textools/"
}

# Import local modules
# More info: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Multi-File_packages
if "bpy" in locals():
	import imp
	imp.reload(operator_islandsAlignSort)
	imp.reload(operator_checkerMap)
	imp.reload(operator_islandsPack)
	imp.reload(operator_align)
	imp.reload(operator_reloadTextures)
	imp.reload(operator_bake)

else:
	from . import operator_islandsAlignSort
	from . import operator_checkerMap
	from . import operator_islandsPack
	from . import operator_align
	from . import operator_reloadTextures
	from . import operator_bake

# Import general modules. Important: must be placed here and not on top
import bpy
import os
import math
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
		size=2, 
		default = (1024,1024),
		subtype = "XYZ"
	)
	#Padding
	padding = IntProperty(
		name = "Padding",
		description="Texture & UV height in pixels",
		default = 4,
		min = 1,
		max = 16384
	)
	#Baking mode
	#Enum help: 	https://docs.blender.org/api/blender_python_api_2_77_0/bpy.props.html
	baking_modes = [
		("mesh.primitive_plane_add", "Plane", '', 'MESH_PLANE', 0),
		("mesh.primitive_cube_add", "Cube", '', 'MESH_CUBE', 1)
	]
	baking_mode = bpy.props.EnumProperty(
		items=baking_modes,
		description="Baking mode",
		default="mesh.primitive_plane_add",
		# update=execute_operator
	)


def getIcon(name):
	return preview_icons[name].icon_id

class TexToolsPanel(bpy.types.Panel):
#    """TexTools Panel"""
	bl_label = "TexTools"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	
	def draw(self, context):
		layout = self.layout
		
		# display the properties
		layout.prop(context.scene.texToolsSettings, "size", text="Size")
		layout.prop(context.scene.texToolsSettings, "padding", text="Padding")
		
        # layout.prop(mytool, "my_int", text="Integer Property")
        # layout.prop(mytool, "my_float", text="Float Property")


		row = layout.row()
		row.label(text="UV Islands")
		
		col = layout.split().column(align=True)
		row = col.row(align=True)
		row.operator("transform.rotate", text="-90°", icon_value = getIcon("turnLeft")).value = -math.pi / 2
		row.operator("transform.rotate", text="+90°", icon_value = getIcon("turnRight")).value = math.pi / 2

		row = col.row(align=True)
		row.operator(operator_align.operator_align.bl_idname, text=" ", icon_value = getIcon("alignBottom"))
		row.operator(operator_align.operator_align.bl_idname, text=" ", icon_value = getIcon("alignLeft"))
		row.operator(operator_align.operator_align.bl_idname, text=" ", icon_value = getIcon("alignRight"))
		row.operator(operator_align.operator_align.bl_idname, text=" ", icon_value = getIcon("alignTop"))
		
		row = col.row(align=True)
		row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, icon_value = getIcon("islandsAlignSort")).is_vertical = True;
		row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, icon_value = getIcon("islandsAlignSort")).is_vertical = False;
		
		# print("X: "+str(x.name))


		# row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, isVertical = True, icon_value = getIcon("islandsAlignSort"));
		# row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, icon_value = getIcon("islandsAlignSort")).isVertical = False;


		#row.operator(bpy.ops.transform.rotate.bl_idname, text="Right", icon_value = getIcon("turnRight"))
		

		#bpy.ops.transform.rotate(value=1.5708, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)


		row = layout.row()
		row.label(text="Textures")
		col = layout.split().column(align=True)
		col.operator(operator_checkerMap.operator_checkerMap.bl_idname, icon_value = getIcon("checkerMap"))
		col.operator(operator_reloadTextures.operator_reloadTextures.bl_idname, text="Reload", icon_value = getIcon("reloadTextures"))


		row = layout.row()
		row.label(text="Baking")

		row = layout.row()
		row.prop(context.scene.texToolsSettings, "baking_mode", text="Mode")

		col = layout.split().column(align=True)
		row = layout.row()
		row.operator(operator_bake.operator_bake.bl_idname, text = "Bake");
		
		row = col.row(align=True)
		row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, text = "Setup Material");
		row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, text = "Explode");

		


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
	
	# Register global Icons
	global preview_icons
	preview_icons = bpy.utils.previews.new()
	registerIcon("islandsAlignSort.png")
	registerIcon("checkerMap.png")
	registerIcon("turnLeft.png")
	registerIcon("turnRight.png")
	registerIcon("reloadTextures.png")
	registerIcon("alignBottom.png")
	registerIcon("alignLeft.png")
	registerIcon("alignRight.png")
	registerIcon("alignTop.png")
	
	#Key Maps
	# wm = bpy.context.window_manager
	# km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
	# kmi = km.keymap_items.new(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, 'SPACE', 'PRESS', ctrl=True, shift=True)
	# keymaps.append((km, kmi))
	
	#bpy.utils.register_module(__name__)
	#handle the keymap
#    wm = bpy.context.window_manager
	
#    km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#    kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#    addon_keymaps.append((km, kmi))
	
	

def unregister():

	bpy.utils.unregister_module(__name__)

	#Unregister Settings
	del bpy.types.Scene.texToolsSettings

	# Unregister icons
	global preview_icons
	bpy.utils.previews.remove(preview_icons)

	#handle the keymap
	for km, kmi in keymaps:
		km.keymap_items.remove(kmi)
	keymaps.clear()

#    bpy.types.IMAGE_MT_uvs.remove(menu_func_uv_squares)
	
	# handle the keymap
#    for km, kmi in addon_keymaps:
#        km.keymap_items.remove(kmi)
	# clear the list
#    addon_keymaps.clear()

if __name__ == "__main__":
	register()