import bpy
import os
import bmesh
import math
import operator
from mathutils import Vector
from collections import defaultdict

from . import utilities_uv



class op(bpy.types.Operator):
	bl_idname = "uv.textools_island_symmetry"
	bl_label = "Symmetry"
	bl_description = "Mirrors selected faces to other half or averages based on selected edge center"

	@classmethod
	def poll(cls, context):

		if not bpy.context.active_object:
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False

		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False


		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False


		if bpy.context.scene.tool_settings.uv_select_mode != 'EDGE' and bpy.context.scene.tool_settings.uv_select_mode != 'FACE':
		 	return False

		# if bpy.context.scene.tool_settings.use_uv_select_sync:
		# 	return False

		return True

	def execute(self, context):
		main(context)
		return {'FINISHED'}



def main(context):
	print("--------------------------- Executing operator_symmetry")

	#Store selection
	utilities_uv.selectionStore()

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()

	if bpy.context.scene.tool_settings.uv_select_mode == 'EDGE':


		# 1.) Collect left and right side verts
		verts_middle = [];

		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop[uvLayer].select and loop.vert not in verts_middle:
						verts_middle.append(loop.vert)
					
		# 2.) Align UV shell
		alignToCenterLine()

		# Convert to Vert selection and extend edge loop in 3D space
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
		bpy.ops.mesh.select_all(action='DESELECT')
		for vert in verts_middle:
			vert.select = True

		bpy.ops.mesh.select_mode(use_extend=True, use_expand=False, type='EDGE')
		bpy.ops.mesh.loop_multi_select(ring=False)
		for vert in bm.verts:
			if vert.select and vert not in verts_middle:
				print("Append extra vert to symmetry line from xyz edge loop")
				verts_middle.append(vert)

		# Select UV shell Again
		bpy.ops.mesh.select_linked(delimit={'UV'})
		verts_island = []
		for vert in bm.verts:
			if vert.select:
				verts_island.append(vert)


		# 3.) Restore UV vert selection
		x_middle = 0
		bpy.ops.uv.select_all(action='DESELECT')
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop.vert in verts_middle:
						loop[uvLayer].select = True
						x_middle = loop[uvLayer].uv.x;


		print("Middle "+str(len(verts_middle))+"x, x pos: "+str(x_middle))

		# Extend selection
		bpy.ops.uv.select_more()
		verts_A = [];
		verts_B = [];
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop[uvLayer].select and loop.vert not in verts_middle:
						if loop[uvLayer].uv.x <= x_middle:
							# Left
							if loop.vert not in verts_A:
								verts_A.append(loop.vert)

						elif loop[uvLayer].uv.x > x_middle:
							# Right
							if loop.vert not in verts_B:
								verts_B.append(loop.vert)

		

		
		def remove_doubles():
			verts_double = [vert for vert in verts_island if (vert in verts_A and vert in verts_B)]

			# print("Temp  double: "+str(len(verts_double))+"x")
			if len(verts_double) > 0:
				print("TODO: Remove doubles "+str(len(verts_double)))
				for vert in verts_double:
					verts_A.remove(vert)
					verts_B.remove(vert)
					verts_middle.append(vert)

		def extend_half_selection(verts_middle, verts_half, verts_other):
			# Select initial half selection
			bpy.ops.uv.select_all(action='DESELECT')
			for face in bm.faces:
				if face.select:
					for loop in face.loops:
						if loop.vert in verts_half:
							loop[uvLayer].select = True

			# Extend selection				
			bpy.ops.uv.select_more()

			# count_added = 0
			for face in bm.faces:
				if face.select:
					for loop in face.loops:
						if loop.vert not in verts_half and loop.vert not in verts_middle and loop[uvLayer].select:
							verts_half.append(loop.vert)


		remove_doubles()

		# Limit iteration loops
		max_loops_extend = 200
		for i in range(0, max_loops_extend):
			print("Now extend selection A / B")
			count_hash = str(len(verts_A))+"_"+str(len(verts_B));
			extend_half_selection(verts_middle, verts_A, verts_B)
			extend_half_selection(verts_middle, verts_B, verts_A)
			remove_doubles()

			count_hash_new = str(len(verts_A))+"_"+str(len(verts_B));
			if count_hash_new == count_hash:
				print("Break loop, same as previous loop")
				break;

		print("Edge, Sides: L:"+str(len(verts_A))+" | R:"+str(len(verts_B)))

		# 4.) Mirror Verts
		mirror_verts(verts_middle, verts_A, verts_B, False)


	if bpy.context.scene.tool_settings.uv_select_mode == 'FACE':

		# 1.) Get selected UV faces to vert faces
		selected_faces = []
		for face in bm.faces:
			if face.select:
				# Are all UV faces selected?
				countSelected = 0
				for loop in face.loops:
					if loop[uvLayer].select:
						countSelected+=1
						# print("Vert selected "+str(face.index))
				if countSelected == len(face.loops):
					selected_faces.append(face)


		# if bpy.context.scene.tool_settings.use_uv_select_sync == False:

		bpy.ops.uv.select_linked(extend=False)
		verts_all = []
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if(loop.vert not in verts_all):
						verts_all.append(loop.vert)

		print("Verts shell: "+str(len(verts_all)))


		bpy.ops.mesh.select_all(action='DESELECT')
		for face in selected_faces:
			face.select = True


		# 2.) Select Vert shell's outer edges
		bpy.ops.mesh.select_linked(delimit=set())
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
		bpy.ops.mesh.region_to_loop()
		edges_outer_shell = [e for e in bm.edges if e.select]

		# 3.) Select Half's outer edges
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		bpy.ops.mesh.select_all(action='DESELECT')
		for face in selected_faces:
			face.select = True
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
		bpy.ops.mesh.region_to_loop()
		edges_outer_selected = [e for e in bm.edges if e.select]

		# 4.) Mask edges exclusive to edges_outer_selected (symmetry line)
		edges_middle = [item for item in edges_outer_selected if item not in edges_outer_shell]

		# 5.) Convert to UV selection
		verts_middle = []
		for edge in edges_middle:
			if edge.verts[0] not in verts_middle:
				verts_middle.append(edge.verts[0])
			if edge.verts[1] not in verts_middle:
				verts_middle.append(edge.verts[1])

		#Select all Vert shell faces
		bpy.ops.mesh.select_linked(delimit=set())
		#Select UV matching vert array
		bpy.ops.uv.select_all(action='DESELECT')
		for face in bm.faces:
			if face.select:
				for loop in face.loops:
					if loop.vert in verts_middle:
						loop[uvLayer].select = True

		# 5.) Align UV shell
		alignToCenterLine()

		# 7.) Collect left and right side verts
		verts_A = [];
		verts_B = [];

		bpy.ops.uv.select_all(action='DESELECT')
		for face in selected_faces:
			for loop in face.loops:
				if loop.vert not in verts_middle and loop.vert not in verts_A:
					verts_A.append(loop.vert)

		for vert in verts_all:
			if vert not in verts_middle and vert not in verts_A and vert not in verts_B:
				verts_B.append(vert)

		# 8.) Mirror Verts
		mirror_verts(verts_middle, verts_A, verts_B, True)

	#Restore selection
	utilities_uv.selectionRestore()





