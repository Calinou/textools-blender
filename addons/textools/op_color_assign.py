import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi

from . import utilities_color

class op(bpy.types.Operator):
	bl_idname = "uv.textools_color_assign"
	bl_label = "Assign Color"
	bl_description = "..."
	bl_options = {'REGISTER', 'UNDO'}
	
	index = bpy.props.IntProperty(description="Color Index", default=0)

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		if bpy.context.active_object not in bpy.context.selected_objects:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		return True
	
	def execute(self, context):
		assign_color(self, context, self.index)
		return {'FINISHED'}



def assign_color(self, context, index):
	obj = bpy.context.active_object
	


	previous_mode = bpy.context.active_object.mode
	# uvLayer = bm.loops.layers.uv.verify();

	print("...")
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data);
	faces = []


	

	#Assign to all or just selected faces?
	if bpy.context.active_object.mode == 'EDIT':
		faces = [face for face in bm.faces if face.select]
	else:
		faces = [face for face in bm.faces]		

	if previous_mode == 'OBJECT':
		bpy.ops.mesh.select_all(action='SELECT')
	

	name_material = utilities_color.get_material_name(index)


	# Verify console slots
	for i in range(index+1):
		if index >= len(obj.material_slots):
			bpy.ops.object.material_slot_add()

	# Assign material to slot
	if index < len(obj.material_slots):
		slot = obj.material_slots[index]
		if not slot.material or slot.material.name != name_material:
			print("Assign material")
			slot.material = utilities_color.get_material(index)
		
		# Verify color
		slot.material.diffuse_color = utilities_color.get_color(index)

		# Assign to selection
		bpy.context.object.active_material_index = index
		bpy.ops.object.material_slot_assign()


	#Change View mode to TEXTURED
	for area in bpy.context.screen.areas:
		if area.type == 'VIEW_3D':
			for space in area.spaces:
				if space.type == 'VIEW_3D':
					space.viewport_shade = 'MATERIAL'

	bpy.ops.object.mode_set(mode=previous_mode)


		# for slot in obj.material_slots:
		# 	if not slot.material or slot.material.name != name_material:
		# 		slot.material = utilities_color.get_material(index)
		# 		# Replace
		# 		print("  Slot: {}".format(slot.material.name))






		# Search in material & texture slots
		# for slot_mat in obj.material_slots:
		# 	# Check for traditional texture slots in material
		# 	for slot_tex in slot_mat.material.texture_slots:
		# 		if slot_tex and slot_tex.texture and hasattr(slot_tex.texture , 'image'):
		# 			return slot_tex.texture.image
			
		# 	# Check if material uses Nodes
		# 	if slot_mat.material:
		# 		if hasattr(slot_mat.material , 'node_tree'):
		# 			if slot_mat.material.node_tree:
		# 				for node in slot_mat.material.node_tree.nodes:
		# 					if type(node) is bpy.types.ShaderNodeTexImage:
		# 						if node.image:
		# 							return node.image



def get_material(index):
	print("...")