import bpy
import bmesh
import operator

selection_mode = '';
selection_loops = []
selection_vertices = set()
selection_pivot = '';