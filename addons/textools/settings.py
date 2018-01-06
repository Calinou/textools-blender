import bpy
import bmesh
import operator

selection_uv_mode = '';
selection_uv_loops = []
selection_uv_pivot = '';

selection_mode = [False, False, True];
selection_vert_indexies = []
selection_face_indexies = []

bake_mode = 'UNDEFINED'
bake_render_engine = ''
bake_sets = []
