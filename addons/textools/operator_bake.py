import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import settings

# Get last-loaded material, such as ~.002.
def _getAppendedMaterial(material_name):
    # Get material name list.
    material_names = [m.name for m in bpy.data.materials if material_name in m.name]
    # Return last material in the sorted order.
    material_names.sort()
    return material_names[-1]

def getMaterial(materialType):
	print("Get material of type: '"+str(materialType)+"'")

	name = "textools_bake_pointiness"
	path = os.path.join(os.path.dirname(__file__), "resources/materials.blend")+"\\Material\\"

	if bpy.data.materials.get(name) is None:
		print("Image not yet loaded: "+name)
		bpy.ops.wm.append(filename=name, directory=path, link=False, autoselect=False)
	else:
		print("Image already loaded :)")

	# If material is loaded some times, select the last-loaded material.
	last_material = _getAppendedMaterial(name)
	return bpy.data.materials[last_material]

	# Apply Only one material in the material slot.
	# for m in bpy.context.object.data.materials:
	# 	bpy.ops.object.material_slot_remove()
	# bpy.context.object.data.materials.append(mat)

	#return None; #bpy.data.images[name];


class operator_bake_setup_material(bpy.types.Operator):
	bl_idname = "uv.textools_bake_setup_material"
	bl_label = "Setup Material"
	bl_description = "Setup Bake materials"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		execute_setup_material(context)
		return {'FINISHED'}

class operator_bake_render(bpy.types.Operator):
	bl_idname = "uv.textools_bake"
	bl_label = "Bake"
	bl_description = "Bake selected objects"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		execute_render(context)
		return {'FINISHED'}



def execute_setup_material(context):
	print("Executing operator_bake_render main()")
	print("Mode: "+str(context.scene.texToolsSettings.baking_mode))
	material = getMaterial("something")


def execute_render(context):
	print("Executing operator_bake_render main()")
	print("Mode: "+str(settings.bake_mode))
