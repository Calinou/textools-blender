import bpy

# blank image
#image = bpy.data.images.new("uvChecker", width=512, height=512)

#bpy.ops.image.open(filepath="//..\\Documents\\GIT\\TexToolsBlender\\addons\\textools\\resources\\checkerMap.jpg", directory="D:\\Documents\\GIT\\TexToolsBlender\\addons\\textools\\resources\\", files=[{"name":"checkerMap.jpg", "name":"checkerMap.jpg"}], relative_path=True, show_multiview=False)

idImage = "TT_checkerMap"

if bpy.data.images.get(idImage) is not None:
    print("Image found")

#Create 
#bpy.data.images["uvChecker"].name = "uvChecker"

#Set 3D viewport shading to 'TEXTURED'
#bpy.context.space_data.viewport_shade = 'TEXTURED'

#print __file__