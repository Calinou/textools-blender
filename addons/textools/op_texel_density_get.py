import bpy
import bmesh
import operator
import math

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


	sum_area_vt = 0
	sum_area_uv = 0

	# Get area for each triangle in view and UV
	for obj in objects:
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True

		# Find image of object
		image = utilities_texel.get_object_texture_image(obj)
		if image:

			# Create triangulated copy
			bpy.ops.object.duplicate()
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.context.tool_settings.mesh_select_mode = (False, False, True)
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

			bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
			uvLayer = bm.loops.layers.uv.verify()

			for face in bm.faces:
				# Triangle Verts
				triangle_uv = [loop[uvLayer].uv for loop in face.loops ]
				triangle_vt = [vert.co for vert in face.verts]

				#Triangle Areas
				face_area_vt = utilities_texel.get_area_triangle(triangle_vt[0], triangle_vt[1], triangle_vt[2] )
				face_area_uv = utilities_texel.get_area_triangle(triangle_uv[0], triangle_uv[1], triangle_uv[2] )
				
				sum_area_vt+= math.sqrt( face_area_vt )
				sum_area_uv+= math.sqrt( face_area_uv ) * min(image.size[0], image.size[1])

			# Delete Copy
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.delete()

	# Restore selection
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:
		obj.select = True
	bpy.context.scene.objects.active = objects[0]

	print("Sum verts area {}".format(sum_area_vt))
	print("Sum texture area {}".format(sum_area_uv))

	# bpy.context.scene.texToolsSettings.texel_density = math.sqrt( sum_area_uv) / math.sqrt( sum_area_vt)
	bpy.context.scene.texToolsSettings.texel_density = sum_area_uv / sum_area_vt


