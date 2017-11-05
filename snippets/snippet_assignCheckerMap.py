import bpy

# blank image
#image = bpy.data.images.new("uvChecker", width=512, height=512)

bpy.ops.image.open(filepath="//..\\Documents\\GIT\\TexToolsBlender\\addons\\textools\\resources\\checkerMap.jpg", directory="D:\\Documents\\GIT\\TexToolsBlender\\addons\\textools\\resources\\", files=[{"name":"checkerMap.jpg", "name":"checkerMap.jpg"}], relative_path=True, show_multiview=False)



for area in bpy.context.screen.areas:
    print("..>>"+ area.type)
    for space in area.spaces:
            if space.type == 'VIEW_3D':
                spaceviewpoert_shade = 'TEXTURED'

#Create 
#bpy.data.images["uvChecker"].name = "uvChecker"

#Set 3D viewport shading to 'TEXTURED'
#bpy.context.space_data.viewport_shade = 'TEXTURED'

#print __file__