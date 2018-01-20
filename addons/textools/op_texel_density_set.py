import bpy
import bmesh
import operator
import math
from mathutils import Vector
from collections import defaultdict


from . import utilities_texel
from . import utilities_uv

class op(bpy.types.Operator):
	bl_idname = "uv.textools_texel_density_set"
	bl_label = "Set Texel size"
	bl_description = "Apply texel density by scaling the UV's to match the ratio"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):

		if not bpy.context.active_object:
			return False
		
		if len(bpy.context.selected_objects) == 0:
			return False
		
		if bpy.context.active_object.type != 'MESH':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True

	
	def execute(self, context):
		set_texel_density(
			self, 
			context,
			bpy.context.scene.texToolsSettings.texel_mode_scale,
			bpy.context.scene.texToolsSettings.texel_density
		)
		return {'FINISHED'}



def set_texel_density(self, context, mode, density):

	print("Set texel density!")

	# Force Object mode
	if bpy.context.object.mode == 'EDIT':
		bpy.ops.object.mode_set(mode='OBJECT')

	# Collect valid Objects
	objects = []
	for obj in bpy.context.selected_objects:
		if obj.type == 'MESH' and obj.data.uv_layers:
			objects.append(obj)

	if len(objects) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No valid objects with UV maps selected" )
		return

	# Process each object
	for obj in objects:
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.scene.objects.active = obj
		obj.select = True

		

		# Find image of object
		image = utilities_texel.get_object_texture_image(obj)
		if image:
			print("Process {} @{}".format(obj.name, density))
			bpy.ops.object.mode_set(mode='EDIT')

			# Store selection
			utilities_uv.selection_store()

			bpy.ops.mesh.select_all(action='SELECT')



			bm = bmesh.from_edit_mesh(obj.data);
			uvLayer = bm.loops.layers.uv.verify();

			# Collect groups of faces to scale together
			groups_faces = []
			if mode == 'ALL':
				# Scale all UV's together
				groups_faces = [bm.faces]

			elif mode == 'ISLAND':
				# Scale each UV idland centered
				bpy.ops.uv.select_all(action='SELECT')
				groups_faces = utilities_uv.getSelectionIslands()


			print("groups: {}x".format(len(groups_faces)))


			for group in groups_faces:
				# Get triangle areas
				sum_area_vt = 0
				sum_area_uv = 0
				for face in group:
					# Triangle Verts
					triangle_uv = [loop[uvLayer].uv for loop in face.loops ]
					triangle_vt = [obj.matrix_world * vert.co for vert in face.verts]

					#Triangle Areas
					face_area_vt = utilities_texel.get_area_triangle(
						triangle_vt[0], 
						triangle_vt[1], 
						triangle_vt[2] 
					)
					face_area_uv = utilities_texel.get_area_triangle_uv(
						triangle_uv[0], 
						triangle_uv[1], 
						triangle_uv[2],
						image.size[0],
						image.size[1]
					)
					
					sum_area_vt+= math.sqrt( face_area_vt )
					sum_area_uv+= math.sqrt( face_area_uv ) * min(image.size[0], image.size[1])

				# Apply scale to group
				scale = density / (sum_area_uv / sum_area_vt)

				# print("Scale: D: {:.2f} D: {:.2f} = scale: {:.2f}".format(density, (sum_area_uv / sum_area_vt), scale))

				# Set Scale Origin to Island or top left
				if mode == 'ALL':
					bpy.context.space_data.pivot_point = 'CURSOR'
					bpy.ops.uv.cursor_set(location=(0, 1))

				elif mode == 'ISLAND':
					bpy.context.space_data.pivot_point = 'MEDIAN'

				# Select Face loops and scale
				bpy.ops.uv.select_all(action='DESELECT')
				bpy.context.scene.tool_settings.uv_select_mode = 'VERTEX'
				for face in group:
					for loop in face.loops:
						loop[uvLayer].select = True
				bpy.ops.transform.resize(value=(scale, scale, 1), proportional='DISABLED')

			# Restore selection
			utilities_uv.selection_restore()

	# Restore selection
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:
		obj.select = True
	bpy.context.scene.objects.active = objects[0]