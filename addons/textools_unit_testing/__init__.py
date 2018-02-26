import bpy
import os
import mathutils

bl_info = {
 "name": "TexTools Unit Testing",
 "description": "Automated testing for TexTools tools",
 "author": "renderhjs",
 "blender": (2, 7, 5),
 "version": (1, 0, 0),
 "category": "Testing",
 "location": "Viewport > Tool shelf"
}

class TT_Test:
	name = ""
	blend = ""
	def __init__(self, name, blend="", call=None):
		self.name = name


# Test Categories
tests_size = []
tests_layout = []
tests_mesh = []
tests_baking = []
tests_color = []

groups = {
	'0_size':tests_size, 
	'1_layout':tests_layout, 
	'2_mesh':tests_mesh, 
	'3_baking':tests_baking, 
	'4_color':tests_color
}


def test_op_uv_crop():
	print("Testing")

tests_size.append( TT_Test('size_dropdown', call=test_op_uv_crop))
tests_size.append( TT_Test('op_uv_size_get', call=test_op_uv_crop))
tests_size.append( TT_Test('op_uv_crop', call=test_op_uv_crop))
tests_size.append( TT_Test('op_uv_resize', call=test_op_uv_crop))
tests_size.append( TT_Test('op_texture_reload_all', call=test_op_uv_crop))
tests_size.append( TT_Test('uv_channel', call=test_op_uv_crop))
tests_size.append( TT_Test('op_uv_channel_add', call=test_op_uv_crop))
tests_size.append( TT_Test('op_uv_channel_swap', call=test_op_uv_crop))

tests_layout.append( TT_Test('op_island_align_edge', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_rectify', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_island_rotate_90', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_align', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_island_align_sort', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_unwrap_faces_iron', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_unwrap_peel_edge', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_select_islands_identical', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_select_islands_overlap', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_select_islands_outline', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_select_islands_flipped', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_textools_texel_checker_map', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_texel_density_get', call=test_op_uv_crop))
tests_layout.append( TT_Test('op_texel_density_set', call=test_op_uv_crop))

tests_baking.append( TT_Test('op_bake mode:ao', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:cavity', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:curvature', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:diffuse', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:displacment', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:dust', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:id_element', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:id_material', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:normal_object', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:normal_tangent', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:position', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake mode:selection', call=test_op_uv_crop))

tests_baking.append( TT_Test('bake_sampling', call=test_op_uv_crop))
tests_baking.append( TT_Test('bake_force_single', call=test_op_uv_crop))
tests_baking.append( TT_Test('bake_force_single', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_select_bake_type', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake_organize_names', call=test_op_uv_crop))
tests_baking.append( TT_Test('op_bake_explode', call=test_op_uv_crop))



class op_run(bpy.types.Operator):
	bl_idname = "textools.testing_run"
	bl_label = "Choose Directory"

	def execute(self, context):
		print("Export Compressed")
		export_selection(context, True)
		return {'FINISHED'}


class op_run_all(bpy.types.Operator):
	bl_idname = "textools.testing_runall"
	bl_label = "Choose Directory"

	def execute(self, context):
		print ("Export Normal")
		export_selection(context, False)
		return {'FINISHED'}



class texTools_panel_testing(bpy.types.Panel):

	bl_idname = "textools_testing"
	bl_label = "TexTools Testing"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):

		layout = self.layout
		
		count = len( [test for group in groups.values() for test in group] )
		layout.operator(op_run_all.bl_idname, text="Run all {}x tests".format(count), icon='PLAY')
		layout.separator()

		for key in groups:
			row = layout.row(align=True)
			row.label(text="{} {}x".format(key[2:], len(groups[key])))
			row.operator(op_run_all.bl_idname, text="Run {}x".format(len(groups[key])), icon='PLAY')
			box = layout.box()
			
			col = box.column(align=True)
			for test in groups[key]:
				row = col.row(align=True)
				
				# row.separator()
				row.operator(op_run.bl_idname, text="", icon='RADIO')
				row.label(test.name)



		



def export_FBX(path):

	print("Export: " + path)

	# Export
	bpy.ops.export_scene.fbx(
		filepath=path + ".fbx", 
		use_selection=True, 
		
		axis_forward='-Z', 
		axis_up='Y', 
		
		global_scale =0.01, 
		use_mesh_modifiers=True, 
		mesh_smooth_type='OFF', 
		batch_mode='OFF', 
		use_custom_props=True)



# registers
def register():
	bpy.utils.register_class(texTools_panel_testing)
	bpy.utils.register_class(op_run)
	bpy.utils.register_class(op_run_all)
	


def unregister():
	bpy.utils.unregister_class(texTools_panel_testing)
	bpy.utils.unregister_class(op_run_all)
	bpy.utils.unregister_class(op_run)
	

if __name__ == "__main__":
	register()
