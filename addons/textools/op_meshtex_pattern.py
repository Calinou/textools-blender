import bpy
import bmesh
import operator

from mathutils import Vector
from collections import defaultdict
from math import pi
import math

from . import utilities_meshtex
from . import utilities_ui


class op(bpy.types.Operator):
	bl_idname = "uv.textools_meshtex_pattern"
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
		default = 'brick'
	)

	size = bpy.props.IntProperty(
		name = "Size",
		description = "Size X and Y of the repetition",
		default = 4,
		min = 1,
		max = 128
	)

	scale = bpy.props.FloatProperty(
		name = "Scale",
		description = "Scale of the mesh pattern",
		default = 1
	)

	@classmethod
	def poll(cls, context):
		if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
			return False

		return True

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "mode")
		layout.prop(self, "size")
		layout.prop(self, "scale")

	def execute(self, context):
		create_pattern(self, self.mode, self.size, self.scale)
		return {'FINISHED'}



def create_pattern(self, mode, size, scale):
	
	print("Create pattern {}".format(mode))
	
	# bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


	contextView3D = utilities_ui.GetContextView3D()
	if not contextView3D:
		self.report({'ERROR_INVALID_INPUT'}, "This tool requires an available View3D view.")
		return


	if mode == 'hexagon':
		bpy.ops.mesh.primitive_circle_add(vertices=6, radius=scale, fill_type='NGON')

		bpy.ops.object.editmode_toggle()
		bpy.ops.transform.rotate(contextView3D, value=math.pi*0.5,  axis=(0, 0, 1))
		bpy.ops.object.editmode_toggle()

		AddArray("Array0", 0.75,-0.5,2)
		AddArray("Array1", 0,-0.66666666666,size)
		AddArray("Array2", 1 - (0.5/3.5),0,size*0.66)

	elif mode == 'triangle':
		bpy.ops.mesh.primitive_circle_add(vertices=3, radius=scale, fill_type='NGON')

		bpy.ops.object.editmode_toggle()
		bpy.ops.transform.translate(contextView3D, value=(0, scale*0.5, 0), constraint_axis=(False, True, False))
		bpy.ops.object.editmode_toggle()
		
		modifier = bpy.context.object.modifiers.new(name="Mirror", type='MIRROR')
		modifier.use_y = True
		modifier.use_x = False
		modifier.show_expanded = False
		AddArray("Array0", 0.5,-0.5,2)
		AddArray("Array1", 1-1/3.0,0,size)
		AddArray("Array1", 0,-(1-1/3.0),size*0.66)

	elif mode == 'rectangle':
		bpy.ops.mesh.primitive_plane_add(radius=scale)
		AddArray("Array0", 1,0,size)
		AddArray("Array1", 0,-1,size)

	elif mode == 'diamond':
		bpy.ops.mesh.primitive_plane_add(radius=scale)

		bpy.ops.object.editmode_toggle()
		bpy.ops.transform.rotate(contextView3D, value=math.pi*0.25,  axis=(0, 0, 1))
		bpy.ops.object.editmode_toggle()

		AddArray("Array0", 0.5,-0.5,2)
		AddArray("Array1", 1-1/3,0,size)
		AddArray("Array2", 0,-(1-1/3),size)

	elif mode == 'brick':
		bpy.ops.mesh.primitive_plane_add(radius=scale)

		bpy.ops.object.editmode_toggle()
		bpy.ops.transform.resize(contextView3D, value=(1, 0.5, 1), constraint_axis=(True, True, False), constraint_orientation='GLOBAL')
		bpy.ops.object.editmode_toggle()

		AddArray("Array0", 0.5,-1,2)
		AddArray("Array1", 1-1/3,0,size)
		AddArray("Array2", 0,-1,size)

	elif mode == 'stripe':
		bpy.ops.mesh.primitive_plane_add(radius=1)

		bpy.ops.object.editmode_toggle()		
		bpy.ops.transform.resize(contextView3D, value=(0.5, size/2, 1), constraint_axis=(True, True, False), constraint_orientation='GLOBAL')
		bpy.ops.transform.resize(contextView3D, value=(scale, scale, 1), constraint_axis=(True, True, False), constraint_orientation='GLOBAL')
		bpy.ops.transform.translate(contextView3D, value=(0, (-size/2)*scale, 0), constraint_axis=(False, True, False))

		bpy.ops.object.editmode_toggle()

		AddArray("Array0", 1,0, size)

	if bpy.context.object:
		bpy.context.object.name = "pattern_{}".format(mode)
	# 	bpy.context.object.show_wire = True



def AddArray(name, offset_x, offset_y, count):
	modifier = bpy.context.object.modifiers.new(name=name, type='ARRAY')
	modifier.relative_offset_displace[0] = offset_x
	modifier.relative_offset_displace[1] = offset_y
	modifier.count = count
	modifier.show_expanded = False
	return modifier



