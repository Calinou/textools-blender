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
if "bpy" in locals():
	import imp
	imp.reload(operator_islandsAlignSort)
	imp.reload(operator_checkerMap)
	imp.reload(operator_islandsPack)
else:
	from . import operator_islandsAlignSort
	from . import operator_checkerMap
	from . import operator_islandsPack
	

# Import general modules. Important: must be placed here and not on top
import bpy
import os
import bpy.utils.previews

def getIcon(name):
	return preview_icons[name].icon_id

class TexToolsPanel(bpy.types.Panel):
#    """TexTools Panel"""
	bl_label = "TexTools"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'TOOLS'
	
	def draw(self, context):
		layout = self.layout
		
		row = layout.row()
		row.label(text="UV Islands")
		
		col = layout.split().column(align=True)
		col.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, icon_value = getIcon("islandsAlignSort"))
	#	col.operator(operator_islandsPack.operator_islandsPack.bl_idname, icon_value = getIcon("islandsAlignSort"))
		
		# col.operator(operator_checkerMap.CheckerMap.bl_idname, icon_value = getIcon("checkerMap"))
		
		row = layout.row()
		row.label(text="Layout")
		col = layout.split().column(align=True)
		row = col.row(align=True)
		row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, text="-90", icon_value = getIcon("turnLeft"))
		row.operator(operator_islandsAlignSort.operator_islandsAlignSort.bl_idname, text="+90", icon_value = getIcon("turnRight"))

		row = layout.row()
		row.label(text="Texels")
		col = layout.split().column(align=True)
		col.operator(operator_checkerMap.operator_checkerMap.bl_idname, icon_value = getIcon("checkerMap"))


def registerIcon(fileName):
	# global custom_icons
	name = fileName.split('.')[0]   # Don't include file extension
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")
	preview_icons.load(name, os.path.join(icons_dir, fileName), 'IMAGE')
	
def register():
	# Register global Icons
	global preview_icons
	preview_icons = bpy.utils.previews.new()
	registerIcon("islandsAlignSort.png")
	registerIcon("checkerMap.png")
	registerIcon("turnLeft.png")
	registerIcon("turnRight.png")
	
	# Register Operators
	bpy.utils.register_class(TexToolsPanel)
	bpy.utils.register_class(operator_islandsAlignSort.operator_islandsAlignSort)
	bpy.utils.register_class(operator_checkerMap.operator_checkerMap)
	bpy.utils.register_class(operator_islandsPack.operator_islandsPack)

	#bpy.utils.register_module(__name__)
	#handle the keymap
#    wm = bpy.context.window_manager
	
#    km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#    kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#    addon_keymaps.append((km, kmi))
	
	

def unregister():
	# Unregister icons
	global preview_icons
	bpy.utils.previews.remove(preview_icons)

	#Unregister Operators
	bpy.utils.unregister_class(TexToolsPanel)
	bpy.utils.unregister_class(operator_islandsAlignSort.operator_islandsAlignSort)
	bpy.utils.unregister_class(operator_checkerMap.operator_checkerMap)
	bpy.utils.unregister_class(operator_islandsPack.operator_islandsPack)


	bpy.utils.unregister_module(__name__)



#    bpy.types.IMAGE_MT_uvs.remove(menu_func_uv_squares)
	
	# handle the keymap
#    for km, kmi in addon_keymaps:
#        km.keymap_items.remove(kmi)
	# clear the list
#    addon_keymaps.clear()

if __name__ == "__main__":
	register()