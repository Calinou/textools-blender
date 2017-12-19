import bpy
import bmesh
import operator

selection_uv_mode = '';
selection_uv_loops = []
selection_uv_pivot = '';

selection_mode = [False, False, True];
selection_verts = []

bake_mode = 'UNDEFINED'