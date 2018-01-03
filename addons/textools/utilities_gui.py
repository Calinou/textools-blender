import bpy
from bpy.types import Panel, EnumProperty, WindowManager
import bpy.utils.previews

import os

preview_collections = {}

def get_padding():
    size_min = min(bpy.context.scene.texToolsSettings.size[0],bpy.context.scene.texToolsSettings.size[1])
    return bpy.context.scene.texToolsSettings.padding / size_min


def generate_previews():
    # We are accessing all of the information that we generated in the register function below
    pcoll = preview_collections["thumbnail_previews"]
    image_location = pcoll.images_location
    VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg')
    
    enum_items = []
    
    # Generate the thumbnails
    for i, image in enumerate(os.listdir(image_location)):
        if image.endswith(VALID_EXTENSIONS):
            filepath = os.path.join(image_location, image)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((image, image, "", thumb.icon_id, i))
            
    return enum_items
    
def register():
    from bpy.types import Scene
    from bpy.props import StringProperty, EnumProperty
    
    # Create a new preview collection (only upon register)
    pcoll = bpy.utils.previews.new()
    
    # This line needs to be uncommented if you install as an addon
    pcoll.images_location = os.path.join(os.path.dirname(__file__), "resources/bake_modes")
    
    # This line is for running as a script. Make sure images are in a folder called images in the same
    # location as the Blender file. Comment out if you install as an addon
    #pcoll.images_location = bpy.path.abspath('//images')
    
    # Enable access to our preview collection outside of this function
    preview_collections["thumbnail_previews"] = pcoll
    
    # This is an EnumProperty to hold all of the images
    # You really can save it anywhere in bpy.types.*  Just make sure the location makes sense
    bpy.types.Scene.TT_bake_mode = EnumProperty(
        items=generate_previews(),
        )
    
def unregister():
    from bpy.types import WindowManager
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    del bpy.types.Scene.TT_bake_mode
   
if __name__ == "__main__":
    register()