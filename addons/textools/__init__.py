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
else:
    from . import operator_islandsAlignSort

# Import general modules. Important: must be placed here and not on top
import bpy
import bmesh



class SortAndPack(bpy.types.Operator):
    #Sorts shapes
    bl_idname = "uv.textools_sort_and_pack"
    bl_label = "Rotates UV islands to minimal bounds and sorts them horizontal or vertical"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')
    
    def execute(self, context):
        #main(context, self)
        return {'FINISHED'}


class TexToolsPanel(bpy.types.Panel):
#    """TexTools Panel"""
    bl_label = "TexTools"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Prototype scripts area")
        
        split = layout.split()
        col = split.column(align=True)
        #col.operator(UvSquaresByShape.bl_idname, text="To Grid By Shape", icon = "GRID")
        col.operator(SortAndPack.bl_idname, text="Sort & Pack", icon = "GRID")
        
        col.operator(operator_islandsAlignSort.IslandsAlignSort.bl_idname, text="Align & Sort", icon = "GRID")
        

        # row = layout.row()
        # row.label(text="UV Island")
        # split = layout.split()
        # col = split.column(align=True)
        # col.operator(SortAndPack.bl_idname, text="Align by Edge")
        # col.operator(SortAndPack.bl_idname, text="Align LT,RT,TP,BM")
        # col.operator(SortAndPack.bl_idname, text="Rotate 90")
        # col.operator(SortAndPack.bl_idname, text="Sort & Align")
        
        # row = layout.row()
        # row.label(text="Misc")
        # split = layout.split()
        # col = split.column(align=True)
        # col.operator(SortAndPack.bl_idname, text="Islands to Smoothing Groups")
        # col.operator(SortAndPack.bl_idname, text="Symmetry")
        # col.operator(SortAndPack.bl_idname, text="Align Island to Edge")
        
        
        
#        col.label(text="Islands to Smoothing Groups")

#        row.label(text="Prototype scripts area")
#        row = layout.row()
#        row.label(text="Align Island to Edge")
#        row = layout.row()
#        row.label(text="Align Islands LT,RT,TP,BM")
#        row = layout.row()
#        row.label(text="Rotate Islands 90")
#        row = layout.row()
#        row.label(text="Symmetry")
#        row = layout.row()
#        row.label(text="Sort")
        
        
    
def register():
    bpy.utils.register_class(TexToolsPanel)
    bpy.utils.register_class(SortAndPack)

    bpy.utils.register_class(operator_islandsAlignSort.IslandsAlignSort)

    #menu
    #bpy.types.IMAGE_MT_uvs.append(menu_func_uv_squares)
   

    #handle the keymap
#    wm = bpy.context.window_manager
    
#    km = wm.keyconfigs.addon.keymaps.new(name='UV Editor', space_type='EMPTY')
#    kmi = km.keymap_items.new(UvSquaresByShape.bl_idname, 'E', 'PRESS', alt=True)
#    addon_keymaps.append((km, kmi))
    
    

def unregister():
    bpy.utils.unregister_class(TexToolsPanel)
    bpy.utils.unregister_class(SortAndPack)

    bpy.utils.unregister_class(operator_islandsAlignSort.IslandsAlignSort)

#    bpy.types.IMAGE_MT_uvs.remove(menu_func_uv_squares)
    
    # handle the keymap
#    for km, kmi in addon_keymaps:
#        km.keymap_items.remove(kmi)
    # clear the list
#    addon_keymaps.clear()

if __name__ == "__main__":
    register()