import bpy
import os
import bmesh
from mathutils import Vector
from collections import defaultdict
from math import pi


class operator_bake_setup_material(bpy.types.Operator):
	bl_idname = "uv.textools_bake_setup_material"
	bl_label = "Setup Material"
	bl_description = "Setup Bake materials"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		return {'FINISHED'}

class operator_bake_render(bpy.types.Operator):
	bl_idname = "uv.textools_bake"
	bl_label = "Bake"
	bl_description = "Bake selected objects"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing operator_bake_render main()")
	print("Mode: "+str(context.scene.texToolsSettings.baking_mode))
