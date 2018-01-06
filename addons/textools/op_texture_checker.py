import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi


name_material = "TT_checkerMap_material"
name_texture = "TT_checkerMap_texture"
name_node = "TT_checkerMap_node"

names_checkermap = [
	"TT_checkermap_A", 
	"TT_checkermap_B"
]

class op(bpy.types.Operator):
	"""UV Operator description"""
	bl_idname = "uv.textools_texture_checker"
	bl_label = "Checker Map"
	bl_description = "Add a checker map to the selected model and UV view"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if bpy.context.object == None:
			return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):

	if bpy.context.scene.render.engine != 'CYCLES':
		bpy.context.scene.render.engine = 'CYCLES'

	
	#Change View mode to TEXTURED
	for area in bpy.context.screen.areas: # iterate through areas in current screen
		if area.type == 'VIEW_3D':
			for space in area.spaces: # iterate through spaces in current VIEW_3D area
				if space.type == 'VIEW_3D': # check if space is a 3D view
					space.viewport_shade = 'TEXTURED' # set the viewport shading to rendered
					space.show_textured_shadeless = True




	# Setup Material
	material = None
	if name_material in bpy.data.materials:
		material = bpy.data.materials[name_material]
	else:
		material = bpy.data.materials.new(name_material)
		material.use_nodes = True

	if material == None:
		return

	# Assign material
	if len(bpy.context.object.data.materials) > 0:
		bpy.context.object.data.materials[0] = material
	else:
		bpy.context.object.data.materials.append(material)


	# Setup Node
	tree = material.node_tree
	node = None
	if name_node in tree.nodes:
		node = tree.nodes[name_node]
	else:
		node = tree.nodes.new("ShaderNodeTexImage")
	node.name = name_node
	node.select = True
	tree.nodes.active = node

	
	# Setup Image
	if node.image == None:
		node.image = get_image( names_checkermap[0] )

	else:
		print("Current image? {}".format(node.image.name))
		if node.image.name not in names_checkermap:
			node.image = get_image( names_checkermap[0] )
		else:
			# Cycle to next image
			index = (names_checkermap.index(node.image.name)+ 1) % len(names_checkermap)
			node.image = get_image( names_checkermap[index] )

	







def get_image(name):

	#Get Image
	image = None
	if bpy.data.images.get(name) is not None:
  		image = bpy.data.images[name];
	else:
		#Load image
		pathTexture = icons_dir = os.path.join(os.path.dirname(__file__), "resources/{}.png".format(name))
		image = bpy.ops.image.open(filepath=pathTexture, relative_path=False)
		bpy.data.images["{}.png".format(name)].name = name #remove extension in name
		image = bpy.data.images[name];
	
	return image












	# if name == "":
	# 	set_texture("TT_checkermap_A")

	# elif name == "TT_checkermap_A":
	# 	set_texture("TT_checkermap_B")

	# elif name == "TT_checkermap_B":
		# set_texture("TT_checkermap_A")
		# print("Destroy material and remove")









# def get_material():
	# return None


# def get_texture():
# 	print("get_texture")

# 	if len(bpy.context.object.material_slots) == 0:
# 		return ""
# 	else:
# 		for slot in bpy.context.object.material_slots:
# 			if slot.material is not None:
# 				if name_material in slot.material.name:
# 					for tex_slot in slot.material.texture_slots:
# 						if tex_slot is not None:
# 							if tex_slot.texture is not None:
# 								if tex_slot.texture.image is not None:
# 									return tex_slot.texture.image.name;
	return ""


'''
def set_texture(name):
	print("set_texture")
	# idImage = "TT_checkerMap"
	

	#Get Image
	image = None
	if bpy.data.images.get(name) is not None:
  		image = bpy.data.images[name];
	else:
		#Load image
		pathTexture = icons_dir = os.path.join(os.path.dirname(__file__), "resources/{}.png".format(name))
		image = bpy.ops.image.open(filepath=pathTexture, relative_path=False)
		bpy.data.images["{}.png".format(name)].name = name #remove extension in name
		image = bpy.data.images[name];
	

	#Assign image variable
	# 

	# bpy.context.object.active_material.use_shadeless = True
	mat = None
	if bpy.data.materials.get(name_material) is not None:
		mat = bpy.data.materials[name_material]
	else:
		mat = bpy.data.materials.new(name_material)

	mat.diffuse_color = (0.5,0.5,0.5)
	mat.diffuse_shader = 'LAMBERT' 
	mat.diffuse_intensity = 1.0 
	mat.specular_color = (1,1,1)
	mat.specular_shader = 'COOKTORR'
	mat.specular_intensity = 0.5
	# mat.alpha = alpha
	mat.ambient = 1
	mat.use_shadeless = True


	imageTexture = None
	if bpy.data.textures.get(name_texture) is not None:
		imageTexture = bpy.data.textures.get(name_texture)
	else:
		imageTexture = bpy.data.textures.new(name_texture, type = 'IMAGE')
	imageTexture.image = image

	# Add texture slot for color texture
	mtex = None
	if len(mat.texture_slots) == 0 or mat.texture_slots[0] is None:
		mtex = mat.texture_slots.add()
	else:
		mtex = mat.texture_slots[0]

	mtex.texture = imageTexture
	mtex.texture_coords = 'UV'
	mtex.use_map_color_diffuse = True 
	mtex.use_map_color_emission = True 
	mtex.emission_color_factor = 0.5
	mtex.use_map_density = True 
	mtex.mapping = 'FLAT' 


	#Assign image to UV faces
	for obj in bpy.context.selected_objects:
		#Only Assign if already UV maps
		if obj.data.uv_layers:
			for uv_face in obj.data.uv_textures.active.data:
				uv_face.image = image

		obj.active_material = mat

	

'''

