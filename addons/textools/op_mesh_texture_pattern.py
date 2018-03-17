import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi
import math

from . import utilities_mesh_texture




class op(bpy.types.Operator):
	bl_idname = "uv.textools_mesh_texture_pattern"
	bl_label = "Create Pattern"
	bl_description = "Create mesh pattern"
	bl_options = {'REGISTER', 'UNDO'}

	mode = bpy.props.EnumProperty(items= 
		[('hexagon', 'Hexagons', ''),
		('triangle', 'Triangles', ''), 
		('diamond', 'Diamonds', ''),
		('rectangle', 'Rectangles', ''),
		('stripe', 'Stripes', ''),
		('brick', 'Bricks', '')], 
		name = "Mode", 
		default = 'triangle'
	)
	size = bpy.props.IntProperty(
		name = "Size",
		description = "Size X and Y of the repetition",
		default = 4,
		min = 1,
		max = 128
	)

	@classmethod
	def poll(cls, context):
		return True

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "mode")
		layout.prop(self, "size")

	def execute(self, context):
		create_pattern(self, self.mode, self.size)
		return {'FINISHED'}



def create_pattern(self, mode, size):
	
	print("Create pattern {}".format(mode))
	

	if mode == 'hexagon':
		bpy.ops.mesh.primitive_circle_add(vertices=6, radius=1, fill_type='NGON')
		bpy.context.object.show_wire = True

		bpy.ops.object.editmode_toggle()
		bpy.ops.transform.rotate(GetContextView3D(), value=math.pi*0.5,  axis=(0, 0, 1))
		bpy.ops.object.editmode_toggle()

		AddArray("Array0", 0.75,-0.5,2)
		AddArray("Array1", 0,-0.66666666666,size)
		AddArray("Array2", 1 - (0.5/3.5),0,size*0.66)

	elif mode == 'triangle':
		bpy.ops.mesh.primitive_circle_add(vertices=3, radius=1, fill_type='NGON')
		bpy.context.object.show_wire = True

		bpy.ops.object.editmode_toggle()
		# bpy.ops.transform.rotate(GetContextView3D(), value=math.pi*0.5,  axis=(0, 0, 1))
		bpy.ops.transform.translate(GetContextView3D(), value=(0, 0.5, 0), constraint_axis=(False, True, False))
		bpy.ops.object.editmode_toggle()
		
		bpy.ops.object.modifier_add(type='MIRROR')
		bpy.context.object.modifiers["Mirror"].use_y = True
		bpy.context.object.modifiers["Mirror"].use_x = False


def AddArray(name, offset_x, offset_y, count):
	modifier = bpy.context.object.modifiers.new(name=name, type='ARRAY')
	modifier.relative_offset_displace[0] = offset_x
	modifier.relative_offset_displace[1] = offset_y
	modifier.count = count
	modifier.show_expanded = False
	return modifier

def GetContextView3D():
	#=== Iterates through the blender GUI's windows, screens, areas, regions to find the View3D space and its associated window.  Populate an 'oContextOverride context' that can be used with bpy.ops that require to be used from within a View3D (like most addon code that runs of View3D panels)
	# Tip: If your operator fails the log will show an "PyContext: 'xyz' not found".  To fix stuff 'xyz' into the override context and try again!
	for oWindow in bpy.context.window_manager.windows:          ###IMPROVE: Find way to avoid doing four levels of traversals at every request!!
		oScreen = oWindow.screen
		for oArea in oScreen.areas:
			if oArea.type == 'VIEW_3D':                         ###LEARN: Frequently, bpy.ops operators are called from View3d's toolbox or property panel.  By finding that window/screen/area we can fool operators in thinking they were called from the View3D!
				for oRegion in oArea.regions:
					if oRegion.type == 'WINDOW':                ###LEARN: View3D has several 'windows' like 'HEADER' and 'WINDOW'.  Most bpy.ops require 'WINDOW'
						#=== Now that we've (finally!) found the damn View3D stuff all that into a dictionary bpy.ops operators can accept to specify their context.  I stuffed extra info in there like selected objects, active objects, etc as most operators require them.  (If anything is missing operator will fail and log a 'PyContext: error on the log with what is missing in context override) ===
						oContextOverride = {'window': oWindow, 'screen': oScreen, 'area': oArea, 'region': oRegion, 'scene': bpy.context.scene, 'edit_object': bpy.context.edit_object, 'active_object': bpy.context.active_object, 'selected_objects': bpy.context.selected_objects}   # Stuff the override context with very common requests by operators.  MORE COULD BE NEEDED!
						print("-AssembleOverrideContextForView3dOps() created override context: ", oContextOverride)
						return oContextOverride
	raise Exception("ERROR: AssembleOverrideContextForView3dOps() could not find a VIEW_3D with WINDOW region to create override context to enable View3D operators.  Operator cannot function.")