def mirror_verts(verts_middle, verts_A, verts_B, isAToB):

	print("____________________\nMirror: C:"+str(len(verts_middle))+" ; verts: "+str(len(verts_A))+"|"+str(len(verts_B))+"x, 	A to B? "+str(isAToB))


	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()


	# Get verts_island
	verts_island = []
	for vert in verts_middle:
		verts_island.append(vert)
	for vert in verts_A:
		verts_island.append(vert)
	for vert in verts_B:
		verts_island.append(vert)

	# Select Island as Faces
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
	bpy.ops.mesh.select_all(action='DESELECT')
	for vert in verts_island:
		vert.select = True
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=True, type='FACE')

	# Collect Librarys of verts / UV
	verts_to_uv = {}
	uv_to_vert = {}
	uv_to_face = {}
	for face in bm.faces:
		if face.select:
			for loop in face.loops:
				uv = loop[uvLayer]
				
				if loop.vert not in verts_to_uv:
					verts_to_uv[loop.vert] = [uv];
				else:
					verts_to_uv[loop.vert].append(uv)

				if uv not in uv_to_vert:
					uv_to_vert[ uv ] = loop.vert;
				if uv not in uv_to_face:
					uv_to_face[ uv ] = face;

	# Get Center X
	x_middle = verts_to_uv[ verts_middle[0] ][0].uv.x;
	

	# 3.) Grow layer by layer
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

	verts_processed = []

	def select_extend_filter(verts_border, verts_mask):
		# print("Extend A/B")
		connected_verts = []
		for i in range(0, len(verts_border)):
			 # Collect connected edge verts
			verts_connected_edges = []
			for edge in verts_border[i].link_edges:
				if(edge.verts[0] not in verts_connected_edges):
					verts_connected_edges.append(edge.verts[0])
				if(edge.verts[1] not in verts_connected_edges):
					verts_connected_edges.append(edge.verts[1])

			# Select vert on border
			bpy.ops.mesh.select_all(action='DESELECT')
			verts_border[i].select = True
			

			# Extend selection
			bpy.ops.mesh.select_more()

			# Filter selected verts against mask, connected edges, processed and border
			verts_extended = [vert for vert in bm.verts if (vert.select and vert in verts_connected_edges and vert in verts_mask and vert and vert not in verts_border and vert not in verts_processed)]
			

			# print("    "+str(i)+". scan: "+str(verts_border[i].index)+"; ext: "+str(len(verts_extended))+"x")

			connected_verts.append( [] )

			# Sort by distance
			verts_distance = {}
			for vert in verts_extended:
				verts_distance[vert] = (verts_border[i].co - vert.co).length

			for item in sorted(verts_distance.items(), key=operator.itemgetter(1)):
				connected_verts[i].append( item[0] )

			if verts_border[i] not in verts_processed:
				verts_processed.append(verts_border[i])

		return connected_verts

	# find UV vert blobs , see which ones are same spot
	def collect_uv_groups(uvs):
		groups = []
		for uv in uvs:
			if len(groups) == 0:
				groups.append([uv])
			else:
				isMerged = False
				for group in groups:
					d = (uv.uv - group[0].uv).length
					if d <= 0.0000001:
						#Merge
						group.append(uv)
						isMerged = True;
						break;
				if not isMerged:
					#New Group
					groups.append([uv])
		return groups

	
	border_A = [vert for vert in verts_middle]
	border_B = [vert for vert in verts_middle]
	

	for i in range(0, 200):

		if len(border_A) == 0:
			print("Finished scanning at {} growth iterations".format(i))
			break;
		if len(border_A) != len(border_B) or len(border_A) == 0:
			print("Abort: non compatible border A/B: {}x {}x ".format(len(border_A), len(border_B)))
			break;

		connected_A = select_extend_filter(border_A, verts_A)
		connected_B = select_extend_filter(border_B, verts_B)

		print("Map pairs: {}|{}".format(len(connected_A), len(connected_B)))

		border_A.clear()
		border_B.clear()

		count = min(len(connected_A), len(connected_B))
		# count = 1 #Temp override
		for j in range(0, count):
			if len(connected_A[j]) != len(connected_B[j]):
				# print("Error: Inconsistent grow mappings from {}:{}x | {}:{}x".format(border_A[j].index,len(connected_A[j]), border_B[j].index, len(connected_B[j]) ))
				print("Error: Inconsistent grow mappings from {}  {}x | {}x".format(j, len(connected_A[j]), len(connected_B[j]) ))
				continue

			for k in range(0, len(connected_A[j])):
				# Vertex A and B
				vA = connected_A[j][k];
				vB = connected_B[j][k];

				uvsA = verts_to_uv[vA];
				uvsB = verts_to_uv[vB];

				uv_groups_A = collect_uv_groups(uvsA)
				uv_groups_B = collect_uv_groups(uvsB)

				if len(uv_groups_A) != len(uv_groups_B):
					print("Error: Inconsistent vertex UV group pairs at vertex {} : {}".format(vA.index, vB.index))
					continue

				print("    Map {0} -> {1}  = UVs {2}|{3}x | UV-Groups {4}|{5}x".format( vA.index, vB.index, len(uvsA), len(uvsB), len(uv_groups_A), len(uv_groups_B) ))

				if len(uv_groups_A) > 0:
					# For each group
					sortA = {}
					sortB = {}
					for g in range(0, len(uv_groups_A)):
						uv_A = uv_groups_A[g][0].uv.copy()
						uv_B = uv_groups_B[g][0].uv.copy()

						# localize X values (from symmetry line)
						uv_A.x = (uv_A.x - x_middle)
						uv_B.x = (uv_B.x - x_middle)

						sortA[g] = abs(uv_A.x) + uv_A.y*2.0
						sortB[g] = abs(uv_B.x) + uv_B.y*2.0
						# print("    .   [{}] : {:.2f}, {:.2f} | {:.2f}, {:.2f}".format(g, uv_A.x, uv_A.y, uv_B.x, uv_B.y))
						print("    .   [{}] : {:.2f} | {:.2f}".format(g, sortA[g], sortB[g]))

					# Sort sortA by value
					sortedA = sorted(sortA.items(), key=operator.itemgetter(1))
					sortedB = sorted(sortB.items(), key=operator.itemgetter(1))
					
					print("Sorted: '"+str(sortedA)+"'")
					print("Sorted: '"+str(sortedB)+"'")

					# for item in sorted(verts_distance.items(), key=operator.itemgetter(1)):
					# 	connected_verts[i].append( item[0] )

					# TODO: Now map groups to each other
					# uv_avg_A = Vector([0,0])
					# uv_avg_B = Vector([0,0])
					# for m in range(0, len(uv_groups_A)):
					# 	print("        . ")
					# 	uv_avg_A+= uv_groups_A[m][0].uv;
					# 	uv_avg_B+= uv_groups_B[m][0].uv;

					# uv_avg_A/=len(uv_groups_A)
					# uv_avg_B/=len(uv_groups_B)

					# print("        avg: {} : {}".format(uv_avg_A, uv_avg_B))
			
				# Done processing, add to border arrays
				border_A.append(vA)
				border_B.append(vB)

	

def alignToCenterLine():
	print("align to center line")

	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uvLayer = bm.loops.layers.uv.verify()
	bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

	# 1.) Get average edges rotation + center
	average_angle = 0
	average_center = Vector((0,0))
	average_count = 0
	for face in bm.faces:
		if face.select:
			verts = []
			for loop in face.loops:
				if loop[uvLayer].select:
					verts.append(loop[uvLayer].uv)

			if len(verts) == 2:
				diff = verts[1] - verts[0]
				angle = math.atan2(diff.y, diff.x)%(math.pi)
				average_center += verts[0] + diff/2
				average_angle += angle
				average_count+=1

	if average_count >0:
		average_angle/=average_count
		average_center/=average_count

	average_angle-= math.pi/2 #Rotate -90 degrees so aligned horizontally

	# 2.) Rotate UV Shell around edge
	bpy.context.space_data.pivot_point = 'CURSOR'
	bpy.ops.uv.cursor_set(location=average_center)

	bpy.ops.uv.select_linked(extend=False)
	bpy.ops.transform.rotate(value=average_angle, axis=(0, 0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED')



