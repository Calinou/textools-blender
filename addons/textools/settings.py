import bpy
import bmesh
import operator

selection_mode = '';
selection_loops = []
selection_pivot = '';

bake_mode = 'UNDEFINED'