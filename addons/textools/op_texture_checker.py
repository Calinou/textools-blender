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