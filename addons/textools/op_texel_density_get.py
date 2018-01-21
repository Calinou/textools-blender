import bpy
import bmesh
import operator
import math



# if "bpy" in locals() and utilities_texel:
# 	import imp
# 	imp.reload(utilities_texel)
# else:
from . import utilities_texel




class op(bpy.types.Operator):
	bl_idname = "uv.textools_texel_density_get"
	bl_label = "Get Texel size"
	bl_description = "Get Pixel per unit ratio or Texel density"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		if not bpy.context.active_object:
			return False
		
		if len(bpy.context.selected_objects) == 0:
			return False

		if bpy.context.active_object.type != 'MESH':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		return True

	def execute(self, context):
		get_texel_density(
			self, 
			context
		)
		return {'FINISHED'}



def get_texel_density(self, context):
	print("Get texel density")


	object_face_indexies = {}
	object_edit_mode = bpy.context.object.mode == 'EDIT'

	if bpy.context.object.mode == 'EDIT':
		# Only selected Mesh faces
		obj = bpy.context.active_object
		if obj.type == 'MESH' and obj.data.uv_layers:
			bm = bmesh.from_edit_mesh(obj.data)
			object_face_indexies[obj] = [face.index for face in bm.faces if face.select]
	else:
		# Selected objects with all faces each
		selected_objects = [obj for obj in bpy.context.selected_objects]
		for obj in selected_objects:
			if obj.type == 'MESH' and obj.data.uv_layers:
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.scene.objects.active = obj
				obj.select = True
				bpy.ops.object.mode_set(mode='EDIT')

				bm = bmesh.from_edit_mesh(obj.data)
				object_face_indexies[obj] = [face.index for face in bm.faces]

	# Warning: No valid input objects
	if len(object_face_indexies) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No valid meshes or UV maps" )
		return

	# Collect Images / textures
	object_images = {}
	for obj in object_face_indexies:
		image = utilities_texel.get_object_texture_image(obj)
		if image:
			object_images[obj] = image

	# Warning: No valid images
	if len(object_images) == 0:
		self.report({'ERROR_INVALID_INPUT'}, "No Texture found. Assign Checker map or texture." )
		return


	sum_area_vt = 0
	sum_area_uv = 0

	# Get area for each triangle in view and UV
	for obj in object_face_indexies:
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.scene.objects.active = obj
		obj.select = True

		# Find image of object
		image = object_images[obj]
		if image:
			bpy.ops.object.mode_set(mode='EDIT')
			bm = bmesh.from_edit_mesh(obj.data)
			uvLayer = bm.loops.layers.uv.verify()

			bm.faces.ensure_lookup_table()
			for index in object_face_indexies[obj]:
				face = bm.faces[index]

				# Triangle Verts
				triangle_uv = [loop[uvLayer].uv for loop in face.loops ]
				triangle_vt = [vert.co for vert in face.verts]

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

			

	# Restore selection
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	for obj in object_face_indexies:
		obj.select = True
	bpy.context.scene.objects.active = list(object_face_indexies.keys())[0]
	if object_edit_mode:
		bpy.ops.object.mode_set(mode='EDIT')


	print("Sum verts area {}".format(sum_area_vt))
	print("Sum texture area {}".format(sum_area_uv))

	if sum_area_uv == 0 or sum_area_vt == 0:
		bpy.context.scene.texToolsSettings.texel_density = 0
	else:
		bpy.context.scene.texToolsSettings.texel_density = sum_area_uv / sum_area_vt