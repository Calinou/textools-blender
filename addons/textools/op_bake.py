import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings
from . import utilities_bake

# Get last-loaded material, such as ~.002.
# def _getAppendedMaterial(material_name):
#     # Get material name list.
#     material_names = [m.name for m in bpy.data.materials if material_name in m.name]
#     # Return last material in the sorted order.
#     material_names.sort()
#     return material_names[-1]

def getMaterial(name):
	path = os.path.join(os.path.dirname(__file__), "resources/materials.blend")+"\\Material\\"

	if bpy.data.materials.get(name) is None:
		print("Material not yet loaded: "+name)
		bpy.ops.wm.append(filename=name, directory=path, link=False, autoselect=False)

	return bpy.data.materials.get(name)


class op_setup_material(bpy.types.Operator):
	bl_idname = "uv.textools_bake_setup_material"
	bl_label = "Setup Material"
	bl_description = "Setup Bake materials"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		execute_setup_material(context)
		return {'FINISHED'}


def execute_setup_material(context):
	print("Executing operator_bake_render main()")
	print("Mode: "+str(context.scene.texToolsSettings.baking_mode))
	material = getMaterial("something")


class op_bake(bpy.types.Operator):
	bl_idname = "uv.textools_bake"
	bl_label = "Bake"
	bl_description = "Bake selected objects"

	@classmethod
	def poll(cls, context):
		if len(bpy.context.selected_objects) == 0:
			return False

		return True

	def execute(self, context):
		execute_render(self, context, settings.bake_mode)
		return {'FINISHED'}




def setup_material(obj, mode):

	if mode == 'bake_normal' or mode == 'bake_ao':
		# No material setup requires
		return

	if mode == 'bake_worn' or mode == 'bake_cavity' or mode == 'bake_dust':
		# Setup vertex dirt colors
		bpy.ops.paint.vertex_color_dirt()
	
	# Assign material
	material = getMaterial(mode)
	if len(obj.data.materials) == 0:
		obj.data.materials.append(material)
	else:
		obj.data.materials[0] = material


def execute_render(self, context, mode):

	if bpy.context.scene.render.engine != 'CYCLES':
		bpy.context.scene.render.engine = 'CYCLES'

	if bpy.context.object.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')

	sets = utilities_bake.get_bake_pairs()
	bpy.ops.object.select_all(action='DESELECT')
	
	print("________________________________\nBake {}x '{}'".format(len(sets), mode))


	for set in sets:
		# Requires 1+ low poly objects
		if len(set.objects_low) == 0:
			self.report({'ERROR_INVALID_INPUT'}, "No low poly object selected for {}".format(set.name) )
			return

		# Check for UV maps
		for obj in set.objects_low:
			if len(obj.data.uv_layers) == 0:
				print("NO UV MAP FOUND FOR {} ".format(obj.name))
				return



		# Assign materials
		if len(set.objects_high) == 0:
			# Assign material to lowpoly
			for obj in set.objects_low:
				setup_material(obj, mode)
		else:
			# Assign material to highpoly
			for obj in set.objects_high:
				setup_material(obj, mode)

		# BRM BakeUI: https://github.com/leukbaars/BRM-BakeUI/blob/master/BRM_BakeUI.py

		#create bake image and material
		image = bpy.data.images.new("BakeImage", width=256, height=256) #context.scene.bakeWidth

		# Setup active node for baking
		tree = set.objects_low[0].data.materials[0].node_tree
		node = tree.nodes.new("ShaderNodeTexImage")
		node.select = True
		node.image = image
		tree.nodes.active = node

		
		print("Bake {}".format(set.name))