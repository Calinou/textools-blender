import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_uv

class operator_island_align_edge(bpy.types.Operator):
	bl_idname = "uv.textools_island_align_edge"
	bl_label = "Align Island by Edge"
	bl_description = "Align the island by selected edge"
   
	@classmethod
	def poll(cls, context):

		return True


	def execute(self, context):

		main(context)
		return {'FINISHED'}


def main(context):
	print("Executing operator_island_align_edge")
   	